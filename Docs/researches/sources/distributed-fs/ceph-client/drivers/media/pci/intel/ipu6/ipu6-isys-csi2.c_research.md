# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-csi2.c

## Purpose
This file implements IPU6 ISYS CSI-2 receiver subdevices. It handles supported media-bus formats, CSI-2 timing calculation from sensor link frequency, receiver error capture/logging, stream enable/disable with PHY power, crop/format subdev operations, SOF/EOF event reporting, and remote CSI-2 frame descriptor lookup.

## Important APIs, types, and functions
`csi2_supported_codes[]` lists accepted media-bus formats. `ipu6_isys_csi2_get_link_freq()` queries the remote sensor. `ipu6_isys_csi2_calc_timing()` computes clock/data terminate and settle values. `ipu6_isys_csi2_set_stream()` programs CSI FE/PPI/IRQ registers and calls `isys->phy_set_power()`. Pad operations include `ipu6_isys_csi2_enable_streams()`, `ipu6_isys_csi2_disable_streams()`, `ipu6_isys_csi2_set_sel()`, and `ipu6_isys_csi2_get_sel()`. `ipu6_isys_csi2_init()` registers the subdevice. `ipu6_isys_register_errors()` and `ipu6_isys_csi2_error()` collect/log receiver errors. `ipu6_isys_csi2_get_remote_desc()` reads upstream frame descriptors.

## Control flow and integration points
When streams are enabled, the code translates source-pad stream masks to sink streams, calculates timing, enables receiver hardware, powers the selected PHY, and then enables the remote sensor/subdev stream. Disable reverses hardware and remote streaming. Crop operations support source-pad vertical cropping and adjust Bayer order when needed. Firmware response handling in other ISYS files calls SOF/EOF event helpers and remote descriptor lookup to route streams and virtual channels.

## State, persistence, and dependencies
Persistent state is `struct ipu6_isys_csi2`: embedded ISYS subdev, ISYS pointer, video outputs, base MMIO, receiver error bitfield, lane count, and port. Dependencies include media controller routing/streams API, V4L2 controls/events/subdev state, platform CSI register definitions, ISYS subdev helpers, and platform-specific PHY callbacks.

## Risks and test signals
Risks are link-frequency errors, invalid lane/port combinations, stream mask translation mistakes, IRQ mask/clear ordering, duplicate or missing sensor stream toggles, incorrect Bayer crop conversion, and receiver errors lost when IRQs are disabled. Test signals include media graph format/routing validation, stream enable/disable on every CSI port, SOF events, remote frame descriptor VC matching, receiver error logging under injected CSI faults, and no PHY power failures.
