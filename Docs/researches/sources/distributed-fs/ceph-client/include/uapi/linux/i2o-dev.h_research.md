<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i2o-dev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/i2o-dev.h

## Purpose
`i2o-dev.h` defines the legacy Intelligent I/O userspace ABI for controller discovery, hardware/resource table reads, parameter set/get, software download/upload/delete, event registration, HTML queries, and raw passthrough messages.

## Important APIs, types, and functions
The ioctl namespace is `I2O_MAGIC_NUMBER`. Ioctls include `I2OGETIOPS`, `I2OHRTGET`, `I2OLCTGET`, `I2OPARMSET`, `I2OPARMGET`, `I2OSWDL`, `I2OSWUL`, `I2OSWDEL`, `I2OVALIDATE`, `I2OHTML`, `I2OEVTREG`, `I2OEVTGET`, `I2OPASSTHRU`, and `I2OPASSTHRU32`. Structures cover passthrough, HRT/LCT commands, parameter set/get, software transfer, HTML, event IDs/info, S/G flags, bus entries (`i2o_pci_bus`, local, ISA, EISA, MCA, other), `i2o_hrt`, `i2o_lct`, `i2o_status_block`, event masks, class/subclass IDs, parameter operations, serial-number formats, adapter states, software module types, and DPT/Adaptec flash constants.

## Control flow
User space opens an I2O control device, enumerates controllers, obtains HRT/LCT topology, reads status, registers for events, manipulates parameter groups, downloads or uploads firmware/software fragments, or sends raw passthrough messages to an IOP.

## State and persistence behavior
Controller topology, LCT change indicators, adapter state, event registrations, software modules, flash fragments, and parameter tables are persistent or semi-persistent IOP/device state. Event queues are bounded by `I2O_EVT_Q_LEN`.

## Dependencies and integration points
It depends on `<linux/ioctl.h>` and `<linux/types.h>`. It integrates with legacy I2O controllers, storage/network class drivers, DPT/Adaptec firmware update tools, and kernel compat ioctl paths.

## Risks and test signals
Risks include obsolete hardware assumptions, raw passthrough privilege hazards, 32-bit pointer compatibility, bitfield layout sensitivity, firmware update failures, bounded event loss, and table-size trust issues. Test signals include ioctl size/compat tests, HRT/LCT dump validation, event queue overflow tests, parameter set/get round trips, safe passthrough rejection, and flash fragment boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i2o-dev.h -->
