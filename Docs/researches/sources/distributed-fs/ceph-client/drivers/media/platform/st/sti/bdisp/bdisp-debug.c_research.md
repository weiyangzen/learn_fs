# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-debug.c

Purpose: implements debugfs and performance diagnostic support for the ST BDISP 2D blitter driver.

Important APIs and functions: exported driver-facing helpers are `bdisp_dbg_perf_begin`, `bdisp_dbg_perf_end`, `bdisp_debugfs_create`, and `bdisp_debugfs_remove`. Debugfs show callbacks include `regs_show`, `last_nodes_show`, `last_nodes_raw_show`, `last_request_show`, and `perf_show`. Numerous dump helpers decode BDISP node fields such as instruction bits, target/source pixel types, coordinates, sizes, filter control, resize factors, resize initial values, and color-conversion matrices.

Control flow: hardware request paths call `bdisp_dbg_perf_begin` before processing and `bdisp_dbg_perf_end` after completion to update last/min/max/total duration. Probe/debug setup calls `bdisp_debugfs_create`, which creates a per-device directory named from `BDISP_NAME` and `bdisp->id`, then installs read-only debugfs files. Reading `regs` resumes the device with runtime PM, dumps static, plug, node, filter, and luma-filter registers, then releases PM. Reading `last_nodes` decodes copied nodes until `MAX_NB_NODE` or a zero next-node pointer; `last_nodes_raw` dumps raw node words; `last_request` summarizes copied source/destination request geometry; `perf` reports average/min/max/last processing time and approximate FPS.

State and persistence: diagnostic state lives under `bdisp->dbg`, including copied node pointers, copied request, debugfs dentry, hardware start time, and performance duration counters. This is volatile runtime/debug state and is reset when the device is removed or driver state is reinitialized. Debugfs files expose current in-memory snapshots only.

Dependencies and integration points: depends on Linux debugfs, seq_file show helpers, runtime PM, BDISP core structures from `bdisp.h`, coefficient constants from `bdisp-filter.h`, and register/bit definitions from `bdisp-reg.h`. It integrates with the main BDISP driver through copied request/node snapshots and performance hooks.

Risks: debugfs has no stable ABI, but it can still expose stale copied pointers if lifecycle handling outside this file is wrong. `regs_show` wakes hardware for register reads and could perturb power-management timing. FPS math divides by duration fields; `min_duration` is initialized on first request, but corrupted or zero state could divide by zero. Raw node dumps expose DMA programmed values, which may be sensitive in debug environments. Directory name uses a fixed 16-byte buffer and depends on `BDISP_NAME` plus id fitting.

Test signals: build with `CONFIG_DEBUG_FS`; probe creates expected debugfs files; reading each file before and after a request; runtime PM balance after `regs`; performance counters across multiple requests; and lockdep/KASAN tests for remove while debugfs readers are active.
