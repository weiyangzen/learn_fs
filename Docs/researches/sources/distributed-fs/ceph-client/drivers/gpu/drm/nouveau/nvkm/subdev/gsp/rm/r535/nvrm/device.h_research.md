# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/device.h

Purpose: defines R535 RM device and subdevice allocation classes and payloads.

Important definitions: `NV01_DEVICE_0` is the device class. `NV0080_ALLOC_PARAMETERS` carries device ID, sharing/target handles, flags, internal VA size/start/limit, and VA mode. `NV20_SUBDEVICE_0` is the subdevice class, with `NV2080_ALLOC_PARAMETERS.subDeviceId`.

Control flow and state: the header declares allocation-time parameters for the RM device tree. Once allocated, these handles become parents for controls such as display static info, FBSR, FIFO, GR, VMM, and internal GSP controls.

Dependencies and integration: consumed by RM device constructors and by `gsp->internal.device` static handles populated from `GET_GSP_STATIC_INFO` in `gsp.c`.

Risks and tests: VA sizing and subdevice ID fields must align with RM's expectations, particularly for multi-subdevice or SR-IOV paths. Test signals are successful client-device-subdevice construction and follow-on internal controls through the subdevice object.
