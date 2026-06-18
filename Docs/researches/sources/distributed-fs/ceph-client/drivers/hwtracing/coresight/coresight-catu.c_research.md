# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-catu.c

## Purpose
`coresight-catu.c` implements the Arm CoreSight CATU, a helper device that lets a TMC-ETR sink consume a scatter-gather trace buffer through a CATU translation table. Its main roles are to build CATU-compatible 4 KiB translation-table pages over TMC scatter-gather pages, register CATU-backed `etr_buf_operations`, and program the CATU into either translate or pass-through mode when a CoreSight trace path is enabled.

## Important APIs, Types, And Functions
The file-private `struct catu_etr_buf` stores the allocated `tmc_sg_table` and table base DMA address (`sladdr`) attached to an `etr_buf`. `catu_get_table()` maps a trace-buffer offset to the CATU table page and optionally returns the DMA address of that table. `catu_populate_table()` fills all data-page entries and previous/next table links. `catu_init_sg_table()` allocates the TMC scatter-gather table and populates it.

The ETR buffer operations are `catu_alloc_etr_buf()`, `catu_free_etr_buf()`, `catu_sync_etr_buf()`, and `catu_get_data_etr_buf()`, exported to TMC through `tmc_etr_set_catu_ops()`. The CoreSight helper callbacks are `catu_enable()` and `catu_disable()`, backed by `catu_enable_hw()` and `catu_disable_hw()`. Probe is shared between AMBA and ACPI/platform entry points via `__catu_probe()`.

## Control Flow
Module init registers both AMBA and platform drivers, then installs CATU ETR buffer ops. Probe enables CoreSight clocks, maps registers, derives a DMA mask from `CORESIGHT_DEVID`, loads CoreSight platform topology, clears stale self-claim tags, and registers a helper device with subtype `CORESIGHT_DEV_SUBTYPE_HELPER_CATU`.

When the TMC layer allocates an ETR buffer in CATU mode, `catu_alloc_etr_buf()` finds the CATU helper attached to the TMC, allocates the CATU private buffer, creates CATU tables, marks the `etr_buf` as `ETR_MODE_CATU`, and uses `CATU_DEFAULT_INADDR` as the synthetic ETR input address. On path enable, `catu_enable_hw()` waits for READY, claims the device, finds the upstream sysmem ETR, and asks it for the active buffer. If the ETR buffer is CATU-backed, CATU is programmed with `CATU_MODE_TRANSLATE`, `CATU_OS_AXICTRL`, `SLADDR`, and `INADDR`; otherwise it is programmed in pass-through mode. Disable clears CONTROL, disclaims the device, and waits for READY again.

## State And Persistence
Runtime state is in `struct catu_drvdata`: clock handles, MMIO base, CoreSight device, IRQ number, and a raw spinlock. Enable state is tracked through `csdev->refcnt`; hardware is only programmed for the first enable and only disabled on the final disable. CATU table/data state lives in TMC-owned `tmc_sg_table` objects attached to `etr_buf->private` and is freed through the ETR buffer operation. Trace-buffer read state (`etr_buf->offset` and `etr_buf->len`) is recomputed in `catu_sync_etr_buf()` from hardware RRP/RWP values.

## Dependencies And Integration Points
The driver depends on CoreSight helper-device registration, TMC ETR scatter-gather helpers, DMA mapping, runtime PM, AMBA discovery, and ACPI/platform discovery. It integrates with path enable/disable through CoreSight helper ops and with the TMC ETR allocation path through `tmc_etr_set_catu_ops()`. Management attributes expose CATU registers under a `mgmt` sysfs group.

## Risks
The table generator assumes CATU 4 KiB table/data pages and a 1 MiB addressable range per CATU table. Incorrect buffer sizing, page alignment, or table-link programming would corrupt trace capture. `catu_enable_hw()` claims the CATU before `tmc_etr_get_buffer()` returns; the error path returns directly if that call fails, which is worth checking against claim-leak expectations. `catu_sync_etr_buf()` subtracts hardware addresses from `etr_buf->hwaddr`; invalid RRP/RWP values could produce bogus offsets. DMA mask derivation defaults unknown hardware to 40 bits, which is pragmatic for TMC-ETR but may hide unusual platform constraints.

## Test Signals
Useful validation includes CATU probe on AMBA and ACPI/platform systems, sysfs `mgmt` register reads, ETR allocation with and without CATU, wrap-around trace-buffer sync, trace extraction through `tmc_sg_table_get_data()`, runtime PM suspend/resume, and failure injection for SG allocation and `tmc_etr_get_buffer()`. Hardware tests should verify translate mode actually maps discontinuous pages and pass-through mode still allows non-CATU ETR operation.
