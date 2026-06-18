# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_sas.h

## Purpose

`pm8001_sas.h` is the central shared contract header for the PM8001/PM80xx SAS/SATA driver. It defines the driver name/version, logging masks, hardware dispatch interface, chip metadata, HBA/PHY/port/device/CCB/queue structures, DMA memory descriptors, firmware/NVMD/flash/forensic payload structures, device-state constants, external globals, function prototypes, and inline CCB allocation/free helpers.

The header is the glue between common libsas-facing code, PCI/module initialization, chip-specific hardware implementation, MPI response handling, sysfs/ctl support, firmware update support, and diagnostic dump support. Its structure layouts are both kernel-internal APIs and firmware/hardware-facing ABI descriptions for DMA rings, config tables, status tables, and PRDs.

## Important APIs, Types, and Constants

Top-level constants are `DRV_NAME` (`pm80xx`), `DRV_VERSION`, logging masks (`PM8001_FAIL_LOGGING` through `PM8001_EVENT_LOGGING`), `IS_SPCV_12G`, `PM8001_NAME_LENGTH`, and `PM8001_INVALID_TAG`. `pm8001_info` and `pm8001_dbg` standardize logging and use `pm8001_hba_info->logging_level` to gate debug categories.

`struct pm8001_dispatch` is the most important API in the header. It is the per-chip operations table used through `PM8001_CHIP_DISP`. It contains chip lifecycle hooks, BAR mapping/unmapping hooks, ISR and interrupt-control hooks, command builders for SMP/SSP/SATA/TMF/abort, PHY control and device register/deregister hooks, NVMD/flash hooks, device-state and SAS diagnostic hooks, SAS reinit, fatal-error detection, and hardware-event ACK.

Core topology/runtime structures are:

- `struct pm8001_chip_info`: encryption support flag, number of phys, and dispatch table pointer.
- `struct pm8001_port`: embedded `asd_sas_port`, attachment state, wide-port PHY map, port state/id, and list linkage.
- `struct pm8001_phy`: back-pointer to HBA, port pointer, embedded `asd_sas_phy`, SAS identity, optional SCSI device pointer, SAS address, PHY type/state, enable/reset completion pointers, received frame buffer, attached flag, link-rate bounds, reset status, and reset success.
- `struct pm8001_device`: libsas device type and `domain_device` pointer, attached PHY, local slot id, discovery and set-device-state completions, firmware device ID, and atomic running request count.
- `struct pm8001_ccb_info`: live `sas_task`, SG element count, CCB tag, PRD DMA handle, device pointer, PRD buffer, firmware-control context, and open-retry flag.
- `struct pm8001_hba_info`: the full HBA state object tying together PCI/device pointers, BARs, coherent memory map, encryption/forensic state, firmware tables, MPI queues, PHY attributes, SAS/libsas/SCSI state, chip identity, completions, tag bitmap, phys/ports, device and CCB arrays, IRQ/tasklet metadata, logging/link-rate settings, fatal/non-fatal status, queue counts, offsets, and IOP log tracking.

DMA and firmware-table structures include `pm8001_prd`, `pm8001_prd_imt`, `mpi_mem`, `mpi_mem_req`, `inbound_queue_table`, `outbound_queue_table`, `pm8001_hba_memspace`, `union main_cfg_table`, `union general_status_table`, and `sas_phy_attribute_table`. These encode PRDs, coherent memory regions, queue base/index metadata, BAR mappings, firmware main config table variants for SPC and PM80xx, and general status table variants.

Diagnostic and maintenance structures include `pm8001_ioctl_payload`, `forensic_data`, fatal-dump table offsets/status values, `fatal_error_reporter`, `pm8001_work`, `pm8001_fw_image_header`, `fw_flash_updata_info`, `fw_control_info`, and `fw_control_ex`. Device-state constants define firmware states such as `DS_OPERATIONAL`, `DS_IN_RECOVERY`, and `DS_NON_OPERATIONAL`; flash update status constants describe firmware update results.

