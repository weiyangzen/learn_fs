# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_init.h

## Purpose
`csio_init.h` is the OS-integration header for the CSIostor driver. It exposes module identity strings, FC transport templates, SCSI host/lnode lifecycle helpers, interrupt callback entry points used by the work-request layer, debugfs helpers, and lock-wrapped SCSI request/free-list helpers.

## Important APIs, Types, and Constants
- Module metadata constants: `CSIO_DRV_AUTHOR`, `CSIO_DRV_DESC`, and `CSIO_DRV_VERSION`.
- External FC transport templates: `csio_fc_transport_funcs` and `csio_fc_transport_vport_funcs`.
- Attribute setup: `csio_fchost_attr_init()`.
- INTx work-request callbacks: `csio_scsi_intx_handler()` and `csio_fwevt_intx_handler()`.
- Lnode request control: `csio_lnodes_block_request()`, `csio_lnodes_unblock_request()`, `csio_lnodes_block_by_port()`, and `csio_lnodes_unblock_by_port()`.
- SCSI host lifecycle: `csio_shost_init()`, `csio_shost_exit()`, and `csio_lnodes_exit()`.
- Debugfs memory helper: `csio_add_debugfs_mem()`.
- `csio_ln_to_shost()` converts embedded `struct csio_lnode` hostdata back to `struct Scsi_Host`.
- Lock helpers `csio_get_scsi_ioreq_lock()`, `csio_put_scsi_ioreq_lock()`, `csio_put_scsi_ioreq_list_lock()`, and `csio_put_scsi_ddp_list_lock()` serialize SCSI I/O request and DDP freelist operations.

## Control Flow and State
This header does not own state. It provides inline wrappers used in interrupt and completion paths: request freelist operations lock `scsim->freelist_lock`; DDP list return locks `hw->lock`. SCSI host conversion assumes `struct csio_lnode` is stored in `Scsi_Host.hostdata`.

## Dependencies and Integration Points
It includes Linux PCI, Ethernet, SCSI, SCSI host, and FC transport headers plus `csio_scsi.h`, `csio_lnode.h`, `csio_rnode.h`, and `csio_hw.h`. It is consumed by initialization, interrupt, chip/debugfs, and management code that needs OS-facing lifecycle functions.

## Risks and Edge Cases
- The lock helpers accept `hw` in some cases only to match calling conventions; callers must pass the correct `scsim` for the hardware instance.
- `csio_ln_to_shost()` depends on the exact allocation pattern in `csio_shost_init()`; embedding changes would break conversion.
- The DDP-list helper locks `hw->lock`, while other request-list helpers lock `scsim->freelist_lock`; mixing these in new code can introduce lock-order concerns.

## Test Signals
Compile coverage is important because this header ties many modules together. Runtime signals include successful SCSI host conversion in completion/removal paths, no double-free on ioreq list return, and no lockdep issues in interrupt-context use of the inline helpers.
