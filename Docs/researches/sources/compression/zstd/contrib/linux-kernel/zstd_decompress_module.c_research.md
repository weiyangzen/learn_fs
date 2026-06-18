<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_decompress_module.c -->
# sources/compression/zstd/contrib/linux-kernel/zstd_decompress_module.c

## Purpose
This module adapts zstd decompression APIs to Linux kernel naming and workspace semantics.

## Important APIs, Types, And Functions
Exports include error helpers, dctx/ddict workspace and lifetime functions, `zstd_init_dctx`, one-shot decompression, ddict decompression, dstream workspace/init/reset/stream, `zstd_find_frame_compressed_size`, and `zstd_get_frame_header`.

## Control Flow
Callers allocate a workspace according to the bound function, initialize a dctx or dstream with custom memory, then call one-shot or streaming decompression. The wrapper functions mostly forward directly to zstd internals with type aliases from `linux_zstd.h`.

## State And Persistence
All decompression state is held in caller-owned contexts and dictionaries. The module itself has no persistent mutable state.

## Dependencies And Integration Points
It depends on the decompression source aggregation, `zstd_deps.h`, and kernel module export macros. It is the decompression counterpart consumed by btrfs/f2fs-style kernel code and the user-space test harness.

## Risks
Window-size and workspace-bound mismatches can cause caller allocation failures. Frame-header forwarding must preserve zstd error codes so kernel consumers can distinguish short input from corruption.

## Test Signals
`test.c` and `static_test.c` cover one-shot, streaming, ddict/static-adjacent, frame-size, and header paths sufficiently for linkage and common behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_decompress_module.c -->
