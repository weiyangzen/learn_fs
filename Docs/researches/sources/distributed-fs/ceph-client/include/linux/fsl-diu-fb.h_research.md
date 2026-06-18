# sources/distributed-fs/ceph-client/include/linux/fsl-diu-fb.h

Purpose: defines the userspace ioctl ABI and kernel register/descriptor layouts for the Freescale Display Interface Unit framebuffer driver.

Important APIs and types: userspace structs `mfb_chroma_key` and `aoi_display_offset` support chroma-key and area-of-interest offset ioctls. `MFB_SET_*` and `MFB_GET_*` ioctl constants control alpha, brightness, chroma key, AOI display position, pixel format, and legacy MPC5121 gamma. Backward-compatible old pixel-format ioctl numbers are retained. Kernel-only `struct diu_ad` describes packed DDR area descriptors for display planes, and `struct diu` maps DIU registers. `MFB_MODE0` and `MFB_MODE1` define supported display modes.

Control flow: framebuffer ioctl handlers copy userspace structs, update software state, and program DIU descriptors/registers. Display enable uses descriptor addresses and register fields to configure planes, palette/gamma/cursor/background, display size, sync parameters, interrupts, and color bars.

State and persistence: ioctl settings and descriptors are runtime display state, not persistent storage. Descriptor layout is hardware ABI in DMA-visible memory and must match endian/packing requirements.

Dependencies and integration points: depends on Linux ioctl/type definitions and integrates with the DIU framebuffer driver, platform device setup, user framebuffer utilities, and hardware display timing code.

Risks and test signals: risks include ioctl ABI collisions (`MFB_SET_CHROMA_KEY` and legacy gamma share numbers with different payloads), packed descriptor endian mistakes, old pixel-format compatibility, and programming unsupported modes. Tests should cover all ioctls, legacy ioctl numbers, descriptor DMA layout, endian platforms, suspend/resume display restore, and invalid AOI/pixfmt inputs.
