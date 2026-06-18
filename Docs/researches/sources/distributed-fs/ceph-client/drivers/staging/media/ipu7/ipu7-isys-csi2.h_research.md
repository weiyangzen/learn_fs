# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi2.h

## Purpose
Declares the CSI-2 receiver object and public CSI2 helper API for the IPU7 ISYS driver. It is the shared contract between CSI2 subdevice setup, video stream preparation, and top-level ISYS interrupt handling.

## Important APIs, Types, and Constants
Constants describe media topology limits: `IPU7_NR_OF_CSI2_VC` is 16, `IPU7_NR_OF_CSI2_SINK_PADS` is 1, `IPU7_NR_OF_CSI2_SRC_PADS` is 8, and `IPU7_CSI2_PAD_SINK`/`IPU7_CSI2_PAD_SRC` identify pad numbering. `INVALID_VC_ID` is used during stream initialization. `struct ipu7_isys_csi2` embeds the generic `ipu7_isys_subdev`, backpointers to platform and ISYS state, eight capture video nodes, MMIO base, receiver error accumulator, legacy IRQ mask, lane count, port number, PHY mode, and active stream count. Conversion macros `ipu7_isys_subdev_to_csi2()` and `to_ipu7_isys_csi2()` are used throughout the stream and ISR paths.

## Control Flow and State
The header does not execute code, but its fields are mutated by `ipu7_isys_csi2_init()`, async sensor binding, stream enable/disable, CSI PHY helpers, and ISRs. `stream_count` gates physical receiver power, `receiver_errors` accumulates legacy error bits until `ipu7_isys_csi2_error()` logs and clears them, and `legacy_irq_mask` maps top-level CSI IRQ status to this receiver instance.

## Dependencies and Integration Points
Includes `ipu7-isys-subdev.h` and `ipu7-isys-video.h`, so it couples CSI receivers to both V4L2 subdev state and capture queues. Exported APIs are consumed by `ipu7-isys.c`, `ipu7-isys-video.c`, and `ipu7-isys-queue.c` indirectly through stream setup.

## Risks and Test Signals
The object owns both subdevice and video-node arrays, so lifetime ordering matters: video cleanup and CSI subdev cleanup must not run while queued stream references remain. The VC limit must match remote CSI descriptors and firmware ABI expectations. Test signals include correct eight capture nodes per port, no stale `stream_count` after failed enable, valid VC rejection for `vc >= 16`, and clean cleanup after partial registration failures.
