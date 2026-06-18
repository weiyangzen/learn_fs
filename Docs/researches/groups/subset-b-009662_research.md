# Research Report: subset-b-009662

Grouped research for selected libsmb2 PDU, PS2 integration, SHA, and SMB2 command implementation files. Each section preserves the original source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/pdu.c -->
# sources/user-network-fs/libsmb2/lib/pdu.c

## Purpose

`pdu.c` is the central SMB2 packet lifecycle module. It allocates PDUs, initializes SMB2 headers, encodes and decodes fixed header fields, manages compound chains, selects tree/session IDs, correlates server replies with queued requests, dispatches fixed and variable payload parsing to command-specific files, applies signing/encryption decisions, and times out queued commands.

## Important APIs, Types, And Functions

Key exported helpers are `smb2_allocate_pdu`, `smb2_queue_pdu`, `smb2_free_pdu`, `smb2_add_compound_pdu`, `smb2_get_compound_pdu`, `smb2_decode_header`, integer endian accessors, tree ID helpers, message-id accessors, `smb2_find_pdu`, fixed-size lookup functions, payload dispatcher functions, and `smb2_timeout_pdus`. The file works on `struct smb2_context`, `struct smb2_pdu`, `struct smb2_header`, `struct smb2_io_vectors`, and `struct smb2_iovec`.

## Control Flow

Allocation creates a zeroed PDU, fills protocol magic, command, credit charge/request, tree ID, session ID, seal flag, timeout, and a first output iovec for the SMB2 header. Queueing walks each compound PDU, server-side correlates replies and sets flags, encodes headers, optionally signs each PDU, encrypts the chain, then appends it to the outqueue and updates events. Receive processing is split: `smb2_get_fixed_size` chooses the fixed body length, then fixed and variable dispatchers call command-specific parsers.

## State And Persistence Behavior

There is no disk persistence. Runtime state is in context queues, `message_id`, `async_id`, `credits`, tree-id stack, session ID, current input header, and PDU payload pointers. Timeouts invoke the original callback with `SMB2_STATUS_IO_TIMEOUT` and free the PDU. Compound metadata preserves previous compound message IDs for client receive ordering.

## Dependencies And Integration Points

The module depends on libsmb2 private headers, endian helpers, list macros, signing, and SMB3 sealing. Every `smb2-cmd-*` file plugs into this dispatcher through `smb2_process_*` functions. Socket integration is through `smb2_write_to_socket`, `smb2_change_events`, and `smb2_which_events`.

## Risks And Edge Cases

Tree-id state is global to the context and is mutated while decoding server-side requests, so concurrent or nested use must be serialized. `smb2_queue_pdu` uses `pdu` rather than loop variable `p` in several server-side flag/message-id checks, which is worth testing for compound replies. The endian setters use direct casts for 16/32-bit writes and may be sensitive to unaligned access on strict platforms. Error-response classification treats selected warnings as errors and special-cases `STATUS_MORE_PROCESSING_REQUIRED`.

## Test Signals

Test header encode/decode against captured SMB2 frames, compound `next_command` and related-operation flag updates, client message-id increments for credit charge, server reply correlation including async `STATUS_PENDING`, tree connect reply tree-id handling, unsolicited oplock breaks, signing/encryption hooks, dispatch tables for every command, and timeout removal from both outqueue and waitqueue.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/pdu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/irx_imports.h -->
# sources/user-network-fs/libsmb2/lib/ps2/irx_imports.h

## Purpose

`irx_imports.h` is a PS2 IOP module convenience header. It centralizes IRX import headers needed by the SMB2MAN PS2 build so source files can include one local header for kernel, IO, networking, memory, thread, and semaphore APIs.

## Important APIs, Types, And Functions

The file declares no functions or data. Its public surface is the include guard `IOP_IRX_IMPORTS_H` and inclusions of `<irx.h>`, `<intrman.h>`, `<ioman.h>`, `<ps2ip.h>`, `<sifman.h>`, `<stdio.h>`, `<sysclib.h>`, `<sysmem.h>`, `<thbase.h>`, and `<thsemap.h>`.

## Control Flow

There is no runtime control flow. At compile time, it pulls in PS2SDK import definitions required for IRX linking and module symbol resolution.

## State And Persistence Behavior

No state is stored or persisted. Its only effect is on compilation and module import visibility.

## Dependencies And Integration Points

It depends on PS2SDK headers and is intended for IOP/IRX builds, not host builds. It integrates with PS2-specific libsmb2 files such as `smb2man.c` and `smb2_fio.c` when they need IRX service declarations.

## Risks And Edge Cases

The header can hide accidental dependency creep because including it imports many subsystems at once. It also uses `<ioman.h>` while `smb2_fio.c` uses `iomanX.h`, so API mismatches between IOMAN variants should be watched in PS2 build configurations.

## Test Signals

The useful signal is a PS2SDK IRX build that compiles with strict include paths and no missing import stubs. Also verify the header is not included by non-PS2 targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/irx_imports.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/ps2smb2.h -->
# sources/user-network-fs/libsmb2/lib/ps2/ps2smb2.h

## Purpose

`ps2smb2.h` defines the PS2-facing SMB2MAN devctl command contract and small data structures used to connect and disconnect SMB shares through the `smb:` IOP filesystem device.

## Important APIs, Types, And Functions

