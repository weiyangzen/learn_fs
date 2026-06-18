# Research: subset-b-006092

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha512-avx2-asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sha512-avx2-asm.S

## Purpose
Provides the x86-64 AVX2/BMI2 SHA-512 compression transform used by the kernel crypto SHA-512 implementation. Despite the `avx2` filename, the exported symbol is `sha512_transform_rorx`, selected by x86 SHA-512 glue when AVX2, BMI2, and usable YMM state are available.

## APIs, Types, and Functions
The only externally visible API is `SYM_FUNC_START(sha512_transform_rorx)`, with the C ABI `void sha512_transform_rorx(struct sha512_block_state *state, const u8 *data, size_t nblocks)`. It includes `<linux/linkage.h>`, uses the kernel symbol/return macros, and expects a SHA-512 block state of eight 64-bit chaining words. Internal assembly macros include `addm`, `COPY_YMM_AND_BSWAP`, `rotate_Ys`, `RotateState`, `MY_VPALIGNR`, `FOUR_ROUNDS_AND_SCHED`, and `DO_4ROUNDS`. Read-only data sections provide the standard 80-entry `K512` table, a byte-swap shuffle mask, and a YMM lane mask.

## Control Flow
The function saves callee-saved GPRs, aligns a stack frame, converts `nblocks` to an end pointer, and loads the eight chaining variables. For each 128-byte input block, it byte-swaps four YMM chunks into big-endian 64-bit words, then runs the SHA-512 schedule and rounds in groups of four. The first loop expands scheduled words while hashing; the second loop finishes the remaining rounds using already prepared schedule vectors. At block completion it adds the working variables back into the caller's state, advances by one block, and loops until the input pointer reaches the computed end. It finishes with `vzeroupper` before returning.

## State and Persistence
Persistent state is only the caller-owned SHA-512 block state updated in place. The message schedule, round-transfer buffer, saved context pointer, input pointer, and end pointer live on the stack. The constants are immutable rodata. There is no allocation, locking, or global mutable state.

## Dependencies and Integration Points
This file is used through `sha512.h`, which wraps the assembly call in `kernel_fpu_begin()`/`kernel_fpu_end()` and exposes it through a static call selected at module initialization. It depends on AVX2 vector instructions, BMI2 `rorx`, x86-64 calling conventions, YMM state support, and the SHA-512 generic fallback for contexts where FPU use is unsafe.

## Risks and Test Signals
Risks are concentrated in assembly correctness: stack alignment, preserving callee-saved registers, using `vzeroupper`, correct byte order, exact `K512` constants, and correct handling of `nblocks >= 1`. The wrapper must never call it when `irq_fpu_usable()` is false. Test signals include crypto manager SHA-512 vectors, comparison against `sha512_blocks_generic`, KASAN/objtool/unwind checks for the hand-written frame, boot tests on AVX2/BMI2 and non-AVX2 machines, and stress tests from interrupt-heavy or softirq contexts that force fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha512-avx2-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha512-ssse3-asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sha512-ssse3-asm.S

## Purpose
Implements the x86-64 SSSE3 SHA-512 compression transform. It is the lower SIMD tier used when SSSE3 is present but AVX/YMM acceleration is unavailable or not selected.

## APIs, Types, and Functions
The exported assembly symbol is `sha512_transform_ssse3`, with C ABI `void sha512_transform_ssse3(struct sha512_block_state *state, const u8 *data, size_t nblocks)`. The file defines symbolic register aliases for `digest`, `msg`, `msglen`, the eight SHA-512 working variables, and temporary registers. It uses a stack message schedule `W_t`, a two-word `WK_2` transfer area, `SHA512_Round`, `SHA512_2Sched_2Round_sse`, and `RotateState`. Ro data includes `XMM_QWORD_BSWAP` and the standard `K512` table.

## Control Flow
After saving GPRs and aligning the stack, the function loops over message blocks. For each block it loads the digest words, byte-swaps the first sixteen 64-bit message words with `pshufb`, stores them in the stack schedule, and interleaves two scalar SHA-512 rounds with vectorized two-word message-schedule expansion. It runs 80 rounds, adds the resulting working variables back into the digest, advances `msg` by 128 bytes, decrements `msglen`, and repeats until all blocks are processed.

## State and Persistence
The caller's digest state is the only durable mutation. Stack storage holds the 80-word schedule and two-word round-transfer buffer. The static constants are mergeable read-only sections. The function does not allocate memory, take locks, or store process-wide state.

## Dependencies and Integration Points
It depends on SSSE3 `pshufb`, SSE2 integer-vector operations, x86-64 ABI preservation rules, and kernel linkage macros. `sha512.h` declares the symbol, protects the call with kernel FPU save/restore, and switches to this transform through `static_call_update()` when `X86_FEATURE_SSSE3` is the best available acceleration tier.

## Risks and Test Signals
Important risks include incorrect endian shuffling, schedule expansion errors, stack-frame alignment mistakes, missed register restores, and use without a valid FPU context. Tests should compare against generic SHA-512 for single and multi-block inputs, exercise CPU feature selection on SSSE3-only systems, run crypto selftests under preemption and interrupt pressure, and use objtool/build coverage to catch unwinder or frame violations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha512-ssse3-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha512.h -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sha512.h

## Purpose
Provides the x86-specific SHA-512 block-dispatch glue that chooses between generic, SSSE3, AVX, and AVX2/BMI2 transform implementations.

## APIs, Types, and Functions
The header includes `<asm/fpu/api.h>` and `<linux/static_call.h>`, defines `DEFINE_STATIC_CALL(sha512_blocks_x86, sha512_blocks_generic)`, declares each assembly transform through `DEFINE_X86_SHA512_FN`, and defines static wrappers `sha512_blocks_ssse3`, `sha512_blocks_avx`, and `sha512_blocks_avx2`. The public local override is `static void sha512_blocks(...)`, which calls the current static-call target. `sha512_mod_init_arch()` performs feature selection.

## Control Flow
Each generated wrapper checks `irq_fpu_usable()`. If true, it enters a kernel FPU section, calls the selected assembly transform, and exits the FPU section. Otherwise it calls `sha512_blocks_generic`. At architecture initialization, the code prefers AVX2 plus BMI2 when AVX/YMM xfeatures are available, otherwise AVX, otherwise SSSE3, leaving the default generic target if no accelerated feature is supported.

## State and Persistence
The persistent state is the static-call target `sha512_blocks_x86`, updated once during module initialization. Per-call state is the caller's SHA-512 block state. No memory is allocated and no digest state is kept globally.

## Dependencies and Integration Points
This header is included by the SHA-512 implementation's architecture hook path. It depends on CPU feature helpers (`boot_cpu_has`, `cpu_has_xfeatures`), x86 FPU APIs, static calls, the generic SHA-512 block function, and assembly symbols from the companion x86 files.

