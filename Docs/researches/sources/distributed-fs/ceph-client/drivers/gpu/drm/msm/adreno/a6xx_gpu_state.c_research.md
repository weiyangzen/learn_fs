# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu_state.c

## Purpose

`a6xx_gpu_state.c` implements A6xx/A7xx GPU crash-state capture and printing. It gathers generic Adreno state, GMU registers and buffers, CP indexed registers, main GPU register ranges, shader/debug memories, clusters, DBGAHB ranges, debugbus blocks, HFI queue history, and then emits a YAML-like devcoredump through `a6xx_show()`.

## Important APIs, Types, And Functions

- `struct a6xx_gpu_state` extends `struct msm_gpu_state` with arrays of captured GMU registers, GPU registers, shader blocks, clusters, DBGAHB clusters, indexed registers, debugbus blocks, GMU BO snapshots, HFI history, allocation list, and `gpu_initialized`.
- `struct a6xx_gpu_state_obj` pairs a static table handle with captured dword data and optional runtime count.
- `a6xx_gpu_state_get()` is the capture entry point used by the GPU function table.
- `a6xx_gpu_state_put()` releases state through kref.
- `a6xx_show()` prints all captured data.
- `a6xx_crashdumper_init()` and `a6xx_crashdumper_run()` allocate a 1 MiB GPU scratch BO, write a CP crashdump script, run it, and copy results.
- `a6xx_get_registers()` and `a7xx_get_registers()` capture normal register ranges via AHB or crashdumper depending on SMMU/fault state.
- `a6xx_get_shaders()/a7xx_get_shaders()`, `a6xx_get_clusters()/a7xx_get_clusters()`, and DBGAHB helpers capture deeper block state through CP apertures.
- `a6xx_get_gmu_registers()`, `a6xx_snapshot_gmu_bo()`, and `a6xx_snapshot_gmu_hfi_history()` preserve GMU-side diagnostics.
- Debugbus helpers collect GX, CX, and VBIF/GBIF debugbus data when the global `snapshot_debugbus` option is active.

## Control Flow

`a6xx_gpu_state_get()` allocates state, initializes the owned allocation list, and calls `adreno_gpu_state_get()` first. On full GMU targets it snapshots GMU CX/RSCC/GPUCC/GX registers, GMU log/HFI/debug BO contents, and HFI queue history before checking GX state. If GX is off, it returns a GMU-only plus generic snapshot.

If GX is on, it halts SQE with `CP_SQE_CNTL = 3`, captures indexed CP registers, detects SMMU stalled-on-fault state, and only initializes the crashdumper if the SMMU is not stalled and hardware is initialized. This distinction matters because the crashdumper needs GPU memory writes, which will fail while translation is stalled.

For A7xx, capture uses generated `adreno_gen7_*_snapshot.h` tables. It collects pre-crashdumper registers, optional crashdumper register lists, shader blocks, clusters, SPTP/DBGAHB clusters, releases the crashdump BO, and then reads post-crashdumper registers. For A6xx, it uses local tables from `a6xx_gpu_state.h`, reading AHB-safe registers directly and deeper ranges through crashdumper when available. If `snapshot_debugbus` is true, it configures debugbus muxes and reads GX/CX/VBIF/GBIF data. Finally it records whether the GPU was initialized.

Printing mirrors the captured object arrays. It emits generic Adreno state, GMU BOs with encoded data, HFI queue history, register lists, GMU registers, indexed-register ascii85 blocks, shader blocks, clusters, DBGAHB clusters, and debugbus blocks. A7xx printers include pipe, cluster, context, location, SPTP, and USPTP metadata from table handles.

## State And Persistence Behavior

Captured state is immutable after `a6xx_gpu_state_get()` returns. Small arrays are owned by `state_kcalloc()` allocations linked on `a6xx_state->objs`; GMU BO snapshots allocate separate `kvzalloc()` buffers and are freed explicitly in `a6xx_gpu_state_destroy()`. The crashdumper BO is temporary and returned with `msm_gem_kernel_put()` after capture. The capture process can temporarily alter hardware debug selectors, SQE state, CP mempool size, debugbus config, A7xx `SP_DBG_CNTL`, and chicken debug bits; functions generally restore modified values where necessary.

## Dependencies And Integration Points

This file depends on `a6xx_gpu.h`, `a6xx_gmu.h`, `a6xx_gpu_state.h`, generated A7xx snapshot headers, register XML, msm GEM helpers, ASCII85 encoding, DRM printers, Adreno core state capture/show, GMU initialization/status helpers, and global debug flags. It integrates with `a6xx_gpu.c` through `gpu_state_get`, `gpu_state_put`, and `show` function-table entries, and with the MMU fault path because SMMU stall state controls crashdumper use.

## Risks And Edge Cases

- Crashdumper cannot run if SPTPRAC is off, GX is off, hardware needs init, or SMMU is stalled. The code falls back to partial AHB capture, so missing sections can be expected in some fault classes.
- The crashdump script uses a fixed 8 KiB script area and data area under 1 MiB. Large table additions must respect `A6XX_CD_DATA_SIZE`.
- Capture halts SQE and toggles debug registers on already-faulted hardware. Bad ordering can worsen hangs or obscure original fault state.
- `state_kmemdup()` stores binary data that printers later interpret using static table handles. Table/data mismatch yields misleading dumps.
- Debugbus capture is optional and invasive; it remaps `cx_dbgc`, reprograms muxes, and can be unavailable on some DTs.
- A7xx family selection uses `BUG_ON()` for unexpected families in several helper paths. New generations must add tables before enabling state capture.

## Test Signals

Validation includes forced GPU hangs producing devcoredumps, SMMU faults producing partial but non-crashing dumps, GMU log/HFI/debug snapshots on full-GMU targets, A7xx dumps showing BR/BV/LPAC metadata, indexed CP mempool data with plausible sizes, debugbus output only when requested, no warnings about data size overflow, and successful `a6xx_gpu_state_put()` without leaks or double frees.
