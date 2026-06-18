# sources/distributed-fs/ceph-client/include/linux/rpmsg/qcom_smd.h

## Purpose
`qcom_smd.h` declares the Qualcomm Shared Memory Driver rpmsg edge interface.

## Important APIs, types, and functions
The header forward-declares `struct qcom_smd_edge` and exposes `qcom_smd_register_edge()` and `qcom_smd_unregister_edge()` when `CONFIG_RPMSG_QCOM_SMD` is enabled, with stubbed fallbacks otherwise.

## Control flow, state, and persistence
Qualcomm SMD transport probe registers an SMD edge, which lets rpmsg clients bind to SMD channels. Unregistration removes the edge and associated channel devices. Runtime state persists in SMD edge/channel objects owned by the transport.

## Dependencies and integration points
It depends on the device model and Qualcomm SMD rpmsg support. Integration points include legacy Qualcomm remote processors, shared-memory channel discovery, subsystem restart, and rpmsg client drivers.

## Risks and test signals
Risks include channel teardown while clients still hold endpoints, missing cleanup on remote crash, and disabled-config callers not checking returned pointers. Test signals include SMD channel discovery, client probe/remove, message loopback, remote restart cleanup, and disabled Kconfig builds.