Function prototypes expose the cross-file driver API: tag management, CCB/task cleanup, PHY control, scan callbacks, task queue/abort/reset/query, device found/gone, open-reject retry, memory allocation, chip/NVMD/flash/MPI helpers, event and response handlers, BAR shifting, PHY profile setup, dump accessors, fatal-error signaling, sysfs attribute groups, and diagnostics.

The inline helpers `pm8001_ccb_alloc`, `pm8001_ccb_free`, and `pm8001_ccb_task_free_done` are key shared behavior. Allocation chooses either a blk-mq/libsas request tag offset by `PM8001_RESERVE_SLOT` or a reserved low tag, initializes the matching `ccb_info[]` entry, and records task/device context. Freeing clears fields so manual scans can detect inactive CCBs, then frees low reserved tags when applicable. `_done` frees task resources and calls `task_done` after a memory barrier.

## Control Flow and Integration

This header does not run control flow directly, but it defines the data and callbacks that all runtime paths use:

1. `pm8001_init.c` selects a `pm8001_chip_info`, stores it in `pm8001_hba_info`, and uses `PM8001_CHIP_DISP` for chip init, reset, ISR, interrupt enable/disable, NVMD reads, PHY starts, and profile setup.
2. `pm8001_sas.c` uses the same dispatch table to build and send SMP/SSP/SATA/TMF/internal-abort commands, control phys, register/deregister devices, and change firmware device state.
3. Hardware-specific files implement the dispatch functions and consume `pm8001_hba_info`, `inbound_queue_table`, `outbound_queue_table`, `main_cfg_tbl`, `gs_tbl`, CCBs, PRDs, and device records to construct and process MPI messages.
4. MPI response/event files use the prototypes and structure fields to complete commands, update device IDs, complete discovery and reset completions, handle fatal/non-fatal dumps, and free CCBs.
5. sysfs/ctl paths use host/sdev attribute groups, firmware-control structures, dump functions, and NVMD/flash request prototypes.

The CCB inline flow is especially important. A submitted `sas_task` maps to one `ccb_info[tag]`; the tag comes from blk-mq when available or from the reserved bitmap for internal work. The chip-specific request builder receives the CCB and uses its task, device, PRD buffer, and tag to build firmware commands. Completion handlers free the CCB and call the task callback through the helpers.

## State and Persistence Behavior

`pm8001_sas.h` defines volatile in-memory state; it does not persist state itself. Some structures describe hardware or firmware state that may be persistent or long-lived outside the driver:

- `main_cfg_tbl`, `general_status_table`, queue tables, and PRDs mirror firmware-visible DMA/BAR state.
- `pm8001_ioctl_payload`, `fw_control_ex`, and flash/NVMD prototypes represent requests that may read or modify controller nonvolatile memory or firmware images.
- Fatal/non-fatal forensic fields in `pm8001_hba_info` track dump progress, offsets, preserved transfer counts, and fatal table BAR/shift data.
- `pm8001_device->device_id` is assigned by firmware during registration and remains valid until deregistration.

State ownership conventions are encoded in the structures. `pm8001_hba_info->lock` is the host-wide lock for CCB/device/port operations, while `bitmap_lock` protects reserved tags. `running_req` is atomic because command completion and removal/error-recovery paths coordinate on it. Completion pointers in `pm8001_phy`, `pm8001_device`, and `pm8001_hba_info` are borrowed pointers to stack or caller-owned completions, so users must set/clear them carefully around waits.

The layout of many structures is ABI-sensitive. `pm8001_prd` is explicitly packed, firmware image headers are packed/aligned, endian annotations are used in PRDs and queue indices, and main/general table unions preserve different SPC and PM80xx layouts. Changes to these fields can break firmware communication even if C code still compiles.

## Dependencies and External Contracts

