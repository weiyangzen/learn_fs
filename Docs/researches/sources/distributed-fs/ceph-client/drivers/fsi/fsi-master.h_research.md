<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master.h -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-master.h

## Purpose
`fsi-master.h` defines the contract between the FSI core and hardware-specific FSI masters. It also centralizes common FSI master register offsets, register bitfields, hub address geometry, protocol timing constants, command/response encodings, retry limits, and master lifecycle APIs.

## Important APIs, types, and functions
The central type is `struct fsi_master`, which embeds a `struct device`, master index, link count, flags, `scan_lock`, and callbacks for read, write, term, send_break, link_enable, and link_config. Public functions are `fsi_master_register()`, `fsi_master_unregister()`, and `fsi_master_rescan()`. Constants include `FSI_MMODE`, `FSI_MRESP0`, `FSI_MRESB0`, command opcodes like `FSI_CMD_ABS_AR`, response tags like `FSI_RESP_ACK`, and `FSI_MASTER_FLAG_SWCLOCK`.

## Control flow
The header itself has no executable flow. Hardware masters populate a `struct fsi_master`, set callbacks and device release behavior, then hand it to the core. The core invokes callbacks during scan, read/write, error recovery, link enable/disable, delay configuration, TERM, and BREAK.

## State and persistence behavior
It defines runtime structures and register constants only. Master lifetime comments document that registration takes ownership of `master->dev` and that implementations may need an extra reference if remove paths need to access the object after unregister.

## Dependencies and integration points
It depends on device and mutex APIs. All FSI master drivers in this subset include it, and `fsi-core.c` uses it as the core-to-master ABI.

## Risks and edge cases
The lifetime rules are easy to get wrong because `fsi_master_unregister()` can drop the final device reference. Register constants are shared by hardware and hub masters, so incorrect bit definitions affect multiple drivers. Protocol retry constants influence GPIO and ColdFire behavior.

## Test signals
Build coverage of all masters, registration/unregistration lifetime tests, scan/rescan flows, and callback invocation under error recovery validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master.h -->
