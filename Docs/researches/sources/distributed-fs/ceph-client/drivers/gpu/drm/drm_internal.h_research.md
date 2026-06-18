# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_internal.h

## Purpose

`drm_internal.h` is the private DRM core header used to share non-UAPI declarations across DRM core compilation units. It centralizes internal interface version constants, forward declarations, feature-dependent stubs, and prototypes for file, PCI, PRIME, managed-resource, vblank, IRQ, auth, sysfs, GEM, debugfs, syncobj, and framebuffer helpers.

## Important APIs, Types, And Functions

The header defines `DRM_IF_MAJOR`, `DRM_IF_MINOR`, and `DRM_IF_VERSION(maj, min)`, which are consumed by SET_VERSION/GET_UNIQUE compatibility paths. It declares `drm_global_mutex`, file lifecycle helpers (`drm_file_alloc()`, `drm_file_free()`), PCI bus-id setup (`drm_pci_set_busid()` or an `-EINVAL` stub), PRIME handle-private helpers, managed-resource release entry points (`drm_managed_release()`, `drmm_add_final_kfree()`), vblank counters/workers, ioctl handlers, auth/master operations, sysfs registration, GEM handle/open/close/vmap helpers, debugfs setup/teardown, syncobj ioctls, and framebuffer debug/print helpers.

Conditional sections provide no-op stubs for disabled `CONFIG_DRM_CLIENT`, `CONFIG_MAGIC_SYSRQ`, `CONFIG_PCI`, and `CONFIG_DEBUG_FS` features. This keeps call sites simple while allowing the configured kernel to compile out optional infrastructure.

## Control Flow

This header has no executable control flow of its own except small inline helpers. `drm_vblank_passed()` compares sequence numbers with 24-bit wrap semantics. `drm_vblank_flush_worker()` and `drm_vblank_destroy_worker()` wrap kthread worker operations. Debugfs and client/sysrq stubs collapse to empty or success-returning functions when their configs are disabled.

## State And Persistence

The header owns no runtime storage. It exposes state owned by other compilation units, such as `drm_global_mutex`, `drm_class`, DRM file private data, GEM object handle state, syncobj state, vblank workers, sysfs minors, and managed-resource lists. Its constants affect persistent userspace ABI behavior for DRM interface version negotiation but do not themselves store data.

## Dependencies And Integration Points

It includes Linux `kthread.h`, `types.h`, and public DRM headers `drm_ioctl.h` and `drm_vblank.h`. It is included by core files such as ioctl, compat ioctl, leasing, managed resources, GEM, sysfs, auth, debugfs, and vblank code. Because it is private to the DRM core, declarations here are integration contracts between DRM internals rather than driver-facing API.

## Risks And Edge Cases

Prototype drift is the main risk: changing a function signature in an implementation without updating this header breaks core builds or silently changes call semantics if casts are involved elsewhere. Config stubs must match real function semantics closely enough that disabled-feature builds remain correct; returning success for debugfs registration is intentional but could hide code that assumes debugfs side effects. `DRM_IF_MINOR` changes affect old libdrm compatibility logic and must be handled cautiously.

## Test Signals

Primary validation is build coverage across config combinations: with and without PCI, debugfs, DRM client, sysrq, syncobj, modeset, and GEM users. Runtime signals come from successful DRM device open/close, sysfs/debugfs registration, vblank handling, PRIME handle conversion, syncobj ioctls, GEM handle lifetimes, and SET_VERSION/GET_UNIQUE behavior.
