## sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_ioctlP.h

Purpose: private ioctl prototype header for Armada GEM userspace entry points. It keeps the driver ioctl table and GEM implementation files sharing one declaration style.

Important API is `ARMADA_IOCTL_PROTO(name)`, which declares `armada_gem_create_ioctl`, `armada_gem_mmap_ioctl`, and `armada_gem_pwrite_ioctl` with the DRM ioctl signature `(struct drm_device *, void *, struct drm_file *)`. The file has no state or control flow.

Dependencies are DRM core types and the implementations in the GEM code plus registration in the Armada DRM driver. Integration risk is mostly ABI wiring: mismatched prototypes or removed declarations break ioctl table compilation, while semantic bugs live in the implementation files. Test signals are successful module build, ioctl registration, GEM buffer creation/mmap/pwrite behavior, and userspace exercising the Armada DRM UAPI without `-ENOTTY` or argument decoding failures.
