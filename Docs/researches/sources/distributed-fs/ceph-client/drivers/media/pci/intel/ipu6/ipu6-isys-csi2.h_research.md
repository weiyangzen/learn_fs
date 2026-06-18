# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-csi2.h

## Purpose
This header declares the CSI-2 receiver data structures, pad/VC constants, timing coefficients, error descriptor type, and public CSI-2 helper APIs for IPU6 ISYS.

## Important APIs, types, and definitions
Constants define 16 virtual channels, one sink pad, eight source pads, invalid VC marker, and timing coefficients for clock/data terminate and settle registers. `struct ipu6_isys_csi2` stores the subdevice, ISYS pointer, output video objects, MMIO base, accumulated receiver errors, lane count, and port. `struct ipu6_isys_csi2_timing` carries calculated timing values. APIs cover init/cleanup, link-frequency lookup, SOF/EOF event reporting, receiver error registration/logging, and remote frame descriptor retrieval.

## Control flow and integration points
ISYS core allocates one of these structures per CSI-2 port and registers it as a V4L2 subdevice. Queue/video stream setup uses these APIs to resolve CSI-2 descriptors and generate frame events. PHY drivers consume the config/timing data passed from CSI-2 stream enable paths.

## State, persistence, and dependencies
State persists for each registered CSI-2 subdevice lifetime. The header depends on IPU6 ISYS subdev/video headers and media/V4L2 frame descriptor forward declarations.

## Risks and test signals
Risks are pad-count assumptions, VC range mismatches, timing coefficient drift, and stale structure fields after cleanup. Test signals include subdevice registration for all ports, media routing across eight source pads, frame descriptor VC validation, and stream events tied to correct CSI port and stream.
