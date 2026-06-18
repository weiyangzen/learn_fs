# sources/distributed-fs/ceph-client/lib/xz/xz_dec_bcj.c

## Purpose
Implements XZ Branch/Call/Jump filters that post-process LZMA2 output for executable code. Supported filters are conditionally compiled for x86, PowerPC, ARM, ARM-Thumb, SPARC, ARM64, and RISC-V.

## APIs and control flow
Internal APIs are `xz_dec_bcj_create`, `xz_dec_bcj_reset`, and `xz_dec_bcj_run`. `struct xz_dec_bcj` stores filter type, downstream return value, single-call mode, absolute block position, x86 mask state, temporary output fields, and a 16-byte mixed filtered/unfiltered buffer. `xz_dec_bcj_run` flushes filtered temp bytes, calls `xz_dec_lzma2_run`, applies `bcj_apply`, buffers lookahead bytes that cannot yet be filtered, and propagates `XZ_OK` or `XZ_STREAM_END`.

## State, dependencies, and integration
BCJ state persists across calls because instruction windows can cross buffer boundaries. `xz_dec_stream.c` activates this layer when a Block Header has a BCJ filter followed by LZMA2. `xz_private.h` and Kconfig decide which IDs are accepted.

## Risks and test signals
Boundary and alignment mistakes corrupt output. Unsupported filter IDs must return `XZ_OPTIONS_ERROR`. Single-call mode uses output as workspace, requiring higher-layer rollback on failure. Tests should decode streams with every enabled BCJ filter, tiny output buffers, single/multi-call modes, unsupported IDs, and architecture-specific boundary vectors.
