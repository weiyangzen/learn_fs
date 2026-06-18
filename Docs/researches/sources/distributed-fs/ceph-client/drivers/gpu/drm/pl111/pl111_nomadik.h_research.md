# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_nomadik.h

Purpose: This header exposes the Nomadik mux helper to the PL111 core while compiling to a no-op on kernels without `CONFIG_ARCH_NOMADIK`.

Important APIs, types, and functions: Declares `pl111_nomadik_init(struct drm_device *dev)` when Nomadik architecture support is enabled; otherwise provides a static inline empty function with the same signature.

Control flow: There is no runtime control flow beyond the compile-time configuration branch. The PL111 core can call `pl111_nomadik_init()` unconditionally.

State and persistence: The header owns no state. It controls whether the PMU mux write in `pl111_nomadik.c` is linked into the build.

Dependencies and integration points: Included by `pl111_drv.c`; indirectly depends on `struct drm_device` being visible enough for the declaration. The no-op form keeps generic ARM multiplatform builds from needing Nomadik PMU support.

Risks: The file declares `struct device` but the visible API uses `struct drm_device`; correctness relies on included DRM declarations from the including translation unit. If include ordering changes, a forward declaration for `struct drm_device` may be needed.

Test signals: Compile PL111 with and without `CONFIG_ARCH_NOMADIK`; verify no unresolved symbol or missing type warning; run probe on both configurations.