## Risks and Test Signals
Risks include selecting an AVX/YMM transform when OS xstate support is missing, failing to fall back in IRQ/FPU-unsafe context, or mismatching assembly symbol prototypes. Test signals include crypto selftests across feature matrices, boot logs or ftrace confirming selected static-call targets, forced fallback tests where `irq_fpu_usable()` is false, and module build/link tests covering all configured transform files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha512.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sm3-avx-asm_64.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sm3-avx-asm_64.S

## Purpose
Implements the x86-64 AVX/BMI2 accelerated SM3 compression transform for the kernel crypto SM3 implementation.

## APIs, Types, and Functions
The exported symbol is `sm3_transform_avx`, with C ABI `void sm3_transform_avx(struct sm3_block_state *state, const u8 *data, size_t nblocks)`. The file defines state offsets for eight 32-bit chaining words, all 64 rotated SM3 round constants, register aliases for GPR and XMM state, and a stack layout for expanded words and saved registers. Macros implement rotates, additions, `FF1`/`GG1`, `FF2`/`GG2`, round execution, input byte-swapping, and three-word-at-a-time schedule expansion.

## Control Flow
The transform zeroes upper vector state, saves the frame and callee-saved registers, loads the eight 32-bit chaining variables, and enters a per-block loop. It reads a 64-byte input block, byte-swaps words to host order, computes `W` and `W1 ^ W2` schedule data in XMM registers and stack slots, and unrolls all 64 SM3 rounds. Rounds 0-15 use the XOR-style boolean functions and rounds 16-63 use the majority/choose-style functions. At block end the working variables are XORed into the original state words, `nblocks` is decremented, and the loop repeats. It clears vector registers and restores saved GPRs before returning.

## State and Persistence
The caller-owned `struct sm3_block_state` is updated in place. All schedule and temporary state is local to registers and the stack. The byte-swap mask is read-only data. There is no global mutable state or allocation.

## Dependencies and Integration Points
The assembly depends on AVX, BMI2-style `rorx` helpers, x86-64 ABI conventions, `<asm/frame.h>`, and `<linux/linkage.h>`. `sm3.h` wraps this symbol in FPU protection and selects it with a static call when AVX, BMI2, and YMM xfeatures are available.

## Risks and Test Signals
Risks include round-constant or schedule mistakes, endianness errors, incomplete vector-state cleanup, callee-saved register corruption, and invoking the transform without usable kernel FPU state. Test signals include SM3 known-answer tests, generic-vs-AVX comparisons for multi-block messages, boot tests on AVX/BMI2 and fallback systems, objtool/unwind validation, and stress tests around preemption or interrupt contexts that should trigger generic fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sm3-avx-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sm3.h -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sm3.h

## Purpose
Provides the x86-specific SM3 block-dispatch glue that routes SM3 block processing to the AVX assembly transform when the CPU and kernel FPU state support it.

## APIs, Types, and Functions
The header declares `asmlinkage void sm3_transform_avx(...)`, defines `sm3_blocks_avx()` as the FPU-safe wrapper, declares `DEFINE_STATIC_CALL(sm3_blocks_x86, sm3_blocks_generic)`, defines local `sm3_blocks()` as the static-call dispatch point, and provides `sm3_mod_init_arch()` for feature selection.

## Control Flow
`sm3_blocks_avx()` checks `irq_fpu_usable()`. If usable, it brackets `sm3_transform_avx()` with `kernel_fpu_begin()` and `kernel_fpu_end()`; otherwise it calls `sm3_blocks_generic()`. At init time, the static-call target is updated only when AVX, BMI2, and SSE/YMM xfeatures are all available.

## State and Persistence
The static-call target is the only persistent mutable state. Callers provide and own all SM3 chaining state. No allocations, locks, or permanent buffers are managed here.

## Dependencies and Integration Points
Depends on x86 CPU feature helpers, kernel FPU APIs, static calls, the generic SM3 implementation, and the `sm3_transform_avx` assembly symbol. It integrates with the kernel crypto SM3 module through architecture hook macros.

## Risks and Test Signals
Risks include dispatching AVX code without valid xstate support, failing to fall back in FPU-unsafe contexts, and link failures when assembly support is misconfigured. Test signals are SM3 crypto selftests, feature-selection tests on AVX/BMI2 and non-AVX hosts, forced generic fallback checks, and module builds for configurations with and without the x86 optimized object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sm3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ctype.c -->
# sources/distributed-fs/ceph-client/lib/ctype.c

## Purpose
Defines the kernel's exported `_ctype` classification table used by `linux/ctype.h` character classification macros.

## APIs, Types, and Functions
The file exports `const unsigned char _ctype[256]` with bit flags such as `_C`, `_S`, `_SP`, `_P`, `_D`, `_U`, `_L`, and `_X` assigned to every byte value. `EXPORT_SYMBOL(_ctype)` makes the table available to modules.

## Control Flow
There is no executable control flow. Callers index the table through inline/macros from `<linux/ctype.h>` to implement checks like digit, space, uppercase, lowercase, punctuation, and hexadecimal digit classification.

## State and Persistence
The table is immutable global data. It has no runtime mutation, allocation, or persistence outside the kernel image.

## Dependencies and Integration Points
Depends on `<linux/ctype.h>`, compiler annotations, and export support. It is a low-level dependency for string parsing throughout the kernel, including command-line parsing, sysfs/debugfs input, networking parsers, and filesystem helpers.

## Risks and Test Signals
Risks include ABI-visible flag changes, mismatches between table bits and ctype macros, and non-ASCII assumptions for bytes above 127. Test signals include compile coverage for modules using ctype helpers, unit tests or parser tests for ASCII classification, and regression checks for hex/string parsing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ctype.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/debug_info.c -->
# sources/distributed-fs/ceph-client/lib/debug_info.c

## Purpose
Forces debug information for selected core kernel data structures into the final image when reduced debug information is configured.

## APIs, Types, and Functions
The file intentionally defines no functions or variables. Its API surface is the collection of included headers: credentials, crypto, dcache, device, filesystem, fscache, I/O, kallsyms, kobject, memory-management, module, networking, scheduler, slab, stdarg, core types, IPv6 address configuration, sockets, and TCP.

## Control Flow
There is no runtime control flow. The compiler sees the type declarations from the included headers, allowing debug-info generation to retain their type metadata.

## State and Persistence
No runtime state is created. The lasting effect is build artifact metadata in the kernel image's debug information sections.

## Dependencies and Integration Points
Depends on the headers it includes and on build configurations such as `CONFIG_DEBUG_INFO_REDUCED`. It integrates with debuggers, crash dump analysis, BPF tooling, and postmortem inspection workflows that need type definitions for common kernel structures.

## Risks and Test Signals
Risks are build bloat, accidental addition of executable code contrary to the file's comment, and stale include choices that omit important reduced-debug types. Test signals include debug-info size checks, `pahole`/BTF or debugger visibility for included structures, and build tests under reduced and full debug-info configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/debug_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/debug_locks.c -->
# sources/distributed-fs/ceph-client/lib/debug_locks.c

