# subset-b-009659 Research

Grouped research for the requested libsmb2 sources. Each section preserves the exact source path for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes128ccm.c -->
# sources/user-network-fs/libsmb2/lib/aes128ccm.c

Purpose: Implements in-place AES-128 CCM authenticated encryption/decryption for SMB3 encryption/signing-related code paths. It builds the CCM authentication block stream from a caller-provided key, nonce, AAD, payload, and MAC buffer.

Important APIs/functions: `aes128ccm_encrypt` computes authentication tag `m`, masks it with counter block S0, then XOR-encrypts payload `p` in place. `aes128ccm_decrypt` decrypts payload in place first, recomputes the tag over plaintext, masks it, and returns `memcmp(tmp, m, mlen)`. Internal helpers include `aes_ccm_generate_b0`, `ccm_generate_T`, `ccm_generate_s`, `aes_ccm_crypt`, and `bxory`.

Control flow: Authentication starts with B0 flags containing AAD presence, tag length encoding, nonce length encoding, and 32-bit payload length. AAD is encoded with a 16-bit length prefix and CBC-MACed block by block. Payload blocks are CBC-MACed next. Counter-mode encryption uses generated S blocks with counter values starting at 1; S0 masks/unmasks the tag.

State/persistence: No global state. The payload and tag buffers are mutated in place. Stack buffers hold transient AES blocks. The API assumes `key`, `nonce`, `aad`, `p`, and `m` are valid for the supplied lengths.

Dependencies/integration: Includes `portable-endian.h`, `compat.h`, and `aes.h`; all block encryption goes through `AES128_ECB_encrypt`, which dispatches to Apple CommonCrypto or the reference implementation via `aes.c`. Tests reference it directly in `tests/aes128ccm-test.c`.

Risks: CCM parameter validation is minimal: nonce length, tag length, AAD length encoding, and payload length are trusted. The implementation stores payload length as 32-bit at bytes 12..15, so it is effectively limited to that CCM L=4 shape. `memcmp` is not constant-time, which can matter if authentication timing is observable. Decrypt mutates payload before authentication succeeds, so callers must discard plaintext on nonzero return.

Test signals: Run AES-CCM vectors in `tests/aes128ccm-test.c`, including encrypt/decrypt round trips and authentication failure. Boundary tests should cover empty AAD, empty payload, partial final blocks, bad tag, invalid nonce/tag lengths, and oversized lengths rejected at a higher layer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes128ccm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes128ccm.h -->
# sources/user-network-fs/libsmb2/lib/aes128ccm.h

Purpose: Declares the small public/internal AES-128 CCM interface used by libsmb2 C files.

Important APIs/types/functions: `aes128ccm_encrypt` and `aes128ccm_decrypt` take raw byte pointers for key, nonce, additional authenticated data, payload, MAC, and their lengths. The encrypt function has no return value; decrypt returns the result of comparing the calculated tag to the supplied tag.

Control flow: The header contains declarations only; callers are responsible for sequencing encryption/decryption and checking decrypt return values.

State/persistence: No types or state are declared. The underlying implementation mutates payload and tag buffers, which is not visible from the header comments.

Dependencies/integration: The header relies on `size_t` being declared before inclusion; it does not include `<stddef.h>`. It is included by `tests/aes128ccm-test.c` and expected to pair with `aes128ccm.c`.

Risks: Lack of include guard and missing `stddef.h` make it fragile when included in multiple or minimal translation units. The API does not document in-place mutation, accepted nonce/tag sizes, or that decrypt returns zero on success and nonzero on failure.

Test signals: Compile smoke tests should include this header alone after `<stddef.h>`, and negative compile tests or static analysis should flag duplicate inclusion if the header is expanded in generated amalgamations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes128ccm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes_apple.c -->
# sources/user-network-fs/libsmb2/lib/aes_apple.c

Purpose: Provides the Apple-specific AES-128 ECB block encrypt backend using CommonCrypto, compiled only when `__APPLE__` is defined.