The header exports `SMB2_PATH_MAX`, devctl command constants `SMB2_DEVCTL_CONNECT` and `SMB2_DEVCTL_DISCONNECT_ALL`, `SMB2_MAX_NAME_LEN`, and structs `smb2Connect_in_t`, `smb2Connect_out_t`, and `smb2Disconnect_in_t`. Connect input carries a local share name, username, password, and SMB URL. Connect and disconnect outputs/inputs pass raw context pointers.

## Control Flow

There is no executable flow. Runtime flow is provided by `SMB2_devctl` in `smb2_fio.c`, which switches on these command IDs and consumes the structs.

## State And Persistence Behavior

The header defines ABI layout only. Runtime state behind `ctx` pointers is owned by the SMB2MAN driver and libsmb2 contexts; no persistent storage is defined.

## Dependencies And Integration Points

It integrates PS2 EE/IOP callers with the IOP driver. Callers must populate fixed-size character arrays and issue devctl to device `smb:`. `smb2_fio.c` uses `SMB2_MAX_NAME_LEN` for its mounted-share list.

## Risks And Edge Cases

Fixed-size credentials and URL buffers can truncate if callers do not validate lengths before copying. The disconnect-all command is defined but not implemented in the observed `SMB2_devctl`, and `smb2Disconnect_in_t` is not consumed there. Passing raw context pointers across the interface creates lifetime and trust risks.

## Test Signals

Test ABI sizes on the PS2 toolchain, connect calls with maximum field lengths, unsupported devctl handling, and future disconnect command behavior if implemented.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/ps2smb2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/smb2_fio.c -->
# sources/user-network-fs/libsmb2/lib/ps2/smb2_fio.c

## Purpose

`smb2_fio.c` adapts libsmb2 to the PS2 IOP filesystem device interface. It registers an `smb` filesystem driver, maintains a list of connected SMB shares presented as `smb:/<name>/...`, translates IOP file and directory operations into synchronous libsmb2 calls, and exposes a devctl connect operation.

## Important APIs, Types, And Functions

Public driver entry points include `SMB2_initdev`, `SMB2_init`, `SMB2_deinit`, `SMB2_devctl`, `SMB2_open`, `SMB2_close`, `SMB2_read`, `SMB2_write`, `SMB2_lseek`, `SMB2_lseek64`, `SMB2_dopen`, `SMB2_dclose`, `SMB2_dread`, `SMB2_getstat`, `SMB2_mkdir`, `SMB2_rmdir`, `SMB2_remove`, `SMB2_rename`, and `SMB2_chdir`. Internal structures are `smb2_share_list`, `dir_fh`, and `file_fh`.

## Control Flow

`SMB2_initdev` replaces any existing `smb` driver and registers `smb2man_ops`. `SMB2_devctl` locks a global semaphore and handles `SMB2_DEVCTL_CONNECT`, which creates a libsmb2 context, parses the URL, sets password, connects to the share, and prepends it to the global share list. Path operations call `prepare_path`, split the mounted share name with `find_context`, then lock around libsmb2 calls. Directory root entries can enumerate mounted shares; subdirectories use `smb2_opendir` and `smb2_readdir`.

## State And Persistence Behavior

State is process-resident in global `shares`, `smb2_curdir`, optional debug log context/file, and `smb2man_io_sema`. No durable state is written except optional debug logging to an SMB URL when compiled with `DEBUG`. File handles store libsmb2 context/file-handle pairs in `iop_file_t.privdata`.

## Dependencies And Integration Points

The file depends on PS2SDK IOP headers, IOMANX device structures, thread semaphores, `ps2smb2.h`, and public libsmb2 APIs. It is started by `smb2man.c` and exposed to PS2 software through the `smb:` device name.

## Risks And Edge Cases

`find_context` appears to return a share when `strcmp(share->name, path)` is nonzero, which means the first non-matching share is selected rather than the matching one. `SMB2_dopen` marks virtual root handling as TODO but still calls `find_context`, so mounted-share enumeration is hard to reach unless paths split as expected. Connect failure logs call `smb2_get_error(share->smb2)` after destroying the context. The share list and `smb2_curdir` are not fully cleaned up on deinit, connect does not reject duplicate names, and writes exist despite `SMB2_open` refusing non-read-only opens. `calloc` in `smb2man.c` does not check malloc failure before `memset`, which affects this file's allocations.

## Test Signals

PS2-side tests should cover connect, duplicate share names, root directory listing, path normalization for `/./`, `/..`, and backslashes, open/read/close, directory read/stat conversion, rename across shares, semaphore serialization, deinit cleanup, and failures from URL parsing or SMB connection. A focused unit test should expose the `strcmp` polarity in `find_context`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/smb2_fio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/smb2_fio.h -->
# sources/user-network-fs/libsmb2/lib/ps2/smb2_fio.h

## Purpose

`smb2_fio.h` is the narrow public header for the PS2 SMB2 filesystem adapter. It exposes the driver initialization entry used by the IRX module start function.

## Important APIs, Types, And Functions

The only declaration is `int SMB2_initdev(void);`, protected by include guard `__SMB2_FIO_H__`.

## Control Flow

There is no control flow in the header. `smb2man.c` calls `SMB2_initdev()` from `_start`, which then registers the `smb` IOP driver in `smb2_fio.c`.

## State And Persistence Behavior

No state is defined. The global device and share state live in `smb2_fio.c`.

## Dependencies And Integration Points

It is included by `smb2man.c` and implemented by `smb2_fio.c`. Keeping this header small limits the IRX module entry dependency on the rest of the driver internals.

## Risks And Edge Cases

The header gives no visibility into cleanup or devctl APIs, so external callers must know the PS2 device contract from `ps2smb2.h` or IOMAN. If `SMB2_initdev` changes signature, module startup breaks at compile time.

