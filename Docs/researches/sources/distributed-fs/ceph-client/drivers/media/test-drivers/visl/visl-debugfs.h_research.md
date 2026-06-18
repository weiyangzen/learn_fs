# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-debugfs.h

## Purpose
`visl-debugfs.h` declares the debugfs bitstream tracing interface and provides no-op inline fallbacks when `CONFIG_VISL_DEBUGFS` is disabled.

## Important APIs, types, and functions
When debugfs support is enabled, it declares `visl_debugfs_init()`, `visl_debugfs_bitstream_init()`, `visl_trace_bitstream()`, `visl_debugfs_clear_bitstream()`, `visl_debugfs_bitstream_deinit()`, and `visl_debugfs_deinit()`. The declarations depend on `struct visl_dev`, `struct visl_ctx`, and `struct visl_run` from `visl.h` and `visl-dec.h`.

When debugfs support is disabled, all APIs remain available as inline stubs. Initialization stubs return success and action stubs do nothing, allowing callers in core, video, and decode paths to avoid preprocessor branching.

## Control flow
The header does not execute logic directly. Its compile-time branch decides whether VISL links real debugfs behavior or no-op behavior. This keeps the runtime control flow in `visl-core.c`, `visl-video.c`, and `visl-dec.c` identical across configurations.

## State and persistence
The header defines no state. With the disabled branch, VISL has no bitstream debugfs state. With the enabled branch, state is owned by `struct visl_dev` fields compiled under `CONFIG_VISL_DEBUGFS`.

## Dependencies and integration points
It integrates the optional debugfs implementation with the rest of the VISL driver and is included by the core, video, and decoder implementation files.

## Risks and test signals
The main risk is API drift between the real functions and no-op stubs. Build coverage should include both `CONFIG_VISL_DEBUGFS=y` and disabled configurations. Runtime test signals are successful VISL operation with debugfs absent and visible bitstream dump files when enabled and tracing is configured.