Important APIs/functions: `AES128_ECB_encrypt_apple(const uint8_t *input, const uint8_t *key, uint8_t *output)` creates a CommonCrypto `CCCryptorRef` with `kCCEncrypt`, `kCCAlgorithmAES`, and `kCCOptionECBMode`, encrypts exactly one 16-byte block via `CCCryptorUpdate`, then releases the cryptor.

Control flow: The file includes its own header, enters the Apple-only block, creates a cryptor, returns silently on `CCCryptorCreate` failure, performs one update, and releases the cryptor. It does not finalize because it handles exactly one ECB block.

State/persistence: No persistent state. The cryptor is per call. Output is caller-owned and may remain unchanged if cryptor creation fails or update fails.

Dependencies/integration: Integrated through `aes.c`, which calls `AES128_ECB_encrypt_apple` on Apple and `AES128_ECB_encrypt_reference` elsewhere. Used transitively by AES-CCM and SMB2 signing code that call `AES128_ECB_encrypt`.

Risks: The source file has an unusual `AES_APPLE_H_` guard around the implementation; it does not break normal compilation but is stylistically misleading. Errors from `CCCryptorUpdate` and `dataOutMoved` are ignored. Silent failure can produce bad signatures/MACs without an immediate error path.

Test signals: Apple CI should compare this backend against reference AES vectors and AES-CCM vectors. Fault-injection or wrapper tests should verify that failure to create/update a cryptor is detectable at higher MAC verification layers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes_apple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes_apple.h -->
# sources/user-network-fs/libsmb2/lib/aes_apple.h

Purpose: Declares the Apple CommonCrypto AES-128 ECB encrypt backend when building on Apple platforms.

Important APIs/types/functions: Under `__APPLE__`, exports `AES128_ECB_encrypt_apple(const uint8_t *input, const uint8_t *key, uint8_t *output)`. It includes `config.h` and `<stdint.h>` when available.

Control flow: Preprocessor-only header with an include guard. Non-Apple builds see no function declaration.

State/persistence: No state or allocation behavior is exposed.

Dependencies/integration: Included by `aes.c` and `aes_apple.c`; `aes.c` selects this backend before falling back to the reference implementation. CommonCrypto itself is included only by the C file.

Risks: The function returns `void`, so backend errors cannot be propagated. The prototype is only present on Apple, which is intentional but means generic code should call `AES128_ECB_encrypt`, not this backend directly.

Test signals: Build matrix should include Apple and non-Apple compilation to ensure conditional declaration paths stay valid. AES known-answer tests should execute through the top-level `AES128_ECB_encrypt` dispatcher.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes_apple.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes_reference.c -->
# sources/user-network-fs/libsmb2/lib/aes_reference.c

Purpose: Provides a tiny-AES-derived portable AES-128 implementation for ECB by default and CBC when `CBC` is enabled before including `aes_reference.h`.

Important APIs/functions: `AES128_ECB_encrypt_reference` and `AES128_ECB_decrypt_reference` operate on one 16-byte block. Optional `AES128_CBC_encrypt_buffer_reference` and `AES128_CBC_decrypt_buffer_reference` process buffers with zero padding. Internal core consists of S-box tables, `smb2_KeyExpansion`, `smb2_Cipher`, `smb2_InvCipher`, row/column transforms, and block copy/XOR helpers.

Control flow: Public ECB functions copy input to output, expand the 128-bit key into 176 round-key bytes, then run AES rounds. CBC encrypt XORs each input block with the IV/previous ciphertext before encryption and pads the final partial block with zeros; decrypt reverses the block transform and XORs with IV/previous ciphertext.

State/persistence: No global mutable state. Tables are static const. Round keys live on the stack. CBC mutates the IV pointer locally and writes to caller-provided output.

Dependencies/integration: Included in build files and selected by `aes.c` on non-Apple systems. `smb2-signing.c` defines `CBC 1` before including the header to enable CBC declarations for CMAC-related code; AES-CCM uses the ECB dispatcher.

Risks: This is not constant-time and uses table lookups, so it is not hardened against side-channel attacks. CBC zero padding is not a general authenticated padding scheme. Optional compile-time macros can change exported symbols; build coverage must exercise the intended macro combinations. There is no runtime error reporting.