## Test Signals

Build tests should verify `smb2man.c` links against `SMB2_initdev` and that duplicate declarations do not drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/smb2_fio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/smb2man.c -->
# sources/user-network-fs/libsmb2/lib/ps2/smb2man.c

## Purpose

`smb2man.c` is the PS2 IRX module wrapper for SMB2MAN. It declares module identity, starts the filesystem driver, and provides libc-style allocation shims backed by PS2 IOP system memory.

## Important APIs, Types, And Functions

The module defines `IRX_ID(MODNAME, VER_MAJOR, VER_MINOR)`, `_start`, `malloc`, `free`, and `calloc`. `_start` prints the module version and delegates to `SMB2_initdev`. Allocation wrappers call `AllocSysMemory` and `FreeSysMemory` while interrupts are suspended.

## Control Flow

Module load enters `_start`, ignores arguments, prints a banner, and returns the result of driver registration. `malloc` suspends interrupts, allocates with `ALLOC_FIRST`, resumes interrupts, and returns the pointer. `free` mirrors that for deallocation. `calloc` multiplies count and size, allocates, zeroes, and returns.

## State And Persistence Behavior

No persistent state is stored here. Memory allocation affects global IOP heap state. The IRX module remains resident or not according to the return code from `SMB2_initdev`.

## Dependencies And Integration Points

The file depends on PS2SDK kernel, loadcore, sysmem, and C library headers plus `smb2_fio.h`. Its allocation symbols satisfy code in this module build that expects standard C allocators.

## Risks And Edge Cases

`calloc` does not handle multiplication overflow and calls `memset` even if `malloc` returns `NULL`. Interrupt suspension around allocator calls is platform-specific and can increase interrupt latency. `malloc` takes `int size` while `calloc` computes `size_t`, so large allocations can truncate. There is no `realloc` shim.

## Test Signals

PS2 module tests should verify successful IRX load/unload behavior, driver registration result propagation, allocation failure handling, zeroed `calloc` memory for normal sizes, and behavior under low IOP memory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/smb2man.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha-private.h -->
# sources/user-network-fs/libsmb2/lib/sha-private.h

## Purpose

`sha-private.h` provides shared boolean functions used by the bundled RFC 4634 SHA implementations. It keeps the SHA round functions in one place for SHA-1, SHA-256, and SHA-512 variants.

## Important APIs, Types, And Functions

It defines macros `SHA_Ch`, `SHA_Maj`, and `SHA_Parity`. `SHA_Ch` and `SHA_Maj` have standard FIPS forms by default and alternative equivalent forms when `USE_MODIFIED_MACROS` is defined.

## Control Flow

There is no runtime control flow. The macros are expanded inside compression loops in `sha1.c`, `sha224-256.c`, and the non-32-bit path of `sha384-512.c`. The 32-bit-only SHA-512 path undefines and redefines compatible macro names with output parameters.

## State And Persistence Behavior

No state is stored. Macro choice is compile-time only.

## Dependencies And Integration Points

The header is included after `sha.h` by each SHA implementation. It assumes inputs are integer words of the width expected by the including file.

## Risks And Edge Cases

Macro arguments are evaluated multiple times in the default forms, so callers must pass side-effect-free expressions. Any future change must preserve bit-exact FIPS behavior across 32-bit and 64-bit implementations.

## Test Signals

Known-answer tests for SHA-1, SHA-256, SHA-384, and SHA-512 should be run with and without `USE_MODIFIED_MACROS` to validate equivalence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha.h -->
# sources/user-network-fs/libsmb2/lib/sha.h

## Purpose

`sha.h` declares the bundled SHA and HMAC API used by libsmb2 cryptographic code. It is an RFC 4634-style interface covering SHA-256 and SHA-512 by default, optional SHA-1/SHA-224, optional SHA-384/SHA-512, a unified SHA selector, and HMAC state.

## Important APIs, Types, And Functions

The header defines return codes `shaSuccess`, `shaNull`, `shaInputTooLong`, `shaStateError`, and `shaBadParam`; hash/block sizes; `SHAversion`; contexts `SHA1Context`, `SHA256Context`, `SHA512Context`, aliases `SHA224Context` and `SHA384Context`, `USHAContext`, and `HMACContext`. It declares reset/input/final-bits/result functions for enabled algorithms, `USHA*` helpers, and `hmac*` helpers.

## Control Flow

The header is compile-time feature-gated by `USE_SHA1`, `USE_SHA224`, and `USE_SHA384_SHA512`. Consumers choose an algorithm either by calling the direct functions or by passing `SHAversion` to the unified/HMAC APIs.

## State And Persistence Behavior

Hash state is held in caller-owned contexts: intermediate digest words, bit length counters, pending message block, block index, and `Computed`/`Corrupted` flags. There is no persistence. Result calls finalize and mark contexts computed, after which more input is an error.

## Dependencies And Integration Points

It depends on config/stdlib/stdint availability and is implemented by `sha1.c`, `sha224-256.c`, `sha384-512.c`, and separate unified/HMAC implementation files elsewhere in libsmb2. SMB3 signing, preauth integrity, and key derivation code are likely consumers.

## Risks And Edge Cases

Default macros disable SHA-1 and SHA-224 while enabling SHA-384/512, so build configurations must match callers. Context layouts differ under `USE_32BIT_ONLY`. The API supports final partial bits, which is easy to misuse. It does not provide constant-time comparison or automatic context cleansing beyond implementation finalizers clearing message blocks.

