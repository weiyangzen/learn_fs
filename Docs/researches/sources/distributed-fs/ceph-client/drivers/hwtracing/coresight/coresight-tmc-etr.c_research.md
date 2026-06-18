# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc-etr.c

## Purpose

`coresight-tmc-etr.c` implements the Embedded Trace Router sink side of the Arm CoreSight TMC driver. It allocates trace buffers, programs ETR hardware for circular capture, exposes sysfs and perf sink operations, supports flat, TMC scatter-gather, CATU, and reserved-memory buffer modes, and persists crash trace metadata when reserved crash buffers are configured.

## Important APIs, Types, and Functions

Important internal types are `etr_flat_buf`, `etr_sg_table`, `etr_perf_buffer`, and `etr_buf_hw`. Exported helpers include `tmc_alloc_sg_table`, `tmc_free_sg_table`, `tmc_sg_table_sync_*`, `tmc_sg_table_get_data`, `tmc_etr_get_catu_device`, CATU ops setters, and `tmc_etr_get_buffer`. The central buffer path is `tmc_alloc_etr_buf`, which selects `ETR_MODE_FLAT`, `ETR_MODE_ETR_SG`, `ETR_MODE_CATU`, or `ETR_MODE_RESRV`; each mode supplies `etr_buf_operations` for allocation, sync, data access, and free. Hardware programming is split between `tmc_etr_enable_hw`, `__tmc_etr_enable_hw`, `__tmc_etr_disable_hw`, and `tmc_etr_disable_hw`. User-visible operations are in `tmc_etr_sink_ops`, `tmc_etr_sync_ops`, `tmc_read_prepare_etr`, `tmc_read_unprepare_etr`, and the ETR attribute group.

## Control Flow

Sysfs enable obtains or allocates a persistent `sysfs_buf`, rejects concurrent perf mode, enables hardware, and sets CoreSight mode to `CS_MODE_SYSFS`. Sysfs read preparation stops a running sysfs session, syncs buffer offsets and lengths from RRP/RWP/STS, then marks `reading`; unprepare either restarts tracing or frees the buffer after consumption. Perf allocation creates an `etr_perf_buffer`; CPU-wide sessions share one `etr_buf` through `drvdata->idr` keyed by owner pid, while per-thread sessions allocate independently. Perf enable claims the sink for the pid, enables hardware, and stores `perf_buf`. Perf update flushes/stops the ETR, syncs trace data, trims to AUX space when needed, inserts a CoreSight barrier packet on overflow, copies into perf pages, and may re-enable hardware for active events.

## State and Persistence Behavior

Persistent state lives in `tmc_drvdata`: preferred mode, current hardware `etr_buf`, sysfs/perf buffers, owner pid, IDR, reserved buffer, crash metadata, and mode/refcount state in `csdev`. `etr_buf` carries mode, full flag, hardware address, offset, length, private backend state, and refcount. Reserved mode maps a pre-reserved physical buffer and can survive crashes; `tmc_panic_sync_etr` writes register snapshots, trace address, valid flag, and CRCs into crash metadata.

## Dependencies and Integration Points

The file depends on CoreSight core registration, TMC common helpers from `coresight-tmc.h`, CATU helper ops, perf AUX buffer APIs, DMA/IOMMU APIs, vmalloc page mapping, IDR/mutex/refcount, and crash-data helpers. It integrates with `coresight-tmc-core.c` for common TMC probe data and with CATU through exported operation registration.

## Risks and Edge Cases

Risk concentrates in DMA ownership, circular offset math, and concurrent sysfs/perf transitions. Flat and SG sync paths must map hardware RRP/RWP addresses back to buffer offsets correctly. Perf CPU-wide sharing relies on pid-keyed IDR and refcounts. `tmc_panic_sync_etr` must not claim crash metadata unless reserved mode and metadata buffers are valid. `tmc_update_etr_buffer` re-enables hardware after AUX pause while event state can change.

## Test Signals

Useful signals include sysfs/perf mutual exclusion, all buffer-mode selection paths, fallback from failed large perf buffers to smaller buffers, SG wrap reads, overflow barrier insertion, AUX truncation flags, reserved-mode crash metadata CRC validity, CATU registration/unregistration, and lockdep coverage around `spinlock` plus `idr_mutex`.