Test signals: Validate ECB against NIST SP 800-38A vectors documented in the file, CBC round trips with partial blocks, and cross-backend equality with Apple CommonCrypto. Run AES-CCM and SMB2 signing tests because they transitively depend on this implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes_reference.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes_reference.h -->
# sources/user-network-fs/libsmb2/lib/aes_reference.h

Purpose: Configures and declares the portable reference AES-128 backend.

Important APIs/types/functions: Defaults `CBC` to 0 and `ECB` to 1 if not provided. Declares ECB encrypt/decrypt functions when `ECB` is enabled and CBC buffer encrypt/decrypt functions when `CBC` is enabled.

Control flow: Header behavior is controlled entirely by preprocessor macros, allowing a translation unit such as `smb2-signing.c` to enable CBC before inclusion.

State/persistence: No state. Exposes raw block/buffer APIs that require caller-managed buffers, IVs, and padding expectations.

Dependencies/integration: Included by `aes_reference.c`, `aes.c`, and code that needs optional CBC prototypes. Uses `config.h` and `<stdint.h>` conditionally.

Risks: Macro-controlled declarations can diverge between translation units if `CBC`/`ECB` settings differ unexpectedly. The trailing guard comment says `_AES_H_`, which is inaccurate but harmless. APIs return `void`, so misuse is only observable through downstream cryptographic mismatches.

Test signals: Compile with default macros and with `CBC=1`; run ECB/CBC known-answer tests and any consumers that call the top-level `AES128_ECB_encrypt` dispatcher.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes_reference.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/alloc.c -->
# sources/user-network-fs/libsmb2/lib/alloc.c

Purpose: Implements libsmb2's simple hierarchical allocation context, letting decoded compound objects own child allocations and be freed with one call.

Important APIs/functions: `smb2_alloc_init` allocates a zeroed root block with a hidden `smb2_alloc_header`. `smb2_alloc_data` allocates a zeroed child block with hidden `smb2_alloc_entry`, links it into the root header, and returns the child payload. `smb2_free_data` frees all linked children then the root. `container_of` is used to recover hidden headers, with an MSVC fallback.

Control flow: The caller receives only `buf` pointers. Child allocations prepend each new entry to `hdr->mem`. Free walks the singly linked list and frees entries before freeing the header.

State/persistence: Allocation ownership persists through the hidden root header. There is no global state and no locking; contexts are caller-thread-owned.

Dependencies/integration: Used throughout decode paths, including DCE/RPC payload trees and SMB2 query-info data structures. Errors are reported with `smb2_set_error` when child allocation fails.

Risks: `memctx` passed to `smb2_alloc_data` must be a root pointer from `smb2_alloc_init`; passing child pointers or external memory corrupts ownership assumptions. Individual child frees are unsupported. Size arithmetic adds header offsets without overflow checks. The unused `smb2` parameter in `smb2_alloc_init` is only for API symmetry.

Test signals: Unit tests should allocate root/children, verify zero initialization and tree freeing, exercise allocation failure paths, and run with ASan/UBSan. Decode tests that call `dcerpc_free_data` or `smb2_free_data` are good integration coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/asn1-ber.c -->
# sources/user-network-fs/libsmb2/lib/asn1-ber.c

Purpose: Implements BER/ASN.1 parsing and encoding primitives for simple scalar, OID, byte, and string values.

Important APIs/functions: Byte cursors are handled by `asn1ber_next_byte` and `asn1ber_out_byte`. Parse helpers include `asn1ber_length_from_ber`, `ber_typecode_from_ber`, `ber_typelen_from_ber`, integer decoders, OID decoder, and byte/string decoders. Encode helpers include `asn1ber_ber_from_length`, `asn1ber_ber_from_typelen`, integer encoders, OID encoder, byte/string encoders, length reservation, and `asn1ber_annotate_length`.

Control flow: Decoders consume from `actx->src` using `src_tail` and update output values after type/length validation. Encoders append to `actx->dst` via `dst_head`, optionally reserve length bytes, emit content, then back-annotate actual length with `memmove` if fewer length bytes were needed.

