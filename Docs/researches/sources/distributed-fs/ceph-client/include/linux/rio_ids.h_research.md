# sources/distributed-fs/ceph-client/include/linux/rio_ids.h

Purpose: this header provides RapidIO vendor and device ID constants, currently for IDT RapidIO switches/devices.

Important APIs/types/functions: constants include `RIO_VID_IDT` and `RIO_DID_IDT70K200`, `RIO_DID_IDTCPS8/12/16/6Q/10Q/1848/1432/1616`, `RIO_DID_IDTVPS1616`, `RIO_DID_IDTSPS1616`, and `RIO_DID_IDTRXS1632/2448`. There are no functions or structs.

Control flow: RapidIO drivers and ID tables use these constants with `RIO_DEVICE()` or `struct rio_device_id` matching to bind supported hardware.

State and persistence: no state. The constants are stable hardware identifiers.

Dependencies and integration points: integrates with RapidIO driver ID tables, module autoloading, and device enumeration that reads RapidIO identity CARs.

Risks: wrong IDs prevent driver binding or bind a driver to unsupported silicon. Test signals include modalias/module autoload matching, enumeration of IDT devices, and driver ID table coverage.