## Test Signals

Compile matrix tests should cover feature macro combinations and `USE_32BIT_ONLY`. Runtime tests need NIST known-answer vectors, incremental input in varied chunk sizes, final-bit inputs, post-result input errors, null argument errors, and HMAC vectors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha1.c -->
# sources/user-network-fs/libsmb2/lib/sha1.c

## Purpose

`sha1.c` implements SHA-1 from RFC 4634 when `USE_SHA1` is enabled. It provides reset, input, final partial-bit, and result APIs over `SHA1Context`.

## Important APIs, Types, And Functions

Public functions are `SHA1Reset`, `SHA1Input`, `SHA1FinalBits`, and `SHA1Result`. Internal helpers are `SHA1Finalize`, `SHA1PadMessage`, and `SHA1ProcessMessageBlock`. Macros include `SHA1_ROTL` and `SHA1AddLength`.

## Control Flow

`SHA1Reset` seeds the five initial hash words and clears counters. `SHA1Input` appends bytes to a 64-byte block, increments the 64-bit bit count, and processes a block when full. `SHA1FinalBits` validates a 1-to-7-bit suffix, updates length, and finalizes with the proper marker bit. `SHA1Result` finalizes if needed and writes big-endian digest bytes. The compression function expands 16 input words to 80 and runs the four SHA-1 rounds.

## State And Persistence Behavior

All state is caller-owned in `SHA1Context`. Finalization clears the pending message block and length counters and marks `Computed`. `Corrupted` records overflow, null/state errors, or previous failure. No state is persisted.

## Dependencies And Integration Points

It depends on `compat.h`, `sha.h`, and `sha-private.h`. Because `USE_SHA1` defaults to 0 in `sha.h`, this file may compile to no public functions unless enabled by the build.

## Risks And Edge Cases

SHA-1 is cryptographically weak for collision resistance and should not be used for new integrity designs. The byte-at-a-time input loop is simple but slow for large buffers. The length overflow path sets `Corrupted` to integer `1`, not the named `shaInputTooLong`, matching this RFC code but less expressive.

## Test Signals

Use FIPS SHA-1 known-answer vectors, million-`a` input, incremental byte and multi-byte updates, final-bit vectors, length overflow simulation, null input handling, and state-error checks after result/final-bits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha224-256.c -->
# sources/user-network-fs/libsmb2/lib/sha224-256.c

## Purpose

`sha224-256.c` implements SHA-256 and optional SHA-224 from RFC 4634. SHA-224 reuses the SHA-256 context and compression logic with different initial constants and digest truncation.

## Important APIs, Types, And Functions

Always-present public functions are `SHA256Reset`, `SHA256Input`, `SHA256FinalBits`, and `SHA256Result`. When enabled, SHA-224 exposes `SHA224Reset`, `SHA224Input`, `SHA224FinalBits`, and `SHA224Result`. Internal helpers are `SHA224_256Reset`, `SHA224_256Finalize`, `SHA224_256PadMessage`, `SHA224_256ProcessMessageBlock`, and `SHA224_256ResultN`.

## Control Flow

Reset selects initial hash constants. Input appends bytes to 64-byte blocks, updates the 64-bit bit length, and compresses full blocks. Final-bits inserts a partial-byte suffix and marker. Result finalizes if needed and serializes the requested number of digest bytes. Compression builds a 64-word schedule and runs the SHA-256 round function using `Ch`, `Maj`, big sigma, small sigma, and the 64 constants.

## State And Persistence Behavior

State is in `SHA256Context`: intermediate hash words, low/high length counters, pending block, index, and computed/corrupted flags. Finalization clears the message block and length counters. There is no persistence.

## Dependencies And Integration Points

The file depends on `compat.h`, `sha.h`, and `sha-private.h`. SHA-256 is likely used for SMB2/SMB3 cryptographic derivation paths when SHA-512 is not required; SHA-224 is disabled by default.

## Risks And Edge Cases

As with SHA-1, the implementation processes input byte-by-byte. Macro expressions require unsigned 32-bit behavior. `SHA256FinalBits` returns success for zero-length final bits before null-context validation, so callers passing a null context with zero bits get success. Length overflow sets `Corrupted` through the macro.

## Test Signals

Run NIST SHA-256 and SHA-224 known-answer vectors, chunked input equivalence, final-bit vectors, null and post-result error behavior, overflow handling, and optional macro builds for `USE_SHA224`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha224-256.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha384-512.c -->
# sources/user-network-fs/libsmb2/lib/sha384-512.c

## Purpose

`sha384-512.c` implements SHA-384 and SHA-512 from RFC 4634 when `USE_SHA384_SHA512` is enabled. It supports native 64-bit arithmetic and an alternate `USE_32BIT_ONLY` implementation that represents 64-bit words as pairs of 32-bit words.

## Important APIs, Types, And Functions

Public functions are `SHA384Reset`, `SHA384Input`, `SHA384FinalBits`, `SHA384Result`, `SHA512Reset`, `SHA512Input`, `SHA512FinalBits`, and `SHA512Result`. Shared internals include `SHA384_512Reset`, `SHA384_512Finalize`, `SHA384_512PadMessage`, `SHA384_512ProcessMessageBlock`, and `SHA384_512ResultN`. The file defines extensive rotate, shift, add, sigma, `Ch`, and `Maj` macros for both arithmetic modes.

## Control Flow