State/persistence: State is held in `struct asn1ber_context`: source cursor, destination cursor, buffer sizes, and `last_error`. No global state. Cursor advances are permanent on partial parse failures.

Dependencies/integration: Depends on errno constants and `asn1-ber.h` tags/context definitions. It is a standalone helper for BER consumers in libsmb2; callers must initialize context fields.

Risks: Bounds checks are present at byte I/O boundaries, but APIs trust non-NULL output pointers in several paths. `asn1ber_ber_from_uint64` initializes `bytesneeded` to 4 while examining 64-bit values, which can under-encode large unsigned 64-bit values. Integer length decoders handle only short one-byte length forms for int values, while generic length decoding supports long form. OID length validation compares BER byte length to element capacity, which is conservative but not an exact element-count limit. `strcat(str, tmp)` in other code is not here; byte/string decoder zero-terminates only if spare room exists.

Test signals: Fuzz BER decoders with malformed length/type/value combinations, test cursor positions after failure, test long-form lengths, signed integer sign extension, OID base-128 continuation, back-annotated lengths, and 64-bit unsigned values above 32 bits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/asn1-ber.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/asn1-ber.h -->
# sources/user-network-fs/libsmb2/lib/asn1-ber.h

Purpose: Defines BER tag constants, context structures, OID storage, and function prototypes for ASN.1 BER encoding/decoding.

Important APIs/types/functions: `ber_type_t` enumerates universal and application-specific BER tags. `struct asn1ber_context` carries input/output buffers and cursor offsets. `struct asn1ber_oid_value` stores up to `BER_MAX_OID_ELEMENTS` 32-bit OID components. Macros `ASN1_SEQUENCE`, `ASN1_CONTEXT`, and `ASN1_CONTEXT_SIMPLE` construct tag bytes.

Control flow: Header-only declarations; callers allocate and initialize contexts, then call parse/encode functions in protocol order.

State/persistence: Exposes cursor state fields directly, making the API lightweight but requiring callers to preserve invariants (`src_tail <= src_count`, `dst_head <= dst_size`).

Dependencies/integration: C/C++ compatible via `extern "C"`. Uses `config.h` and `<stdint.h>` conditionally. Function names map one-to-one with `asn1-ber.c`.

Risks: Directly exposed context fields make misuse easy. `src_count`, `src_tail`, `dst_size`, and `dst_head` are `int`, while lengths passed to APIs are often `uint32_t`, so caller-side conversions matter for large buffers. The license URL typo in the comment is nonfunctional.