## Purpose
Provides shared global controls for kernel lock debugging facilities so lockdep and related lock validators can disable noisy follow-on reports after the first detected problem.

## APIs, Types, and Functions
Exports `int debug_locks`, initially enabled, and `int debug_locks_silent`, used by tests to suppress console output. `debug_locks_off()` calls `__debug_locks_off()`, optionally raises console verbosity, and returns whether it performed the first transition to disabled state.

## Control Flow
Callers detect a lock debugging failure and invoke `debug_locks_off()`. If debugging is still enabled and the lower-level atomic off operation succeeds, the function may call `console_verbose()` unless silent mode is set, then returns `1`. Later calls return `0`.

## State and Persistence
`debug_locks` and `debug_locks_silent` are global `__read_mostly` state. Once `debug_locks` is turned off, it remains off for the running kernel unless explicitly reset by test code or reinitialization paths.

## Dependencies and Integration Points
Depends on rwsem, mutex, spinlock, export, and debug-lock headers. It is shared by spinlock, mutex, rwsem, and lockdep debugging code and by the lock test suite.

## Risks and Test Signals
Risks include races in global disable handling, losing first-failure diagnostics if silent mode is misused, and excessive console verbosity if repeated failures are not suppressed. Test signals include lockdep selftests, intentional lock misuse tests, exported-symbol users, and checks that only the first failure toggles the global state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/debug_locks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/debugobjects.c -->
# sources/distributed-fs/ceph-client/lib/debugobjects.c

## Purpose
Implements the kernel generic object lifetime debugger. Subsystems register object addresses and descriptor callbacks so debugobjects can catch invalid init, activate, deactivate, destroy, free, and active-state transitions.

## APIs, Types, and Functions
Core exported APIs are `debug_object_init()`, `debug_object_init_on_stack()`, `debug_object_activate()`, `debug_object_deactivate()`, `debug_object_destroy()`, `debug_object_free()`, `debug_object_assert_init()`, and `debug_object_active_state()`. With `CONFIG_DEBUG_OBJECTS_FREE`, `debug_check_no_obj_freed()` scans address ranges being freed. Boot APIs include `debug_objects_early_init()` and `debug_objects_mem_init()`.

Important internal types are `struct debug_bucket`, `struct pool_stats`, and `struct obj_pool`. The file manages a page-chunk-hashed `obj_hash`, a static boot pool, per-CPU object pools, a global pool, a deferred free pool, a dedicated `debug_objects_cache`, warning/fixup/stat counters, early params `debug_objects` and `no_debug_objects`, and optional debugfs stats.

## Control Flow
Initialization first sets up hash bucket locks and seeds `pool_boot` with static objects. Later `debug_objects_mem_init()` runs an optional selftest, creates the dedicated slab cache, allocates dynamic batches, replaces active static debug objects, adjusts pool thresholds by CPU count, and enables the static key for cache-backed allocation.

Runtime operations hash the target object address by page chunk, lock the bucket, find or allocate a `struct debug_obj`, validate the requested transition, update state when legal, or snapshot the object and print/fix up outside the bucket lock when illegal. Pool management moves objects in fixed batches between per-CPU, global, and free pools. A delayed work item rate-limits freeing surplus objects back to slab. OOM disables debugobjects and drains tracked objects to avoid cascading failures.

## State and Persistence
The subsystem is stateful for the life of the kernel. It persists tracked object records in hash buckets, pool occupancy, per-object `state` and `astate`, global enablement, stats counters, and delayed-work state. It does not persist across reboot. The state machine distinguishes none, initialized, inactive, active, destroyed, and not-available states.

## Dependencies and Integration Points
Depends on CPU hotplug, debugfs, hash lists, kmemleak/slab, scheduler/task-stack helpers, seq_file, static keys, raw spinlocks, delayed work, early params, and descriptor callbacks from object-owning subsystems. It integrates with timers, work items, RCU-like objects, and other facilities that opt into debug object tracking.

## Risks and Test Signals
Risks include false positives from missing annotations, missed reports when OOM disables the subsystem, lock-order problems during pool refill, per-CPU pool accounting bugs, recursion if debug object allocations are themselves debugged, and expensive scans under `CONFIG_DEBUG_OBJECTS_FREE`. Test signals include `CONFIG_DEBUG_OBJECTS_SELFTEST`, debugfs `debug_objects/stats`, lockdep coverage of pool locks, CPU hotplug tests, forced OOM/fallback tests, and subsystem-specific lifetime misuse tests that verify descriptor fixups and warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/debugobjects.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dec_and_lock.c -->
# sources/distributed-fs/ceph-client/lib/dec_and_lock.c

## Purpose
Provides helpers that decrement an atomic reference count and return with a lock held if the decrement reaches zero, making the decrement-to-zero and lock acquisition effectively atomic for object teardown.

## APIs, Types, and Functions
Exports `atomic_dec_and_lock()`, `_atomic_dec_and_lock_irqsave()`, `atomic_dec_and_raw_lock()`, and `_atomic_dec_and_raw_lock_irqsave()`. The APIs accept an `atomic_t *` plus either `spinlock_t *` or `raw_spinlock_t *`; irqsave variants also receive a flags pointer populated when the lock is acquired.

## Control Flow
Each helper first tries `atomic_add_unless(atomic, -1, 1)`. If the counter was not one, the decrement succeeds and the function returns `0` with no lock held. If the counter may drop to zero, it takes the relevant lock, performs `atomic_dec_and_test()`, and returns `1` with the lock held if zero was reached. If another racer changed the count, it unlocks and returns `0`.

## State and Persistence
The only persistent state mutation is the caller's atomic counter. Lock state is returned to the caller only on success; callers must release it. No global state is maintained.

## Dependencies and Integration Points
Depends on Linux atomic and spinlock APIs and is exported for refcounted object teardown paths that need a final-reference lock, such as list removal or shared object destruction.

## Risks and Test Signals
Risks include callers treating it as equivalent to `atomic_dec_and_test()` followed by locking, forgetting to unlock on a `1` return, misusing irqsave flags when the function returns `0`, and underflowing invalid counters. Test signals include refcount teardown race tests, lockdep assertions for returned lock ownership, and stress tests with concurrent put/free operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dec_and_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress.c -->
# sources/distributed-fs/ceph-client/lib/decompress.c

## Purpose
Detects a compressed stream's format from its leading magic bytes and returns the matching kernel decompressor callback.

## APIs, Types, and Functions
Defines `struct compress_format` with two magic bytes, a display name, and a `decompress_fn`. `compressed_formats[]` maps gzip, bzip2, lzma, xz, lzo, lz4, and zstd magic prefixes to configured decompressor functions, or `NULL` when a format is not built. The exported local API is `decompress_method(const unsigned char *inbuf, long len, const char **name)`.

