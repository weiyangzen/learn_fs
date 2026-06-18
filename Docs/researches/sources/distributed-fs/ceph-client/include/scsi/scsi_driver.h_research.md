<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_driver.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_driver.h

## Purpose
This header defines the upper-level SCSI driver registration wrapper around the Linux driver model and links `struct scsi_cmnd` commands back to their owning SCSI driver.

## Important APIs, Types, And Functions
`struct scsi_driver` embeds `struct device_driver` and provides callbacks for `probe`, `remove`, `shutdown`, `resume`, `rescan`, command init/uninit, command completion, EH action, and EH reset. Macros convert driver objects and wrap register/unregister calls. `scsi_register_interface()` and `scsi_unregister_interface()` expose class-interface hooks. `scsi_cmd_to_driver()` returns the command device's bound SCSI driver.

## Control Flow
Upper-level drivers register with `scsi_register_driver()`, probe matching `scsi_device` instances, initialize commands before submission, receive `done()` callbacks, and participate in EH-specific actions/resets. Interfaces can subscribe to SCSI class device events independently of a concrete ULD.

## State And Persistence
The only state defined here is driver callback storage in `struct scsi_driver`. Binding state lives in the driver core and `scsi_device::sdev_gendev.driver`.

## Dependencies And Integration Points
It depends on Linux device and block types plus `scsi_cmnd.h`. It integrates SCSI upper-level drivers such as disk/tape/sg with the generic driver model and SCSI command lifecycle.

## Risks
`scsi_cmd_to_driver()` must not be used for passthrough commands without a normal bound SCSI driver. Driver unregister must coordinate with outstanding commands and EH callbacks.

## Test Signals
Register/unregister ULDs, probe/remove devices, command init/uninit pairing, done callback invocation, class-interface registration, and passthrough command paths that avoid `scsi_cmd_to_driver()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_driver.h -->
