# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/Kconfig

## Purpose

`vmwgfx/Kconfig` declares build-time configuration for the VMware virtual GPU DRM driver and its optional mksGuestStats instrumentation default.

## Important APIs, Types, and Functions

- `CONFIG_DRM_VMWGFX`: tristate option for the VMware SVGA2/KMS DRM driver.
- Dependencies: `DRM`, `PCI`, and either `(X86 && HYPERVISOR_GUEST)` or `ARM64`.
- Selected subsystems: `DRM_CLIENT_SELECTION`, `DRM_TTM`, `DRM_TTM_HELPER`, `MAPPING_DIRTY_HELPERS`, and transitional `DRM_KMS_HELPER`.
- `CONFIG_DRM_VMWGFX_MKSSTATS`: optional boolean default for mksGuestStats instrumentation, dependent on `DRM_VMWGFX` and `X86`.

## Control Flow

Kconfig evaluation determines whether `vmwgfx.ko` can be built in, built as a module, or omitted. If selected, required DRM/TTM helper symbols are automatically enabled. The mksGuestStats option only appears when the base driver and X86 are enabled.

## State and Persistence Behavior

No runtime state is defined here. The selected symbols shape which objects are compiled and whether instrumentation defaults are enabled.

## Dependencies and Integration Points

- Integrates with the kernel DRM and PCI Kconfig menus.
- The `DRM_KMS_HELPER` select is documented as transitional until vmwgfx sets up the primary plane itself.
- `DRM_VMWGFX_MKSSTATS` ties into instrumentation types in `vm_basic_types.h` and driver-side stats code.

## Risks and Edge Cases

- Dependency changes can make the driver visible on unsupported architectures or hide it from supported virtualized environments.
- `select` bypasses dependencies of selected symbols, so selected helper symbols must remain safe to force-enable.
- Removing `DRM_KMS_HELPER` requires confirming all transitional CRTC setup code has been migrated.

## Test Signals

- Build matrix coverage should include `m`, `y`, and `n` for `DRM_VMWGFX` on supported arches and disabled visibility on unsupported combinations.
- X86 builds should cover mksGuestStats enabled/disabled; ARM64 should verify that option remains unavailable.