## Control Flow
`decompress_method()` rejects buffers shorter than two bytes, logs the magic bytes at debug level, scans the sentinel-terminated table with `memcmp()`, stores the matched name if requested, and returns the decompressor function pointer. If the magic is unknown, both name and decompressor come from the sentinel and are `NULL`.

## State and Persistence
The format table is `__initconst` read-only data. No mutable state is maintained.

## Dependencies and Integration Points
Depends on the generic decompression API and optional per-format headers controlled by `CONFIG_DECOMPRESS_*`. It is used by initramfs, initrd, and boot-time decompression dispatch code that has already read the stream prefix.

## Risks and Test Signals
Risks include ambiguous two-byte magic matches, disabled format support returning a name with a `NULL` function, and callers passing too-short input. Test signals include boot/initramfs tests for every configured compression format, unknown-format handling, and configuration-matrix builds with individual decompressors disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress_bunzip2.c -->
# sources/distributed-fs/ceph-client/lib/decompress_bunzip2.c

## Purpose
Implements a small bzip2 decompressor adapted for Linux kernel preboot and initramfs use.

## APIs, Types, and Functions
The callable decompressor is `bunzip2()` in linked builds and `__decompress()` in preboot builds. Internal types include `struct group_data` for Huffman decoding tables and `struct bunzip_data` for input buffering, bit-buffer state, CRCs, block workspace, selectors, MTF tables, and output-resume state. Important helpers are `get_bits()`, `get_next_block()`, `read_bunzip()`, `start_bunzip()`, and `nofill()`.

## Control Flow
`start_bunzip()` allocates and initializes `bunzip_data`, validates the `BZh1` through `BZh9` header, builds the big-endian CRC table, and allocates the block workspace based on the block-size digit. `get_next_block()` parses block headers, validates signatures, builds selector and Huffman tables, decodes Huffman/MTF/RLE symbols into `dbuf`, and prepares the inverse Burrows-Wheeler traversal. `read_bunzip()` emits bytes, handles repeat runs, updates per-block and total CRCs, and requests the next block when needed. `bunzip2()` loops over `read_bunzip()`, flushing or writing into the caller's buffer, then verifies final CRC and frees all allocations.

## State and Persistence
All decompression state is in `struct bunzip_data` and temporary buffers allocated per call. With streaming output, `write*` fields persist between `read_bunzip()` calls. There is no cross-call global state.

## Dependencies and Integration Points
Depends on `linux/decompress/mm.h` allocation helpers, CRC32 polynomial constants, optional static inclusion for preboot, and the generic decompressor callback contract: `fill`, `flush`, `outbuf`, `pos`, and `error`. It integrates with compressed kernel and initramfs paths.

## Risks and Test Signals
Risks include malformed Huffman tables, invalid selectors, block-size overflows, CRC mismatches, short input/output callbacks, and memory pressure for `dbuf`. Test signals include bzip2 known-good streams, corrupted header/block/CRC cases, streaming `fill`/`flush` tests, block sizes 1-9, truncated input, and boot tests using bzip2-compressed initramfs or kernel images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress_bunzip2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress_inflate.c -->
# sources/distributed-fs/ceph-client/lib/decompress_inflate.c

## Purpose
Wraps zlib inflate to decompress gzip-compressed kernels, initramfs, and initrd images in both preboot static and linked kernel environments.

## APIs, Types, and Functions
The core helper is `__gunzip()`. Linked builds expose `gunzip()`, while preboot builds expose `__decompress()`. The file statically includes zlib inflate sources in `STATIC` builds and uses zlib headers in linked builds. `nofill()` is the fallback reader when no `fill` callback is supplied.

## Control Flow
`__gunzip()` allocates an output buffer when using `flush`, an input buffer when no input pointer is supplied, a zlib stream, and a zlib workspace. It validates the gzip magic/method, skips the basic 10-byte header and optional filename, initializes raw inflate with `zlib_inflateInit2(..., -MAX_WBITS)`, then loops reading input via `fill`, inflating, and flushing produced output. It treats `Z_STREAM_END` as success, maps other zlib errors to `-1`, records `pos` past the gzip trailer, and frees all allocations via cleanup labels.

## State and Persistence
Decompression state is per-call in `struct z_stream_s`, the workspace, input buffer, and output buffer. There is no global mutable state. The caller-provided output buffer is filled in place when no `flush` callback is used.

## Dependencies and Integration Points
Depends on zlib inflate internals, optional DFLTCC workspace sizing, `linux/decompress/mm.h`, and the kernel decompressor callback ABI. It integrates with `decompress.c` for gzip magic dispatch and with early boot code that may lack normal kernel allocation facilities.

## Risks and Test Signals
Risks include incomplete gzip header handling, truncated input, flush short writes, workspace sizing differences with DFLTCC, and unbounded output mode when `out_len` is zero. Test signals include gzip kernel/initramfs boot tests, optional filename header cases, corrupted gzip streams, streaming input/output callbacks, and generic-vs-known-tool decompression comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress_inflate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress_unlz4.c -->
# sources/distributed-fs/ceph-client/lib/decompress_unlz4.c

## Purpose
Provides the LZ4 wrapper used to decompress LZ4-compressed kernel, initramfs, and initrd images.

## APIs, Types, and Functions
The main decompressor is `unlz4()`; preboot builds expose `__decompress()`. Constants include `LZ4_DEFAULT_UNCOMPRESSED_CHUNK_SIZE` and `ARCHIVE_MAGICNUMBER`. It uses either statically included `lz4_decompress.c` or the linked kernel LZ4 API.

## Control Flow
`unlz4()` validates input/output mode, allocates buffers when callbacks are used, optionally reads the first chunk size with `fill`, and handles an optional archive magic word. It then loops over little-endian chunk sizes, skips repeated magic words, treats zero as EOF for non-stream input, bounds streaming chunk sizes by `LZ4_compressBound()`, and decompresses each chunk with `LZ4_decompress_safe()` or preboot `LZ4_decompress_fast()` using the output length footer. It flushes each decompressed chunk or advances the caller output pointer, updates `posp`, and frees temporary buffers.

## State and Persistence
State is per-call: input/output buffer pointers, chunk sizes, remaining input size, and output cursor. There is no global state or persistence after return.

## Dependencies and Integration Points
Depends on Linux LZ4 APIs, unaligned little-endian reads, preboot allocation helpers, and the generic decompressor callback contract. It is selected by `decompress.c` for LZ4 magic and used by boot/initramfs decompression.

## Risks and Test Signals
Risks include incorrect handling of chunk-size framing, preboot footer assumptions, short `fill` or `flush`, malformed zero/magic chunks, and output-size mismatches. Test signals include LZ4-compressed boot artifacts, multi-chunk streams, truncated chunk headers, oversized chunk rejection, and streaming callback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress_unlz4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress_unlzma.c -->
# sources/distributed-fs/ceph-client/lib/decompress_unlzma.c

## Purpose
Implements a compact LZMA decompressor for kernel preboot and initramfs use.