The header includes kernel primitives (`spinlock`, `delay`, DMA mapping, PCI, interrupt, workqueue, atomics, blk-mq) and SCSI/SAS interfaces (`libsas`, `scsi_tcq`, `sas_ata`). It includes `pm8001_defs.h` for array sizes, memory-region indices, queue limits, link-rate constants, chip enums, and other hardware constants.

External symbols declared here are defined across the driver:

- `pm8001_8001_dispatch` and `pm8001_80xx_dispatch` in chip-specific implementations.
- `pm8001_wq`, `hba_list`, `pm8001_use_msix`, and `pcs_event_log_severity` in init/common code.
- MPI builders, response handlers, event handlers, BAR shift helpers, PHY profile helpers, fatal dump functions, and sysfs attribute groups in companion pm8001/pm80xx files.

The libsas contract is represented by prototypes for `pm8001_queue_command`, `pm8001_dev_found`, `pm8001_dev_gone`, `pm8001_phy_control`, scan callbacks, and error recovery functions. The firmware contract is represented by dispatch callbacks, queue table structures, config/status table layouts, PRDs, NVMD/flash control structures, and dump/forensic definitions.

## Risks and Edge Cases

Because this header centralizes shared structure definitions, small changes can have broad effects. Reordering or resizing fields in firmware-visible structs, changing packing/alignment, or altering endian types can corrupt DMA communication. Even purely internal fields such as `ccb_tag`, `device`, completion pointers, and `running_req` are used by multiple files and concurrency contexts.

The CCB inline allocator assumes `ccb_info` is large enough for either `rq->tag + PM8001_RESERVE_SLOT` or a reserved low tag. That relies on `pm8001_init_ccb_tag` sizing `shost->can_queue`, host tagset behavior, and firmware `max_out_io` consistently. Any mismatch can produce out-of-bounds CCB access.

`pm8001_ccb_free` always calls `pm8001_tag_free`, but `pm8001_tag_free` ignores tags at or above `PM8001_RESERVE_SLOT`. This split is intentional; callers must not separately release request tags through the reserved bitmap. Active CCB detection depends on `ccb_tag == PM8001_INVALID_TAG`, so all completion and abort paths must use the common free helpers or maintain the same cleanup convention.

Completion pointer fields are non-owning and can point at stack completions in caller functions. Late firmware responses after timeout or teardown can complete stale pointers unless timeout paths clear them. The header cannot enforce this; users of `enable_completion`, `reset_completion`, `dcompletion`, `setds_completion`, and `nvmd_completion` must be audited together with response handlers.

`pm8001_hba_info` mixes many concerns: PCI/BAR state, DMA memory, firmware tables, topology, command slots, interrupts, error dumps, queue offsets, and logging. That breadth makes it easy for cross-file changes to introduce hidden dependencies. Locking rules are mostly conventional rather than encoded in type boundaries.

## Test Signals

Compile-time test signals include sparse/endian checking, structure packing/size checks where available, and warnings from all files that include the header. Runtime validation should focus on the contracts encoded here: CCB allocation/free under normal I/O and internal aborts, reserved-tag exhaustion, blk-mq tag offsets, device registration IDs, queue table setup, PRD DMA correctness, and firmware table decoding for both SPC and PM80xx layouts.

Fault injection should target allocation failures for `ccb_info`, PRD buffers, device arrays, and coherent queue regions; firmware response loss for every completion pointer type; and fatal-error transitions while requests are active. DMA API debug, KASAN, KCSAN, lockdep, and tracing are useful because the header-defined objects are shared by interrupt handlers, tasklets, workqueue work, SCSI callbacks, and libsas error recovery.

Hardware coverage should include `chip_8001` and newer PM80xx/SPCv devices, MSI-X and INTx modes, request-backed SCSI I/O and reserved-tag internal commands, NVMD/flash operations, fatal/non-fatal dump retrieval, and sysfs host/sdev attribute access through `pm8001_host_groups` and `pm8001_sdev_groups`.