Reset loads SHA-384 or SHA-512 initial constants and clears a 128-byte block. Input accumulates bytes, updates a 128-bit bit count, and compresses full 1024-bit blocks. Finalization pads with a marker byte, zeroes to leave 16 bytes for length, stores the 128-bit length, processes the final block, clears pending data, and marks computed. Result serializes 48 or 64 digest bytes in big-endian order.

## State And Persistence Behavior

State is caller-owned in `SHA512Context`. Native mode uses two 64-bit length counters and eight 64-bit intermediate words; 32-bit-only mode uses four length words and sixteen intermediate 32-bit halves. Finalization clears message block and length state but not the final digest words. No persistence occurs.

## Dependencies And Integration Points

The file depends on `compat.h`, `sha.h`, and `sha-private.h`. SMB3.1.1 preauth negotiation advertises `SMB2_HASH_SHA_512`, so this implementation is part of the cryptographic baseline for modern SMB dialects.

## Risks And Edge Cases

The 32-bit macro path is complex and easy to regress independently from the native path. Constants use `ll` suffixes, which assume suitable 64-bit literal support. `SHA512FinalBits` has the same zero-length early-success behavior as SHA-256. The implementation is not a hardened side-channel library, and context cleansing is partial.

## Test Signals

Run SHA-384 and SHA-512 known-answer vectors on both native and `USE_32BIT_ONLY` builds, chunked input, final-bit vectors, million-character tests, overflow simulation, result serialization checks, and SMB3.1.1 preauth hash integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha384-512.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-close.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-close.c

## Purpose

`smb2-cmd-close.c` encodes and decodes SMB2 CLOSE requests and replies for both client and server roles. It handles file ID transmission and optional close metadata returned by the server.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_close_async`, `smb2_cmd_close_reply_async`, `smb2_process_close_fixed`, and `smb2_process_close_request_fixed`. Internal encoders are `smb2_encode_close_request` and `smb2_encode_close_reply`. Payload structures are `smb2_close_request` and `smb2_close_reply`.

## Control Flow

Request creation allocates an SMB2_CLOSE PDU, appends the fixed request body, sets struct size, flags, and 16-byte file ID, pads to 64-bit alignment, and returns the queued-ready PDU. Reply encoding writes struct size, flags, timestamps, allocation size, EOF, and attributes. Fixed parsers validate exact struct size and body length, allocate payloads, and copy fields from the current input iovec.

## State And Persistence Behavior

The file does not persist state. It creates transient PDU payloads owned by `pdu.c` cleanup. Remote state changes are significant: close releases a server file handle, and close replies can return final metadata.

## Dependencies And Integration Points

It depends on libsmb2 endian helpers and PDU allocation/free/padding. Higher-level file APIs call this when closing `smb2fh` handles.

## Risks And Edge Cases

There is no variable parser because CLOSE has fixed bodies. Encoders that fail after adding an iovec rely on PDU cleanup for allocated buffers. Tests should verify exact size handling because SMB2 struct sizes include the odd wire-size convention masked by `0xfffe`.

## Test Signals

Test round-trip request/reply encoding, flag propagation, file ID copy, metadata fields, malformed struct sizes, short fixed bodies, and close callback behavior through the full async queue.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-close.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-create.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-create.c

## Purpose

`smb2-cmd-create.c` implements SMB2 CREATE open/create request and reply marshalling. It converts paths to SMB UTF-16 form, handles create contexts as opaque buffers, parses replies with file IDs and metadata, and supports server-side request decoding.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_create_async`, `smb2_cmd_create_reply_async`, `smb2_process_create_fixed`, `smb2_process_create_variable`, `smb2_process_create_request_fixed`, and `smb2_process_create_request_variable`. Internal helpers are request/reply encoders and offset macros `IOV_OFFSET_CREATE` and `IOVREQ_OFFSET_CREATE`.

## Control Flow

Request encoding fills desired access, attributes, share access, disposition, options, name offset/length, and create-context fields. Nonempty names are converted from UTF-8 to UTF-16 and `/` characters are rewritten to `\`. Empty names still add padding so contexts align. Reply encoding writes oplock/flags/action, timestamps, sizes, attributes, file ID, and optional context. Parsing first validates fixed size and offsets, returns the variable byte count, then variable parsing attaches context pointers or converts the request name back to allocated UTF-8.

## State And Persistence Behavior

State is transient in PDU payloads and buffers. Server-visible remote state includes opening or creating filesystem objects, acquiring oplocks/leases through create contexts, and returning durable file IDs. Request variable parsing allocates name memory through `smb2_alloc_init`, tying it to the context allocator.

## Dependencies And Integration Points

The file depends on UTF conversion helpers, iovec management, endian accessors, and create context definitions in libsmb2 headers. It is used by higher-level open, stat, directory, and create-path APIs.

## Risks And Edge Cases

Create contexts are opaque and not validated here. Offset arithmetic assumes sane received lengths; overlap checks exist, but variable parsers rely on the receive layer to have read the requested length. Request variable parsing decodes the name from the start of the variable iovec, which is correct only because the fixed parser requested padding up to `name_offset`. Empty-name padding and alignment are protocol-sensitive. Path conversion rewrites all slash codepoints, which may surprise callers expecting literal slash handling.

## Test Signals

Test UTF-8/UTF-16 conversion, slash rewriting, empty name with contexts, context alignment, offset overlap rejection, malformed lengths, reply file ID and metadata parsing, server-side name allocation lifetime, and full open/create integration against a test SMB server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-echo.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-echo.c

## Purpose

`smb2-cmd-echo.c` implements SMB2 ECHO request and reply marshalling. ECHO is a lightweight keepalive/health command with fixed-size empty bodies.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_echo_async`, `smb2_cmd_echo_reply_async`, `smb2_process_echo_fixed`, and `smb2_process_echo_request_fixed`. Internal helpers encode request and reply fixed bodies.

