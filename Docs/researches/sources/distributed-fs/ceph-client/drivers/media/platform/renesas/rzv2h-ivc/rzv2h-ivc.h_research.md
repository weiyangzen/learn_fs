# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc.h

Purpose: shared private header for the RZ/V2H(P) Input Video Control driver. It centralizes register offsets, bit fields, image limits, format descriptors, pad numbering, the top-level device state, and cross-file function prototypes.

Important APIs and types: defines AXIRX and frame-manager register offsets such as `RZV2H_IVC_REG_AXIRX_PXFMT`, `RZV2H_IVC_REG_AXIRX_SADDL_P0`, `RZV2H_IVC_REG_FM_STOP`, and interrupt bits. `struct rzv2h_ivc_format` ties video fourcc, acceptable media-bus codes, and MIPI datatype. `struct rzv2h_ivc` stores device resources, video device, subdevice, buffer queue state, active format, mutex, and spinlocks.

Control flow role: the header is not executable, but it defines the contract among the platform device, subdevice, and video-node files. Device probe allocates/populates `struct rzv2h_ivc`; subdev setup uses the pad enum and format limits; video streaming uses the register definitions and buffer fields; IRQ handling updates `vvalid_ifp`, completes buffers, and calls transfer helpers.

State and persistence: persistent driver state includes MMIO base, clock/reset arrays sized by `RZV2H_IVC_NUM_HW_RESOURCES`, IRQ number, current V4L2 format, current and queued buffers, and stream sequence. The header's locks document ownership: `buffers.lock` guards queue/current buffer and `spinlock` protects interrupt-facing state.

Dependencies and integration: includes Linux clock/reset/list/mutex/spinlock/workqueue types plus V4L2, media entity, subdev, and vb2 headers. Prototypes connect `rzv2h-ivc-dev.c`, `rzv2h-ivc-subdev.c`, and `rzv2h-ivc-video.c`.

Risks and test signals: changes here have broad ABI-like impact inside the driver. Validate register bit definitions against hardware documentation, ensure new formats keep fourcc/mbus/datatype mappings coherent, and run compile tests for all three translation units after structural changes.
