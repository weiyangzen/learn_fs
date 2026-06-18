<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_driver.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_driver.h

Purpose: defines the EFCT driver's shared top-level device structure, constants, interrupt context, firmware-write result container, includes, and external device-list declaration used by the EFCT PCI/target stack.

Important APIs/types/functions: key constants include `EFCT_DRIVER_NAME`, `EFCT_DRIVER_VERSION`, `EFCT_DEFAULT_FILTER`, `EFCT_OS_MAX_ISR_TIME_MSEC`, FC SG/DIF limits, watermark defaults, `EFCT_PCI_MAX_REGS`, `MAX_PCI_INTERRUPTS`, and `FW_WRITE_BUFSIZE`. `struct efct_intr_context` links an interrupt vector index to an `efct` device. `struct efct` stores PCI/BAR/MSI-X state, target transport state, libefc pointer, SCSI host pointer, hardware object, filter/topology, node lookup xarray, timers/debug fields, and runtime policy values. `struct efct_fw_write_result` bridges asynchronous firmware-write callbacks to synchronous waits.

Control flow: the header has no direct runtime flow. Its fields are populated during PCI probe and device attach, consumed by interrupt handlers, xport/libefc/hardware code, firmware update paths, and cleanup routines.

State and persistence: `struct efct` is the main in-memory state container for each adapter. It does not itself persist state, but includes fields controlling firmware upgrade requests and target I/O behavior. `efct_fw_write_result` carries transient completion state for one firmware write operation.

Dependencies and integration: includes Linux module/debugfs/firmware headers, common EFC definitions, libefc, and local `efct_hw`, `efct_io`, and `efct_xport` contracts. The external `efct_devices` list is defined in `efct_driver.c` and provides global device enumeration within the driver.

Risks: this structure is shared across many EFCT objects, so field lifetime and ownership must match attach/detach ordering. Fixed interrupt and BAR array sizes must stay aligned with hardware setup. Watermark and SGL constants affect I/O throttling and target resource sizing elsewhere in the module.

Test signals: compile coverage across all `efct-objs`, probe-time initialization of every required field, interrupt context indexing, firmware write completion, target session creation, teardown after partial attach failure, and static analysis for structure ownership and bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_driver.h -->