## Control Flow

Client or server allocates an SMB2_ECHO PDU, appends a fixed body containing only the SMB2 struct size, pads to 64-bit alignment, and queues it through `pdu.c`. Fixed parsers validate struct size and length. Request parsing allocates an empty `smb2_echo_request` payload for server handlers.

## State And Persistence Behavior

No durable state exists. ECHO may refresh connection liveness at higher layers but this file does not update counters or timestamps.

## Dependencies And Integration Points

It depends on the core PDU allocator, iovec helper, and endian setters/getters. It is dispatched by `pdu.c` for command `SMB2_ECHO`.

## Risks And Edge Cases

Because the command carries no variable data, most risk is strict size validation and memory allocation for an otherwise empty request. A malformed peer can trigger errors by sending odd or short fixed bodies.

## Test Signals

Test request and reply encoding bytes, parser acceptance of valid bodies, rejection of wrong struct sizes, callback behavior, and use as a keepalive over an established connection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-echo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-error.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-error.c

## Purpose

`smb2-cmd-error.c` handles SMB2 ERROR response bodies. It is used when `pdu.c` classifies the SMB2 status as an error or selected warning and needs command-independent error payload parsing.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_error_reply_async`, `smb2_process_error_fixed`, and `smb2_process_error_variable`. Internal `smb2_encode_error_reply` writes the fixed error body. The payload type is `smb2_error_reply`.

## Control Flow

Error reply creation allocates a PDU using the causing command, sets `header.status`, encodes struct size, error context count, and byte count, then pads. Fixed parsing validates the error body, allocates payload, reads context count and byte count, and returns the variable byte count. Variable parsing points `error_data` at the variable iovec.

## State And Persistence Behavior

No persistent state is used. Error data pointers reference receive-buffer lifetime owned by the PDU. The header status is the main error state and is set before queueing.

## Dependencies And Integration Points

The module is integrated with `smb2_is_error_response` in `pdu.c`; command-specific parsers are bypassed for error statuses. Server code can create errors for any causing command.

## Risks And Edge Cases

Encoding has a TODO for structured error data, so server-side rich error contexts are not emitted. Variable parsing does not decode context records and exposes raw bytes. Consumers must not use `error_data` after the PDU is freed.

## Test Signals

Test status propagation, byte count variable reads, raw error-data lifetime, malformed fixed sizes, zero-byte errors, and errors attached to each command type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-flush.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-flush.c

## Purpose

`smb2-cmd-flush.c` implements SMB2 FLUSH request and reply bodies, allowing clients to request that server-side cached file data for a file ID be committed.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_flush_async`, `smb2_cmd_flush_reply_async`, `smb2_process_flush_fixed`, and `smb2_process_flush_request_fixed`. Internal helpers encode fixed request and reply bodies. Payload type is `smb2_flush_request`.

## Control Flow

Request encoding writes struct size and file ID into a fixed body. Reply encoding writes only struct size. Parsers validate exact fixed body sizes; request parsing allocates a payload and copies the file ID.

## State And Persistence Behavior

No local persistence exists. The remote side may persist file data as a result of processing FLUSH, but this file only marshals the command.

## Dependencies And Integration Points

It integrates with file handle operations and the core PDU dispatcher. It relies on `SMB2_FD_SIZE` and endian/iovec helpers.

## Risks And Edge Cases

Failure paths after iovec allocation sometimes rely on generic cleanup and sometimes omit a specific error string. The command has no variable area, so malformed size handling is the main parser risk.

## Test Signals

Test file ID round-trip, fixed struct-size validation, successful server flush reply handling, error status routing through `smb2-cmd-error.c`, and full flush behavior against a server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-ioctl.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-ioctl.c

## Purpose

`smb2-cmd-ioctl.c` implements SMB2 IOCTL request and reply marshalling. It supports validate-negotiate-info locally, reparse point decoding on replies, and passthrough mode for control codes the library does not understand.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_ioctl_async`, `smb2_cmd_ioctl_reply_async`, `smb2_process_ioctl_fixed`, `smb2_process_ioctl_variable`, `smb2_process_ioctl_request_fixed`, and `smb2_process_ioctl_request_variable`. Important structures include `smb2_ioctl_request`, `smb2_ioctl_reply`, `smb2_ioctl_validate_negotiate_info`, and `smb2_reparse_data_buffer`.

## Control Flow

Request encoding fills control code, file ID, input offset/count, max response sizes, flags, and appends raw input. Reply encoding writes fixed fields and either transcodes `SMB2_FSCTL_VALIDATE_NEGOTIATE_INFO` or copies output in passthrough mode. Fixed reply parsing validates offsets, reads input/output metadata, and returns enough bytes to include padding, input, and output. Variable parsing decodes reparse data for `GET_REPARSE_POINT` or copies raw output. Server-side request variable parsing decodes validate-negotiate info or exposes raw input in passthrough mode.

## State And Persistence Behavior

State is transient in request/reply payloads and context-allocated output buffers. IOCTL operations can query or mutate remote filesystem/device state depending on the control code; this module itself does not persist anything.

## Dependencies And Integration Points

It depends on core PDU helpers, `smb2_decode_reparse_data_buffer`, passthrough mode on `smb2_context`, and negotiate/security state for validate-negotiate use. It is used by higher-level symlink/reparse and SMB3 validation paths.

## Risks And Edge Cases

Reply encoding allocates `PAD_TO_64BIT(len)` bytes but zeroes `rep->output_count` bytes, which can exceed the allocated length if `len` is reduced for a transcoded output. Raw output copying in `smb2_process_ioctl_variable` copies `iov->len - IOV_OFFSET_IOCTL`, not strictly `output_count`, into a buffer sized `output_count`. Unsupported control codes fail unless passthrough is enabled. Offset validation checks lower bounds but relies on the receive layer and later length checks for upper bounds.

## Test Signals

Test validate-negotiate request/reply encoding, reparse point decoding, passthrough raw input/output, unsupported code errors, offset overlap and overrun rejection, output-count versus padding behavior, and integration with SMB3 negotiate validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-lock.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-lock.c

## Purpose

`smb2-cmd-lock.c` implements SMB2 byte-range lock request and reply marshalling. It supports one inline lock element in the fixed body and additional lock elements in the variable area.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_lock_async`, `smb2_cmd_lock_reply_async`, `smb2_process_lock_fixed`, `smb2_process_lock_request_fixed`, and `smb2_process_lock_request_variable`. Internal helpers include `smb2_encode_lock_request`, `smb2_encode_lock_reply`, and `smb2_parse_locks`. Important types are `smb2_lock_request` and `smb2_lock_element`.

