# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_csi2.c

## Purpose
This file implements AtomISP MIPI CSI-2 V4L2 subdevice entities and ISP2401 receiver timing setup. Each CSI2 port bridges camera sensors to the Atom ISP processing subdev.

## Important APIs and Functions
`atomisp_csi2_set_ffmt()` validates/clamps media-bus formats and mirrors sink to source. V4L2 pad ops enumerate, get, and set formats. `mipi_csi2_init_entities()` initializes subdevs, pads, media entity function, and default formats. Register/unregister helpers attach CSI2 subdevs to the V4L2 device. `atomisp_csi2_configure()` programs ISP2401 CSI receiver timing from sensor link frequency.

## Control Flow
`atomisp_mipi_csi2_init()` first runs `atomisp_csi2_bridge_init()`, then initializes every `isp->csi2_port[]`. Sink pad format setting resolves the requested code through `atomisp_find_in_fmt_conv()`, clamps dimensions, stores field information, and recursively updates the source pad. Stream start calls `atomisp_csi2_configure()`, which computes lane delay counters and writes CSI2 registers through CSS MMIO helpers.

## State and Persistence
Each `atomisp_mipi_csi2_device` stores active formats for sink/source pads and an AtomISP back-pointer. Try formats are V4L2 subdev state. Programmed receiver timing persists in hardware until changed/reset.

## Dependencies and Integration Points
Depends on format conversion from `atomisp_subdev.c`, internals for hardware revision and input state, register definitions, and `atomisp_css2_hw_store_32()`. It sits between sensor subdevs and the ISP media entity.

## Risks
DPCM decompression is not implemented; source always mirrors sink. Receiver configuration assumes valid current input, sensor control handler, and port. Missing `V4L2_CID_LINK_FREQ` falls back to default timing. Port/lane tables are fixed to known hardware.

## Test Signals
Enumerate mbus codes, set active/try pad formats, validate media links, stream on ISP2401 sensors with and without link-frequency controls, and trace CSI2 timing register writes.
