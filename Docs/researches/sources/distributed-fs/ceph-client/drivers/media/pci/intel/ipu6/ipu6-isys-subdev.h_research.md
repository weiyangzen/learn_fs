# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-subdev.h

## Purpose
This header declares the common IPU6 ISYS subdevice wrapper and helper API used by CSI-2 receiver subdevices and video setup code.

## Important APIs, Types, And Data
`struct ipu6_isys_subdev` embeds a `v4l2_subdev`, back-pointer to `struct ipu6_isys`, supported media-bus code table, pad array, optional control handler, optional `ctrl_init` callback, and `source` identifier used for firmware stream source selection. Conversion macros include `to_ipu6_isys_subdev()`.

Declared helpers cover media-bus depth and MIPI data type mapping, Bayer detection/order conversion, common set-format and enum-code ops, source-stream lookup by source pad, routing updates, and lifecycle init/cleanup.

## Control Flow
Callers initialize the wrapper with `ipu6_isys_subdev_init()`, providing subdev ops, expected controls, and sink/source pad counts. The subdevice then participates in V4L2 routing and stream enable/disable flows used by ISYS capture.

## State And Persistence
The header-defined state is per-device and per-subdevice only. `source` is initialized by implementation code and later read during stream preparation; no file or firmware persistence is represented here.

## Dependencies And Integration Points
It depends on V4L2 controls/subdevs and media entities. It is part of the internal contract between the ISYS core, CSI-2 receiver implementation, and video-node setup.

## Risks And Test Signals
The `supported_codes` pointer is expected to be a zero-terminated array. Bad table termination would cause enumeration and format matching to walk past bounds. Tests should cover subdevice init failure unwinding, pad flags for sink/source counts, and source-stream lookup after routing changes.