## Control Flow

Request encoding writes lock count, packed sequence number/index, file ID, first lock element, and optional extra elements. Reply encoding writes only struct size. Fixed request parsing validates size, unpacks sequence fields, copies file ID, requires at least one lock, allocates a lock array, parses the inline element, and returns the byte count for remaining locks. Variable parsing parses the remaining elements.

## State And Persistence Behavior

Local state is transient in PDU payloads. Remote state can create, unlock, or fail byte-range locks on the server. Parsed locks are allocated from the libsmb2 context allocator.

## Dependencies And Integration Points

The file depends on PDU helpers, endian accessors, and lock constants from libsmb2 headers. It integrates with file APIs that expose SMB2 locking.

## Risks And Edge Cases

The encoder allocates space for `lock_count` elements in the variable iovec even though the first element is already in the fixed body; it only fills `lock_count - 1`, leaving extra padded space. Fixed parsing constructs a temporary iovec starting at `iov->buf + SMB2_LOCK_ELEMENT_SIZE`; this works because the first lock starts at offset 24 and `SMB2_LOCK_ELEMENT_SIZE` is 24, but it is non-obvious. Large `lock_count` can drive large allocation without an explicit cap.

## Test Signals

Test one-lock and multi-lock requests, sequence packing/unpacking, invalid zero lock count, large lock counts, lock/unlock/shared/exclusive flags, malformed variable lengths, and server-visible byte-range lock behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-logoff.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-logoff.c

## Purpose

`smb2-cmd-logoff.c` implements SMB2 LOGOFF request and reply marshalling. LOGOFF terminates an SMB2 session after tree and file cleanup at higher protocol layers.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_logoff_async`, `smb2_cmd_logoff_reply_async`, `smb2_process_logoff_fixed`, and `smb2_process_logoff_request_fixed`. Internal helpers encode fixed request and reply bodies.

## Control Flow

Request and reply encoding allocate a small fixed body, write the struct size, pad, and return a PDU. Client-side reply fixed processing is a no-op. Server-side request parsing validates the fixed body, allocates an empty `smb2_logoff_request`, and stores it as payload.

## State And Persistence Behavior

The file itself holds no state. Remote/session state changes happen when a server processes LOGOFF; context session cleanup is handled elsewhere.

## Dependencies And Integration Points

It plugs into `pdu.c` dispatch for `SMB2_LOGOFF`. LOGOFF PDUs use tree ID zero in `smb2_allocate_pdu`.

## Risks And Edge Cases

`smb2_process_logoff_request_fixed` compares against `SMB2_ECHO_REQUEST_SIZE` and reports echo sizes/messages rather than `SMB2_LOGOFF_REQUEST_SIZE`; this is probably harmless only if those constants are identical. The allocation error also says echo request. Tests should guard against future constant divergence.

## Test Signals

Test request/reply byte encoding, parser size constants, session-id preservation in headers, tree-id zero handling, and full disconnect/logoff sequences.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-logoff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-negotiate.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-negotiate.c

## Purpose

`smb2-cmd-negotiate.c` implements SMB2 NEGOTIATE request and reply marshalling, including SMB3.1.1 negotiate contexts for preauth integrity and encryption capability.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_negotiate_async`, `smb2_cmd_negotiate_reply_async`, `smb2_process_negotiate_fixed`, `smb2_process_negotiate_variable`, `smb2_process_negotiate_request_fixed`, and `smb2_process_negotiate_request_variable`. Internal helpers encode/parse preauth, encryption, netname, and generic negotiate contexts.

## Control Flow

Request encoding writes fixed negotiate fields, dialect array, client GUID, security mode, capabilities, and, for SMB2 version any/any3/3.1.1, appends preauth SHA-512 and AES-128-CCM encryption contexts. Reply encoding writes server capabilities, sizes, times, security buffer metadata, and optional contexts. Fixed parsing reads security buffer and context offsets, validates overlap and PDU bounds, and returns variable length. Variable parsing attaches the security buffer and parses known SMB3.1.1 contexts.

## State And Persistence Behavior

