# sources/distributed-fs/ceph-client/include/sound/sdca_fdl.h

Source read summary: 105 lines, SDCA Function Download (FDL) state and helpers.

Purpose: declares state and control/status masks for SDCA function-download transactions plus helpers to allocate state, process interrupts, synchronize downloads, and reset functions.

Important APIs, types, and functions: `struct fdl_state` holds begin/done completions, timeout delayed work, mutex, attached interrupt, current FDL set, and file index. Macros define host/device FDL status combinations and masks: complete, more files, file available, file OK, more files OK, reset/abort/ack/needs-set bits. Enabled APIs are `sdca_fdl_alloc_state()`, `sdca_fdl_process()`, `sdca_fdl_sync()`, and `sdca_reset_function()`; disabled stubs return success.

Control flow: SDCA interrupt setup allocates FDL state, interrupt processing advances file/chunk transfer status, synchronization waits for begin/done completions and handles timeout work, and reset helper requests function reset through regmap.

State and persistence behavior: FDL state persists across interrupts during a download cycle only. Downloaded function files may affect device firmware/runtime state, but no persistent storage is defined here.

Dependencies and integration points: depends on completions, workqueues, mutexes, SDCA function data, interrupts, interrupt info, and regmap. It integrates SDCA firmware/function download with ASoC SDCA devices.

Risks and edge cases: timeout work racing IRQ handlers, incorrect mask interpretation, abort/reset sequencing, file index bounds, and disabled stubs falsely indicating download success.

Test signals: FDL allocation, interrupt-driven chunk/file progression, timeout and abort paths, multi-file sets, reset requests, sync completion ordering, and disabled-config compile behavior.
