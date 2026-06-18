# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/Makefile

Purpose: declares the object list that composes the `kvmgt` build when `CONFIG_DRM_I915_GVT` is enabled.

Important entries: includes the researched objects `gvt/aperture_gm.o`, `gvt/cfg_space.o`, `gvt/cmd_parser.o`, `gvt/debugfs.o`, `gvt/display.o`, and `gvt/dmabuf.o`, plus EDID, execlist, framebuffer decoder, firmware, GTT, handlers, interrupt, KVMGT, MMIO, opregion, page tracking, scheduler, trace points, and vGPU core objects.

Control flow and state: no runtime control flow. The build system appends these objects to `kvmgt-$(CONFIG_DRM_I915_GVT)`, determining which translation units participate in the GVT device implementation.

Dependencies and integration points: integrates with the kernel Kbuild infrastructure and the surrounding i915 driver build. Object ordering matters mainly for link inclusion, not initialization order, which is controlled by C code.

Risks and test signals: missing objects produce unresolved symbols for GVT entry points; extra objects can pull unsupported code into configurations. Test signals are successful `CONFIG_DRM_I915_GVT=y/m` builds and absence of unresolved references for vGPU resource, config, command parser, debugfs, display, and DMA-BUF APIs.