Test signals: Compile from C and C++; include header with minimal prerequisites; unit-test each prototype against `asn1-ber.c` and verify OID boundary behavior at `BER_MAX_OID_ELEMENTS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/asn1-ber.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/compat.c -->
# sources/user-network-fs/libsmb2/lib/compat.c

Purpose: Provides platform fallback implementations for functions and socket helpers missing on console, embedded, Windows/Xbox, Amiga, Android, and other non-POSIX targets.

Important APIs/functions: Conditional implementations include `smb2_getaddrinfo`, `smb2_freeaddrinfo`, `random`, `srandom`, `getpid`, `getlogin_r`, `writev`, `readv`, `poll`, `strdup`, `be64toh`, and platform-specific helpers like PS2 `iop_connect`.

Control flow: Almost every function is compiled only when a `NEED_*` or platform macro is defined. Fallback `getaddrinfo` builds a minimal IPv4 `addrinfo`; vectored I/O implementations flatten/scatter buffers through a temporary allocation; fallback `poll` maps requested events onto `select`.

State/persistence: Mostly stateless, except PS2 IOP pseudo-random state `next` and some platform-global errno substitutions. Allocated `addrinfo` and temporary buffers are owned/freed by callers or the function itself.

Dependencies/integration: Paired with `compat.h`, which maps system calls and typedefs per platform. Core libsmb2 networking and file I/O include this layer to build on unusual targets.

Risks: Some fallbacks are deliberately minimal: `smb2_getaddrinfo` lacks full DNS/service/family behavior on many targets, `writev`/`readv` allocate one contiguous buffer and can fail for large vectors, PS2 `asprintf` uses a fixed 256-byte buffer and suspicious `sprintf(str, fmt, args)` varargs handling, and fallback `poll` approximates errors as `POLLHUP`. `be64toh` takes signed `long long` and uses `ntohl` on shifted pieces, so type assumptions matter.

Test signals: Platform build smoke tests are essential. Host-side tests can force `NEED_READV`, `NEED_WRITEV`, `NEED_POLL`, and `NEED_STRDUP` to validate overflow checks, short reads, event mapping, and allocation failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/compat.h -->
# sources/user-network-fs/libsmb2/lib/compat.h

Purpose: Centralizes portability typedefs, macros, includes, errno aliases, socket abstractions, missing POSIX declarations, and platform-specific replacements.

Important APIs/types/functions: Defines `t_socket`, `SMB2_VALID_SOCKET`, `SMB2_INVALID_SOCKET`, substitute `struct addrinfo`, `struct pollfd`, `struct sockaddr_storage`, `struct iovec`, declarations for fallback `poll`, `writev`, `readv`, `getaddrinfo`, `freeaddrinfo`, `getlogin_r`, `random`, `srandom`, and platform-specific remaps such as `close`, `connect`, `read`, `write`, and Nintendo/Amiga network wrappers.

Control flow: Preprocessor branches select definitions for Windows/Xbox, Pico, Dreamcast, Amiga, PS2, PS3, BSDs, Linux, Apple, Vita, Nintendo platforms, ESP, and Android. The final section supplies missing `O_*`, `ENOMEM`, `EINVAL`, and `typeof` definitions.

State/persistence: No runtime state, but it mutates the compilation environment heavily through macros. Some macros replace standard functions globally after inclusion.

Dependencies/integration: Included by nearly every libsmb2 C file. It must be ordered carefully with system headers because it defines replacement structures and function-like macros.

Risks: Macro substitution can surprise downstream code, especially `strncpy(a,b,c) strcpy(a,b)` on Amiga, `close`, `read`, `write`, and network symbol remaps. Struct definitions may diverge from platform ABI if native headers are partially present. Windows include ordering around winsock headers is fragile. Global `typeof` definition assumes GCC-compatible `__typeof__` where absent.

Test signals: Multi-platform compile matrix is the main signal. Static analysis should inspect macro pollution, duplicate type definitions, and include-order regressions. Runtime smoke tests should cover socket open/connect/read/write/poll on each supported target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/dcerpc-lsa.c -->
# sources/user-network-fs/libsmb2/lib/dcerpc-lsa.c

Purpose: Implements NDR coders for the LSA RPC interface used to open policy handles, resolve SIDs, and close handles over the shared DCE/RPC transport.

Important APIs/functions: Exports `lsa_interface`, `NT_SID_AUTHORITY`, and coders such as `lsa_RPC_SID_coder`, `lsa_RPC_UNICODE_STRING_coder`, `lsa_Close_req_coder`, `lsa_Close_rep_coder`, `lsa_OpenPolicy2_req_coder`, `lsa_OpenPolicy2_rep_coder`, `lsa_LookupSids2_req_coder`, and `lsa_LookupSids2_rep_coder`. Internal coders handle SID arrays, translated names, object attributes, trust/domain lists, and referenced domain lists.

Control flow: Request coders serialize handles, SID buffers, lookup parameters, and object attributes through core NDR primitives. Response coders allocate payload-owned arrays when decoding counts from the wire, then decode nested unique/reference pointers and status values. `OpenPolicy2` encodes an empty object-attributes structure; `LookupSids2` encodes lookup options and client revision constants.

State/persistence: No global mutable state beyond exported interface/SID authority data. Decoded allocations are attached to the DCE/RPC PDU payload memory context and must be released with `dcerpc_free_data`.

Dependencies/integration: Depends on public LSA type definitions in `libsmb2-dcerpc-lsa.h` and generic coders in `dcerpc.c`. Examples in `examples/smb2-lsa-lookupsids.c` exercise connect to `lsarpc`, open policy, lookup SIDs, and close.

Risks: Wire-provided counts drive allocations and loops with limited range enforcement in this file, despite comments showing IDL ranges. Some count variables are `uint64_t` but loop indices are `int`, so very large values can misbehave if not rejected by lower layers. Unicode string length computation uses `strlen * 2` and assumes UTF-8-to-UTF-16 handling in the generic coder.

Test signals: Extend `smb2-dcerpc-coder-test.c` with LSA SID/name/domain list round trips for NDR32/NDR64 and endian variants. Integration tests should run the LSA lookup example against a known SMB server and verify memory cleanup through `dcerpc_free_data`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/dcerpc-lsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/dcerpc-srvsvc.c -->
# sources/user-network-fs/libsmb2/lib/dcerpc-srvsvc.c

Purpose: Implements NDR coders for the SRVSVC RPC interface, mainly share enumeration and share information retrieval.

Important APIs/functions: Exports `srvsvc_interface` and coders for share info levels 0, 1, and 2; share info containers; share enum/get-info unions and structs; `srvsvc_NetrShareEnum_req_coder`, `srvsvc_NetrShareEnum_rep_coder`, `srvsvc_NetrShareGetInfo_req_coder`, and `srvsvc_NetrShareGetInfo_rep_coder`.

Control flow: Request coders serialize server/share names as unique/ref UTF-16 pointers, serialize info levels and preferred maximum length/resume handle. Response coders decode switch-discriminated unions using request state where needed, allocate arrays for decoded share entries, decode nested strings and status codes.

State/persistence: No global mutable state except the interface descriptor. Decoded share structures and strings are payload-owned via `smb2_alloc_data` and are freed with the DCE/RPC payload.

Dependencies/integration: Depends on `libsmb2-dcerpc-srvsvc.h` type definitions and the core `dcerpc_*`/`ndr_*` coders. Examples `smb2-share-enum.c`, `smb2-share-enum-sync.c`, and `smb2-share-info.c` use these coders.

Risks: Only levels 0, 1, and 2 are implemented despite comments listing more IDL levels. Wire-provided `EntriesRead` directly controls allocation size and array loop counts. Some request/response coupling relies on `dcerpc_set_request`/`dcerpc_get_request` so decoding share get-info responses requires the original request pointer to remain valid.

Test signals: Existing `smb2-dcerpc-coder-test.c` covers UTF-16 and SHARE_INFO_1 containers for NDR32/NDR64. Add level 0/2, `NetrShareGetInfo`, unsupported-level behavior, large `EntriesRead`, and example-driven integration tests against a server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/dcerpc-srvsvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/dcerpc.c -->
# sources/user-network-fs/libsmb2/lib/dcerpc.c

Purpose: Implements libsmb2's DCE/RPC-over-SMB named-pipe transport and generic NDR/YAML coding layer used by SRVSVC and LSA clients.

Important APIs/functions: Context/PDU lifecycle: `dcerpc_create_context`, `dcerpc_connect_context_async`, `dcerpc_destroy_context`, `dcerpc_allocate_pdu`, `dcerpc_free_pdu`, `dcerpc_open_async`, `dcerpc_call_async`, `dcerpc_free_data`. NDR primitives include integer coders, `ndr_uint3264_coder`, pointer coders, array/union/struct coders, UTF-16 coders, UUID/context-handle coders, and test hooks `ndr_set_tctx`/`ndr_set_endian`. YAML encode-only helpers provide diagnostic rendering.

Control flow: A connect opens a named pipe with SMB2 create, sends a bind PDU proposing NDR32/NDR64 syntax, parses bind ACK, and selects context id. Calls allocate an NDR request PDU, encode header/request/stub, patch fragment length and allocation hint, send `SMB2_FSCTL_PIPE_TRANSCEIVE`, unfragment multi-fragment responses, decode response header/stub, and return payload-owned decoded data to the callback.

State/persistence: `struct dcerpc_context` stores the SMB context, pipe path, selected syntax, file id, transfer context id, data representation, and monotonically increasing call id. Each PDU tracks direction, encoding, payload memory context, deferred pointers, conformance pass state, request pointer, and YAML indentation state.

Dependencies/integration: Depends on SMB2 raw create/ioctl APIs, endian helpers, UTF-8/UTF-16 helpers, allocation context APIs, and public DCE/RPC headers. Service-specific files plug in request/response coders. Examples use it for SRVSVC and LSA workflows.

Risks: Deferred pointer list has fixed capacity `MAX_DEFERRED_PTR` but `dcerpc_add_deferred_pointer` does not bounds-check. Some decode counts are trusted by service coders. `dcerpc_uint64_coder` encodes `*(uint32_t *)ptr`, likely truncating 64-bit values on encode. `dce_unfragment_ioctl` rewrites response buffers in place and depends on consistent fragment lengths. YAML output uses `strncat`/`snprintf` against the output buffer and is encode-only. Error paths sometimes return `-ENOMEM` for generic encode failure.

Test signals: `tests/smb2-dcerpc-coder-test.c` covers NDR32 LE/BE and NDR64 LE for UTF-16 and share containers. Add tests for pointer overflow, NDR64 64-bit values, fragmented responses, bind rejection cases, YAML rendering, and service examples against real SMB named pipes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/dcerpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/dreamcast/vfs.c -->
# sources/user-network-fs/libsmb2/lib/dreamcast/vfs.c

Purpose: Provides a KallistiOS/Dreamcast VFS handler that mounts an SMB share under `/smb` using libsmb2 synchronous APIs.

Important APIs/functions: Public entry points are `kos_smb_init(const char *url)` and `kos_smb_shutdown(void)`. VFS operations include open/close/read/write/readdir/rename/unlink/stat/mkdir/rmdir/seek64/tell64/readlink/rewinddir/fstat. `smb2_stat_convert` maps `smb2_stat_64` to KOS `struct stat`.

Control flow: Initialization creates an SMB context, parses the URL, connects to the share, logs success, and registers the VFS handler. Each VFS callback takes a global mutex, calls the corresponding libsmb2 operation, logs failures, and returns KOS-compatible values. Shutdown unregisters the handler and disconnects/destroys global SMB resources.

State/persistence: Uses global `cxt`, `smb_url`, and static VFS handler `vh`; all operations serialize on a single static mutex. Each open file/directory gets an allocated `struct smb_fd` wrapping type and handle, with optional embedded `dirent_t` storage for directories.

Dependencies/integration: Depends on KallistiOS headers (`kos.h`, VFS/NMMGR types, mutex macros, `dbglog`) and libsmb2 public synchronous APIs. The handler path is `/smb`.

Risks: `smb_readdir` logs warning on normal end-of-directory because it treats NULL as an error unconditionally. `strncpy` may leave `dirent.name` unterminated when the SMB name length is at least `NAME_MAX - 1`. Initialization failure paths do not always null globals after cleanup. Shutdown assumes init succeeded. The single global connection prevents multiple SMB mounts and serializes all I/O.

Test signals: Dreamcast/KOS integration tests should mount a test share, list directories including EOF, read/write/seek/stat files, handle long names, and call shutdown after failed init paths. Threaded tests should verify mutex serialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/dreamcast/vfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/dreamcast/vfs.h -->
# sources/user-network-fs/libsmb2/lib/dreamcast/vfs.h

Purpose: Declares the Dreamcast/KallistiOS SMB VFS lifecycle API.

Important APIs/functions: `kos_smb_init(const char *url)` initializes libsmb2, connects to an SMB URL, and registers `/smb`; `kos_smb_shutdown(void)` unregisters and tears down the connection.

Control flow: Header only; callers invoke init before VFS use and shutdown when the mount is no longer needed.

State/persistence: The implementation uses global state, but the header does not expose handles, so only one implicit mount/context is supported.

Dependencies/integration: Include guard `__KOS_SMB_VFS_H__`. Intended for Dreamcast/KOS consumers that link `vfs.c` and libsmb2.

Risks: The API has no context handle or idempotency contract, so repeated init/shutdown behavior depends on implementation details. It does not expose error strings beyond the integer return from init.

Test signals: Compile with KOS toolchain; verify callers can include the header from C and that init/shutdown lifecycle tests cover success, parse failure, connect failure, and repeated calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/dreamcast/vfs.h -->
