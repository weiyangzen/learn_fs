<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_compress_module.c -->
# sources/compression/zstd/contrib/linux-kernel/zstd_compress_module.c

## Purpose
This module adapts zstd compression APIs to kernel-style names and workspace-based allocation semantics.

## Important APIs, Types, And Functions
It exports level queries, `zstd_compress_bound`, parameter selection, cctx workspace bounds, cctx/cdict creation/free, one-shot compression, cstream workspace/reset/stream/flush/end functions, external sequence producer registration, and `zstd_compress_sequences_and_literals`. `zstd_cctx_init`, `ZSTD_FORWARD_IF_ERR`, and external-sequence workspace helpers are important internal glue.

## Control Flow
Callers query parameters/workspace sizes, initialize contexts over caller-provided memory, then use one-shot or streaming compression. Streaming initialization sets pledged size unknown, frame flags, and workspace, while subsequent stream calls forward to zstd internals.

## State And Persistence
Compression state lives in caller-provided workspaces and zstd context structs. The module persists no data across calls except what the caller keeps in the context.

## Dependencies And Integration Points
It includes zstd compression sources and kernel dependency shims. Filesystem/kernel consumers use the exported `zstd_*` names from `linux_zstd.h`.

## Risks
Workspace-bound correctness is critical; underestimates can corrupt or fail kernel callers. Parameter translation, external sequence producer setup, and deprecated/static API use must stay aligned with upstream zstd internals.

## Test Signals
`test.c` exercises btrfs-like compression, streaming output, level bounds, and workspace APIs. Macro tests catch include/dependency regressions.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_compress_module.c -->
