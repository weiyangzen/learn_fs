# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_drv.h

`panthor_drv.h` is a very small shared header currently used to expose the transparent hugepage module parameter.

Its only declaration is `extern bool panthor_transparent_hugepage;`, with the backing definition and module parameter in `panthor_drv.c`. `panthor_gem.c` reads the variable during GEM initialization to decide whether it should try to create and use a DRM hugepage mount.

There is no control flow in the header and no storage owned by it. The persistent runtime state is the module-global parameter value, which affects GEM memory allocation policy for the device lifetime.

Dependencies are minimal: consumers must include it only where they need access to the driver-level option. The main risk is configuration mismatch around `CONFIG_TRANSPARENT_HUGEPAGE`; builds without THP must still compile and avoid relying on unavailable behavior. Test signals are builds with and without THP, booting with `panthor.transparent_hugepage=0`, and GEM init logs showing hugepage use only when enabled.