## APIs, Types, and Functions
The main function is `unlzma()`, with preboot `__decompress()`. Key types are `struct rc` for the range coder, `struct lzma_header` for properties/dictionary/output size, `struct writer` for dictionary/output state, and `struct cstate` for the LZMA state machine and repeated distances. Helpers include range-coder primitives, bit-tree decode, literal handling `process_bit0()`, match/repetition handling `process_bit1()`, and writer copy functions.

## Control Flow
`unlzma()` reads the LZMA header, validates property byte ranges, decodes `lc`, `lp`, and `pb`, endian-converts dictionary and output sizes, allocates the dictionary/output buffer and probability model, initializes all probabilities, then loops until the declared output size is reached or an end marker is decoded. Each iteration chooses literal or match processing using probability tables indexed by state and position. Output is written directly or through a circular dictionary flushed in chunks. Cleanup releases probability, output, and input buffers.

## State and Persistence
All state is per decompression call: range-coder position/code/range, probability arrays, dictionary buffer, output cursor, previous byte, and match distances. No data persists globally.

## Dependencies and Integration Points
Depends on `linux/decompress/mm.h`, compiler attributes, static/preboot inclusion conventions, and the generic decompressor ABI. It is dispatched by `decompress.c` for LZMA magic and used in early boot paths with limited library support.

## Risks and Test Signals
Risks include corrupt header properties, dictionary-size edge cases, invalid back references, output flush failures, range-coder EOF behavior, and memory pressure for large dictionaries or probability tables. Test signals include LZMA known-answer streams, truncated/corrupted match-distance cases, end-marker cases, streaming flush tests, and boot tests with LZMA-compressed images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress_unlzma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress_unlzo.c -->
# sources/distributed-fs/ceph-client/lib/decompress_unlzo.c

## Purpose
Wraps LZO decompression for lzop-framed kernel, initramfs, and initrd payloads.

## APIs, Types, and Functions
The linked/preboot decompressor is `unlzo()`, with preboot `__decompress()`. `parse_header()` validates and skips the lzop header. Constants define lzop magic, maximum block size, header flags, and minimum/maximum header lengths.

## Control Flow
`unlzo()` validates that input comes from either a pointer or `fill`, allocates input/output buffers as needed, reads and parses the lzop header, then iterates over blocks. Each block starts with uncompressed size, a zero terminator, compressed size, and checksum fields. The function rejects oversized or inconsistent sizes, fills enough compressed input, copies uncompressed blocks directly when sizes match, otherwise calls `lzo1x_decompress_safe()`, flushes or advances output, updates `posp`, and compacts unused streaming input without relying on `memmove()`.

## State and Persistence
State is per-call: input buffer, output buffer, current lzop cursor, and `posp`. No global state is kept.

## Dependencies and Integration Points
Depends on the Linux LZO API, unaligned big-endian reads, decompressor allocation helpers, and optional static inclusion of the LZO source. It is selected by magic dispatch and supports early environments where standard library helpers may be unavailable.

## Risks and Test Signals
Risks include malformed lzop header parsing, block size validation bugs, ignored checksum fields, short streaming reads, and flush failures. Test signals include lzop-compatible streams, uncompressed-block cases, corrupt size/header cases, streaming input tests, and boot/initramfs tests with LZO compression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress_unlzo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress_unxz.c -->
# sources/distributed-fs/ceph-client/lib/decompress_unxz.c

## Purpose
Provides the XZ wrapper used for kernel, initramfs, and initrd decompression, including support for constrained preboot environments.

## APIs, Types, and Functions
The main API is `unxz()`, with preboot `__decompress()` under `XZ_PREBOOT`. In static builds the file maps kernel allocation names to decompressor allocation helpers and supplies simple memory helpers such as `memeq`, `memzero`, and `memmove` when needed. It uses `xz_dec_init()`, `xz_dec_run()`, and `xz_dec_end()` from the in-kernel XZ decoder.

## Control Flow
`unxz()` initializes an XZ decoder, sets up input/output buffers for single-call or streaming mode, and loops calling `xz_dec_run()`. If input is exhausted, it reads more through `fill` or reports buffer error. If output fills or the decoder returns a final/error status, it flushes pending bytes when a `flush` callback is present. On completion it records consumed input, ends the decoder, maps `XZ_STREAM_END` to success, and maps format/options/data/buffer/memory errors to caller-visible error strings.

## State and Persistence
All decoder state is per-call in the `xz_dec` instance and `xz_buf`. Temporary input/output buffers may be allocated and freed within the call. No global state is mutated.

## Dependencies and Integration Points
Depends on the in-kernel XZ decoder, CRC32 support in preboot configuration, decompressor memory helpers, and the generic decompressor ABI. It integrates with `decompress.c` for XZ magic and architecture boot code that may decompress in place.

## Risks and Test Signals
Risks include in-place decompression safety margins, unsupported XZ options, streaming buffer starvation, short flush writes, and preboot helper mismatches. Test signals include XZ-compressed kernel boot tests, BCJ/LZMA2 option coverage, corrupt/truncated streams, single-call and callback modes, and comparison with known XZ output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress_unxz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress_unzstd.c -->
# sources/distributed-fs/ceph-client/lib/decompress_unzstd.c

## Purpose
Provides the Zstandard decompression wrapper for compressed kernel, initramfs, and initrd payloads.

## APIs, Types, and Functions
The main implementation is `__unzstd()`. Linked builds expose `unzstd()`, while preboot builds expose `__decompress()`. Helpers include `handle_zstd_error()` for mapping zstd errors to kernel messages and `decompress_single()` for the fast single-buffer path. Constants define the maximum supported zstd window size and streaming I/O buffer size.

## Control Flow
If both `fill` and `flush` are absent, `__unzstd()` calls `decompress_single()`, which allocates a dctx workspace, finds the compressed frame size to ignore trailing junk, and decompresses into the caller buffer. Streaming mode allocates input and/or output buffers as needed, reads the frame header, validates that the window size is supported, allocates a `zstd_dstream` workspace sized to that window, then loops refilling input, calling `zstd_decompress_stream()`, flushing produced bytes, and updating `in_pos` until the frame completes. Cleanup frees all allocated buffers and workspace.

## State and Persistence
All state is per-call: zstd context/workspace, input/output buffer positions, frame header, and optional consumed-input counter. No global mutable state persists.

## Dependencies and Integration Points
Depends on Linux zstd APIs, xxhash and zstd source inclusion for static preboot builds, decompressor allocation helpers, and the generic decompressor callback ABI. It is selected by `decompress.c` for zstd magic and includes documented in-place safety margin assumptions.

## Risks and Test Signals
Risks include accepting unsupported window sizes, mishandling truncated frame headers, output buffer overflow when `out_len` is omitted, flush failures, and memory pressure from large windows. Test signals include zstd-compressed boot artifacts, single-shot and streaming decompression tests, corrupt checksum/prefix/window cases, trailing-junk handling, and comparisons with zstd reference output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/decompress_unzstd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/devmem_is_allowed.c -->
# sources/distributed-fs/ceph-client/lib/devmem_is_allowed.c

