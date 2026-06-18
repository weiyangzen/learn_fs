
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cciss_defs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/cciss_defs.h

## Purpose
Defines legacy HP Smart Array/CCISS command, LUN, request, and error-info structures shared by cciss ioctls. It models CISS command status, transfer direction, queue attributes, command type, SCSI-3 addressing, physical/logical device addressing, and sense/error payloads.

## APIs, Control Flow, and State
The header exports status codes such as `CMD_SUCCESS`, target status, underrun/overrun, invalid, protocol/hardware errors, connection loss, abort, timeout, and unabordable states; transfer direction values; tag attributes; command/message type values; aliases for byte/word/dword types; `CISS_MAX_LUN`; and packed/legacy typedefs for `SCSI3Addr_struct`, `PhysDevAddr_struct`, `LogDevAddr_struct`, `LUNAddr_struct`, `RequestBlock_struct`, `MoreErrInfo_struct`, and `ErrorInfo_struct`. There is no active logic. Driver ioctl paths and hardware command submission code fill these structures, and controller/device state persists in the driver and array firmware.

## Dependencies, Integration, Risks, and Tests
Depends on Linux integer types and legacy cciss ABI conventions. Integration points are `cciss_ioctl.h`, Smart Array management utilities, SCSI passthrough, and logical/physical LUN enumeration. Risks include old structure packing assumptions, endian/addressing quirks for multi-level LUNs, fixed sense buffer size, and ABI compatibility with tools for removed or legacy drivers. Test signals include management-tool passthrough tests, structure-size/compat checks, simulated status/error returns, and regression tests against known Smart Array firmware command formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cciss_defs.h -->