State is transient in PDU payloads but negotiation establishes durable-in-context protocol state elsewhere: selected dialect, security mode, capabilities, cipher, server GUID, maximum sizes, and preauth hash inputs. The file reads `smb2->salt`, `version`, `dialect`, `spl`, and `passthrough`-adjacent context state but does not write persistent storage.

## Dependencies And Integration Points

It depends on libsmb2 constants, UTF-16 conversion for netname context parsing, SHA-512 advertised hash constants, encryption constants, and PDU/iovec helpers. It is the first SMB2 command in normal client connections and feeds session setup/signing/sealing decisions.

## Risks And Edge Cases

In reply encoding, `seclen` is initialized from `security_buffer_length` but then overwritten with `PAD_TO_64BIT(len)`, so allocation/copy size appears tied to fixed header length rather than security buffer length. Unknown negotiate contexts are fatal for replies and requests except for a few known ignored types, which may reduce forward compatibility. Request context parsing only interprets contexts when dialect list contains 3.1.1. Offset loops check `offset > iov->len` after reading type/length, so truncated context headers need careful receive-layer coverage.

## Test Signals

Test dialect arrays for SMB2.0.2 through SMB3.1.1, negotiate context alignment/counts, preauth salt encoding, encryption cipher parsing, security buffer bounds, unknown context behavior, server request parsing with and without 3.1.1 dialect, and full negotiate/session-setup integration against Samba and Windows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-negotiate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-notify-change.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-notify-change.c

## Purpose

`smb2-cmd-notify-change.c` implements SMB2 CHANGE_NOTIFY request and reply marshalling. It allows clients to ask for directory change notifications and lets servers return raw notification buffers.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_change_notify_async`, `smb2_cmd_change_notify_reply_async`, `smb2_process_change_notify_fixed`, `smb2_process_change_notify_variable`, and `smb2_process_change_notify_request_fixed`. Payloads are `smb2_change_notify_request` and `smb2_change_notify_reply`.

## Control Flow

Request encoding writes flags, output buffer length, file ID, and completion filter. Reply encoding writes output buffer offset/length and, only in passthrough mode, appends caller-provided raw output. Fixed reply parsing validates the fixed body, reads output metadata, and returns the output length. Variable parsing points the output at the variable iovec. Request parsing reads flags, file ID, and completion filter.

## State And Persistence Behavior

No local state persists. On the server, CHANGE_NOTIFY can create a pending asynchronous operation until a directory changes; async correlation is handled by `pdu.c` and higher server logic.

## Dependencies And Integration Points

It depends on libsmb2 PDU helpers and passthrough mode. Notification output structure packing is not implemented except for raw passthrough, so proxy/server users must supply wire-format data.

## Risks And Edge Cases

Reply encoding sets `output_buffer_offset` using `SMB2_CHANGE_NOTIFY_REQUEST_SIZE` instead of the reply fixed size, which should be checked against protocol constants. Structured notification packing is not implemented. Fixed parsing returns `output_buffer_length` without validating the received output offset. Variable output pointer lifetime is tied to the PDU receive buffer.

## Test Signals

Test request filter/flag encoding, output offset/length correctness, zero-output replies, passthrough raw notification buffers, async pending/complete flow, malformed output lengths, and integration with directory watch operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-notify-change.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-oplock-break.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-oplock-break.c

## Purpose

`smb2-cmd-oplock-break.c` implements SMB2 OPLOCK_BREAK and lease-break acknowledgements, replies, and notifications. It handles both classic oplock structures and SMB2 lease structures under the same command.

## Important APIs, Types, And Functions

Public functions include `smb2_cmd_oplock_break_async`, `smb2_cmd_oplock_break_reply_async`, `smb2_cmd_oplock_break_notification_async`, `smb2_cmd_lease_break_async`, `smb2_cmd_lease_break_reply_async`, `smb2_cmd_lease_break_notification_async`, `smb2_process_oplock_break_fixed`, `smb2_process_oplock_break_variable`, `smb2_process_oplock_break_request_fixed`, and `smb2_process_oplock_break_request_variable`. Payloads are union wrappers for oplock and lease break request/reply variants.

## Control Flow

Encoders allocate an OPLOCK_BREAK PDU and choose body size based on oplock acknowledgement/reply/notification or lease acknowledgement/reply/notification. Fixed parsing first reads only the struct size, allocates a generic wrapper, and returns the remaining byte count for that variant. Variable parsing then decodes fields with offsets adjusted because the struct size was consumed as the fixed part. Unsolicited oplock notifications are distinguished by message ID `0xffffffffffffffff`.

## State And Persistence Behavior

Local state is transient in PDU payloads. Protocol state affects client caching guarantees: oplock/lease breaks require clients to downgrade cached access and acknowledge. `pdu.c` has special correlation logic for unsolicited `SMB2_OPLOCK_BREAK` notifications.

## Dependencies And Integration Points

The file depends on PDU helpers and oplock/lease constants. It integrates tightly with open/create lease state and server async notification handling.

## Risks And Edge Cases

Several lease encoders write multiple fields at offset 4 instead of their distinct wire offsets, so encoded lease acknowledgements and notifications appear corrupt. In lease reply variable parsing, the lease key is copied into `rep->lock.lease.lease_key` rather than the `leaserep` member, which may indicate a union/member mistake. Error text contains typos but more importantly fixed parsing trusts the receive layer to provide the exact remaining bytes for each variant.

## Test Signals

Test byte-level encoding for every oplock and lease variant, unsolicited notification correlation, message-id based break type detection, request acknowledgement parsing, lease key and state offsets, malformed struct sizes, and integration with create lease contexts and cache-downgrade callbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-oplock-break.c -->