## Purpose
Provides the generic fallback policy for `/dev/mem` physical-memory access when an architecture does not provide a stricter implementation.

## APIs, Types, and Functions
Defines `int devmem_is_allowed(unsigned long pfn)`, returning `1` unconditionally.

## Control Flow
There is no branching: every page frame number is allowed by this generic helper.

## State and Persistence
No state is read or modified.

## Dependencies and Integration Points
This weak/default-style library implementation is used by `/dev/mem` access checks on architectures that do not override it. It integrates with memory device drivers and security policy controlled by architecture and Kconfig choices.

## Risks and Test Signals
The risk is permissive raw physical memory access if used on platforms that should restrict RAM or device regions. Test signals include architecture build coverage ensuring stricter implementations override this where required, `/dev/mem` access tests under `CONFIG_STRICT_DEVMEM`, and security policy review for target architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/devmem_is_allowed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/devres.c -->
# sources/distributed-fs/ceph-client/lib/devres.c

## Purpose
Implements managed device-resource wrappers for I/O memory mapping, I/O port mapping, and write-combining memory-type reservations so driver cleanup happens automatically on detach.

## APIs, Types, and Functions
Exports `devm_ioremap()`, `devm_ioremap_uc()`, `devm_ioremap_wc()`, `devm_iounmap()`, `devm_ioremap_resource()`, `devm_ioremap_resource_wc()`, `devm_of_iomap()`, optional `devm_ioport_map()` and `devm_ioport_unmap()`, `devm_arch_phys_wc_add()`, and `devm_arch_io_reserve_memtype_wc()`. Internal helpers include `__devm_ioremap()`, `__devm_ioremap_resource()`, release callbacks, and match callbacks. `enum devm_ioremap_type` selects normal, uncached, write-combined, and non-posted mappings.

## Control Flow
Mapping helpers allocate a small devres record on the device's NUMA node, perform the requested mapping, store the mapped address or reservation handle, and add the record to devres. Resource helpers validate that `struct resource` is memory, choose non-posted mapping when flagged, allocate a descriptive region name, request the memory region, then map it; on failure they unwind the requested region and return an `IOMEM_ERR_PTR()`. Unmap helpers release the matching devres entry and warn if no managed mapping is found. WC helpers add architecture memory-type reservations and register matching release callbacks.

## State and Persistence
State persists in the device's devres list until explicit release or driver detach. Mapped I/O addresses, requested regions, I/O port mappings, MTRR/WC handles, and WC reservations are automatically released by callbacks.

## Dependencies and Integration Points
Depends on device core devres APIs, `ioremap*`, `iounmap`, resource management, OF address translation, I/O port mapping when configured, and architecture WC APIs. It is widely used by platform, PCI, OF, and bus drivers that need MMIO lifetime tied to a `struct device`.

## Risks and Test Signals
Risks include resource leaks on partial failures, double-unmap warnings, mapping a non-memory resource, missing `IORESOURCE_MEM_NONPOSTED` semantics, conflicts hidden by unmanaged `of_iomap()`, and incorrect WC cleanup. Test signals include driver probe/remove cycles, fault-injection for allocation and request failures, devres leak detection, OF mapping tests, and architecture-specific WC/MTRR reservation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/devres.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dhry.h -->
# sources/distributed-fs/ceph-client/lib/dhry.h

## Purpose
Defines the common data model and function prototypes for the kernel's Dhrystone 2.1 benchmark implementation.

## APIs, Types, and Functions
The header documents the benchmark history and measurement rules, then defines `Enumeration`, integer aliases, `Capital_Letter`, `Boolean`, `Str_30`, one- and two-dimensional array types, and `struct record`/`Rec_Type`/`Rec_Pointer` with a discriminated-union-like variant. It declares globals `Int_Glob` and `Ch_1_Glob`, procedures `Proc_6`, `Proc_7`, `Proc_8`, functions `Func_1`, `Func_2`, and benchmark entry `dhry(int n)`.

## Control Flow
The header has no executable flow. It fixes the shared types and prototypes used by `dhry_1.c`, `dhry_2.c`, and `dhry_run.c`.

## State and Persistence
The declared globals are defined in `dhry_1.c`. Type definitions have no runtime state.

## Dependencies and Integration Points
It is included by both benchmark implementation files and by the module runner. It integrates Dhrystone's historical C benchmark structure with kernel allocation, timing, and module-parameter wrappers.

## Risks and Test Signals
Risks include changing types or prototypes in a way that invalidates Dhrystone comparability, making optimization easier than intended, or breaking separate compilation assumptions. Test signals include successful builds of all Dhrystone files, benchmark self-check output from `dhry()`, and sanity comparisons of reported Dhrystones per second across iterations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dhry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dhry_1.c -->
# sources/distributed-fs/ceph-client/lib/dhry_1.c

## Purpose
Contains the first implementation part of the Dhrystone benchmark, including global benchmark state, main benchmark loop, and several procedures.

## APIs, Types, and Functions
Defines exported benchmark globals `Int_Glob` and `Ch_1_Glob`, plus static globals `Ptr_Glob`, `Next_Ptr_Glob`, `Bool_Glob`, `Ch_2_Glob`, `Arr_1_Glob`, and `Arr_2_Glob`. Internal procedures include `Proc_1`, `Proc_2`, `Proc_3`, `Proc_4`, and `Proc_5`. The public entry is `int dhry(int n)`, which returns a measured Dhrystones-per-second value or an error-style result when validation fails.

## Control Flow
`dhry()` allocates two records, initializes Dhrystone globals and strings, captures start time, runs the historical Dhrystone loop for `n` iterations, captures end time, validates final variable values with assertion macros, frees records, and reports a rate based on elapsed microseconds. The loop exercises procedure calls, string operations, arithmetic, conditionals, and array/record access in the prescribed benchmark pattern. The static procedures mutate record fields, globals, and reference parameters as required by the original benchmark.

## State and Persistence
Benchmark state is global during a `dhry()` run, but records are allocated and freed per invocation. The static arrays and scalar globals retain their final values after a run until overwritten by the next invocation.

## Dependencies and Integration Points
Depends on `dhry.h`, kernel timekeeping, slab allocation, and string helpers. `dhry_run.c` invokes `dhry()` from module init or a module parameter.

## Risks and Test Signals
Risks include compiler optimization altering benchmark semantics, allocation failure, timing granularity for small `n`, overflow in rate calculation for extreme inputs, and validation failures if procedures drift from the Dhrystone reference. Test signals include `dhry()` self-checks, multiple iteration counts, module runner output, and build tests under different optimization levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dhry_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dhry_2.c -->
# sources/distributed-fs/ceph-client/lib/dhry_2.c

## Purpose
Contains the second implementation part of Dhrystone, providing the functions and procedures corresponding to the original benchmark's secondary package.

