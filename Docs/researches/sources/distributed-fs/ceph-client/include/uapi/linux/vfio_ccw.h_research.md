# sources/distributed-fs/ceph-client/include/uapi/linux/vfio_ccw.h

Purpose: defines vfio-ccw region layouts for exposing IBM s390 channel-subsystem operations to userspace through VFIO device regions.

Important APIs/types/functions: exports packed structs `ccw_io_region`, `ccw_cmd_region`, `ccw_schib_region`, and `ccw_crw_region`. The I/O region carries ORB, SCSW, IRB byte areas and a return code. The async command region uses `VFIO_CCW_ASYNC_CMD_HSCH` and `VFIO_CCW_ASYNC_CMD_CSCH`. The SCHIB region contains the subchannel-information block captured via `stsch()`. The CRW region returns a Channel Report Word plus padding.

Control flow: userspace discovers vfio-ccw regions through `VFIO_DEVICE_GET_REGION_INFO` and region type/subtype capabilities in `vfio.h`. Writing/reading the I/O region initiates or observes START SUBCHANNEL state. Writing supported commands to the async command region triggers halt or clear subchannel actions when the capability exists. Reading the SCHIB region triggers a hardware `stsch()` collection path. The CRW region is used with the corresponding vfio-ccw interrupt/index support to report channel events.

State and persistence: all state is exchanged through packed region memory backed by the vfio-ccw kernel driver. Return codes communicate the result of the most recent region operation. The header itself stores no state; it fixes byte sizes for hardware-defined areas and therefore must remain ABI-stable.

Dependencies and integration: includes `linux/types.h` and integrates with `vfio.h` CCW region subtypes (`VFIO_REGION_SUBTYPE_CCW_ASYNC_CMD`, `SCHIB`, `CRW`) and IRQ indexes (`VFIO_CCW_IO_IRQ_INDEX`, `VFIO_CCW_CRW_IRQ_INDEX`, `VFIO_CCW_REQ_IRQ_INDEX`). It is specific to s390 channel I/O virtualization.

Risks: region contents are raw hardware ABI blocks, so packing, exact sizes, and byte interpretation matter. Async commands are capability-gated; userspace must not assume the region exists on every vfio-ccw device. Incorrect ORB or command fields can leave subchannels in unexpected states or surface guest-visible I/O errors.

Test signals: vfio-ccw UAPI layout checks, s390 virtualization tests that start/halt/clear subchannels, capability discovery tests for optional regions, SCHIB read tests, CRW interrupt delivery tests, and userspace VMM tests that validate `ret_code` behavior on success and error paths.