## APIs, Types, and Functions
Defines `Proc_6()`, `Proc_7()`, `Proc_8()`, `Func_1()`, and `Func_2()` declared in `dhry.h`. These operate on enumerations, integer aliases, character values, strings, and array parameters, and they reference shared globals such as `Int_Glob` and `Ch_1_Glob`.

## Control Flow
`Proc_6()` maps enumeration input through conditional/switch logic and may inspect `Int_Glob`. `Proc_7()` computes a small integer expression into a reference parameter. `Proc_8()` mutates selected array cells and updates `Int_Glob`. `Func_1()` compares characters and returns an enumeration result while updating `Ch_1_Glob` in one branch. `Func_2()` performs Dhrystone's string/character comparison loop and returns a boolean-style result.

## State and Persistence
Most state is caller-provided through parameters. Persistent effects are writes to global `Int_Glob` and `Ch_1_Glob` plus mutations to the caller's arrays.

## Dependencies and Integration Points
Depends on `dhry.h` and kernel string helpers. It integrates with `dhry_1.c` through shared globals and the prescribed Dhrystone call graph.

## Risks and Test Signals
Risks include subtle changes that break the benchmark's reference final values, string comparison behavior differences, and array index assumptions. Test signals are the validation checks in `dhry()`, build coverage with separate compilation, and benchmark runs across several iteration counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dhry_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dhry_run.c -->
# sources/distributed-fs/ceph-client/lib/dhry_run.c

## Purpose
Provides the loadable/module-parameter wrapper for running the kernel Dhrystone benchmark.

## APIs, Types, and Functions
Defines module parameters `run` and `iterations`. `run` uses a custom `kernel_param_ops` setter `dhry_run_set()` so writing true triggers a benchmark run. `dhry_benchmark()` invokes `dhry(iterations)` and prints results. `dhry_init()` optionally runs the benchmark at module initialization. Module metadata names the author, description, and GPL license.

## Control Flow
If `run` is set at load time or later through the module parameter, `dhry_run_set()` parses the boolean, stores it, and calls `dhry_benchmark()` when true. `dhry_benchmark()` chooses or reports the iteration count, calls `dhry()`, and prints the resulting Dhrystones per second. `dhry_init()` performs the same action when the module is initialized with `run=true`.

## State and Persistence
Persistent module state is `dhry_run` and `iterations`. Benchmark implementation globals live in `dhry_1.c` and are reset by each `dhry()` invocation.

## Dependencies and Integration Points
Depends on module parameter APIs, printk, and `dhry.h`. It integrates the benchmark with module loading and sysfs/module-parameter control.

## Risks and Test Signals
Risks include running CPU-bound benchmark work unexpectedly from parameter writes, invalid iteration values, noisy logs, and benchmark output affected by CPU frequency or scheduling. Test signals include loading with `run=1`, writing the parameter after load, using explicit and default iteration counts, and checking that invalid parameter input is rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dhry_run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/digsig.c -->
# sources/distributed-fs/ceph-client/lib/digsig.c

## Purpose
Implements legacy digital signature verification using RSA public keys stored in kernel keyrings and SHA-1 hashing.

## APIs, Types, and Functions
Exports `digsig_verify(struct key *keyring, const char *sig, int siglen, const char *data, int datalen)`. Internal helpers are `pkcs_1_v1_5_decode_emsa()` for decoding RSA PKCS#1 v1.5 EMSA padding and `digsig_verify_rsa()` for MPI-based RSA verification. It consumes `struct signature_hdr`, `struct pubkey_hdr`, user-key payloads, MPI values, and SHA-1 contexts.

## Control Flow
`digsig_verify()` validates the signature header, requires RSA, derives a hex key name from the big-endian key ID, searches the supplied keyring or requests a user key, hashes the data plus signature header with SHA-1, and calls `digsig_verify_rsa()` on the signature MPI payload. The RSA helper locks the key payload, validates public-key header version/algorithm/MPI count, reads modulus and exponent MPIs, computes `sig^e mod n`, left-pads the result to modulus length, decodes PKCS#1 v1.5 padding, compares the recovered digest with the computed hash, frees all MPIs/buffers, and releases the key semaphore.

## State and Persistence
The code does not persist verifier state. It reads key payload state under the key semaphore and allocates temporary MPI/output buffers per call. Key lifetime is managed by the keyring subsystem through `key_put()`.

## Dependencies and Integration Points
Depends on the key management subsystem, user-key payload format, MPI library, SHA-1 crypto implementation, endian helpers, and `linux/digsig.h` signature/public-key structures. It integrates with kernel consumers needing simple RSA signature verification against keyrings.

## Risks and Test Signals
Risks include SHA-1's weak collision resistance, strict support for only RSA and a legacy padding format, malformed MPI parsing, key revocation races, signature length edge cases, and leaking distinction between key lookup and verification failures. Test signals include valid/invalid RSA signature vectors, revoked or malformed user keys, wrong key ID, unsupported algorithm returns, padding corruption, and memory-failure tests through MPI/buffer allocation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/digsig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dim/Makefile -->
# sources/distributed-fs/ceph-client/lib/dim/Makefile

## Purpose
Builds the Dynamic Interrupt Moderation library objects when `CONFIG_DIMLIB` is enabled.

## APIs, Types, and Functions
The makefile defines `obj-$(CONFIG_DIMLIB) += dimlib.o` and composes `dimlib-y` from `dim.o`, `net_dim.o`, and `rdma_dim.o`.

## Control Flow
There is no runtime control flow. Kbuild includes or omits the aggregate object based on the Kconfig symbol, then links the three implementation objects into `dimlib.o`.

## State and Persistence
No runtime state exists in the makefile. Build output persists as compiled objects.

## Dependencies and Integration Points
Depends on Kbuild and `CONFIG_DIMLIB`. It integrates generic DIM helpers, network DIM, and RDMA DIM into one library for drivers.

## Risks and Test Signals
Risks include missing one implementation object from the aggregate, disabled library symbols for drivers that expect DIM, and Kconfig dependency mismatch. Test signals include `CONFIG_DIMLIB=y/m` builds, link tests for net/RDMA drivers using DIM symbols, and module packaging checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dim/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dim/dim.c -->
# sources/distributed-fs/ceph-client/lib/dim/dim.c

## Purpose
Provides common state-machine helpers and statistics calculation for Dynamic Interrupt Moderation.

## APIs, Types, and Functions
Exports `dim_on_top()`, `dim_turn()`, `dim_park_on_top()`, `dim_park_tired()`, and `dim_calc_stats()`. These operate on `struct dim`, `struct dim_sample`, and `struct dim_stats` from `<linux/dim.h>`.

## Control Flow
`dim_on_top()` interprets tuning direction and step counters to decide whether a local optimum has been reached. `dim_turn()` flips between left and right tuning directions and resets the new direction's step counter. Parking helpers reset counters and set parking states. `dim_calc_stats()` computes elapsed microseconds and counter deltas with wrap handling, then derives packets, bytes, events, completions per millisecond, and completion-per-event ratio.

## State and Persistence
The functions mutate caller-owned `struct dim` state only. No global state is maintained. Statistics are derived from caller-provided samples.

## Dependencies and Integration Points
Depends on `linux/dim.h`, time delta helpers, bit-gap counter wrap helpers, and module export infrastructure. It is shared by `net_dim.c`, `rdma_dim.c`, and drivers using DIM.

## Risks and Test Signals
Risks include divide-by-zero without the zero-delta guard, counter wrap mistakes, misclassifying local optimum state, and tuning oscillation from wrong step counters. Test signals include synthetic sample deltas, wraparound tests, state-machine unit tests for each tune state, and driver-level interrupt moderation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dim/dim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dim/net_dim.c -->
# sources/distributed-fs/ceph-client/lib/dim/net_dim.c

## Purpose
Implements network Dynamic Interrupt Moderation profiles, profile storage on `struct net_device`, and the network DIM tuning algorithm.

## APIs, Types, and Functions
Exports profile accessors `net_dim_get_rx_moderation()`, `net_dim_get_def_rx_moderation()`, `net_dim_get_tx_moderation()`, and `net_dim_get_def_tx_moderation()`. Device integration APIs are `net_dim_init_irq_moder()`, `net_dim_free_irq_moder()`, `net_dim_setting()`, `net_dim_work_cancel()`, `net_dim_get_rx_irq_moder()`, `net_dim_get_tx_irq_moder()`, `net_dim_set_rx_mode()`, `net_dim_set_tx_mode()`, and main algorithm `net_dim()`. Static profile tables provide RX/TX EQE and CQE moderation values.

## Control Flow
Initialization allocates `dev->irq_moder`, copies default RX/TX profiles based on flags and modes, stores work callbacks, and publishes profile pointers with RCU. Freeing clears RCU pointers and releases profile copies after grace periods. `net_dim_setting()` initializes a `struct dim` work item and mode for RX or TX. `net_dim()` collects event deltas until `DIM_NEVENTS`, computes stats, compares byte rate first, packet rate second, and event rate inversely, then steps left/right, turns, parks on top, or parks tired. When the profile index changes it sets `DIM_APPLY_NEW_PROFILE` and schedules driver work.

## State and Persistence
Persistent state lives in `dev->irq_moder` profile copies, mode fields, coal/profile flags, work callbacks, and caller-owned `struct dim` tuning state. RCU protects profile pointer replacement/free. No module-global mutable state is used beyond static profile templates.

## Dependencies and Integration Points
Depends on `<linux/dim.h>`, `<linux/rtnetlink.h>`, RCU, workqueues, netdevice storage, and driver-supplied DIM work callbacks that actually apply the selected moderation values. It integrates with NIC RX/TX completion paths and ethtool-like coalescing configuration.

## Risks and Test Signals
Risks include invalid profile mode/index, missing RTNL when freeing, RCU misuse, scheduling work after teardown, unstable tuning under noisy traffic, and dereferencing `dev->irq_moder` when not initialized. Test signals include NIC driver DIM tests, RCU/KASAN teardown tests, profile mode switching, synthetic traffic ramps, work cancellation on device close, and lockdep checks around RTNL assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dim/net_dim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dim/rdma_dim.c -->
# sources/distributed-fs/ceph-client/lib/dim/rdma_dim.c

## Purpose
Implements the RDMA-specific Dynamic Interrupt Moderation tuning algorithm.

## APIs, Types, and Functions
The exported API is `rdma_dim(struct dim *dim, u64 completions)`. Internal helpers are `rdma_dim_step()`, `rdma_dim_stats_compare()`, and `rdma_dim_decision()`.

## Control Flow
`rdma_dim()` increments the measuring sample's event and completion counters, then follows the common DIM states. In measuring state it waits for `DIM_NEVENTS`, calculates stats, and calls `rdma_dim_decision()`. RDMA comparison prioritizes completions per millisecond and then completion-per-event ratio. The decision function turns direction on worse stats, steps on better stats, resets to profile zero for low completion-per-event ratios in same stats, and schedules work when the profile index changes.

## State and Persistence
All state is caller-owned in `struct dim`, especially sample counters, previous stats, profile index, tune state, and work item. There is no global mutable state.

## Dependencies and Integration Points
Depends on common DIM helpers from `dim.c`, `linux/dim.h`, and workqueues. It integrates with RDMA completion paths and driver work callbacks that apply new CQ moderation profiles.

## Risks and Test Signals
Risks include completion counter overflow assumptions, profile-index edge handling, oscillation under noisy RDMA workloads, and scheduling work after queue teardown. Test signals include synthetic completion-rate tests, profile edge tests, RDMA driver CQ moderation integration, and work cancellation/teardown races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dim/rdma_dim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dump_stack.c -->
# sources/distributed-fs/ceph-client/lib/dump_stack.c

## Purpose
Provides the generic `dump_stack()` implementation and shared stack-dump header printing for architectures that do not override it.

## APIs, Types, and Functions
Defines `dump_stack_set_arch_desc()`, `dump_stack_print_info()`, `show_regs_print_info()`, internal `__dump_stack()`, exported `dump_stack_lvl()`, and exported `dump_stack()`. Static state is `dump_stack_arch_desc_str[128]`. Build-ID output is controlled by `CONFIG_STACKTRACE_BUILD_ID`.

## Control Flow
Architectures can set a hardware description string during init. `dump_stack_print_info()` prints CPU, UID, PID, task name, kdump state, taint flags, kernel release/version, preemption model, optional build ID, verbose taint info, optional hardware name, worker info, stop-machine info, and sched-ext info. `__dump_stack()` prints that header and calls `show_stack()`. `dump_stack_lvl()` serializes printk output with `printk_cpu_sync_get_irqsave()` unless the current CPU is already in panic, then calls `__dump_stack()` and releases synchronization. `dump_stack()` uses `KERN_DEFAULT`.

## State and Persistence
The only persistent mutable state is the optional architecture description string. The rest is sampled from current task, credentials, UTS state, taint state, kexec state, and scheduler/debug subsystems at dump time.

## Dependencies and Integration Points
Depends on printk, build ID, scheduler/debug helpers, SMP CPU ID, atomics, kexec, UTS namespace, stop-machine diagnostics, and architecture `show_stack()`. It integrates with WARN/OOPS/debug call sites and architecture-specific stack-dump implementations that reuse `dump_stack_print_info()`.

## Risks and Test Signals
Risks include printk serialization deadlocks during panic, unsafe current-task metadata access in unusual contexts, truncated architecture description, and missing architecture stack output if `show_stack()` is weak or unavailable. Test signals include explicit `dump_stack()` calls, WARN/OOPS paths, panic-time stack dumps, build-ID enabled/disabled builds, and architecture override builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dump_stack.c -->
