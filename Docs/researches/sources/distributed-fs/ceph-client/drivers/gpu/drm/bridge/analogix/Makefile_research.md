<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/Makefile

## Purpose

The Analogix bridge Makefile maps Analogix Kconfig symbols to their driver objects and defines the shared Analogix DP composite object.

## Important APIs, Types, And Targets

- `analogix_dp-objs := analogix_dp_core.o analogix_dp_reg.o analogix-i2c-dptx.o`.
- `obj-$(CONFIG_DRM_ANALOGIX_ANX6345) += analogix-anx6345.o`.
- `obj-$(CONFIG_DRM_ANALOGIX_ANX7625) += anx7625.o`.
- `obj-$(CONFIG_DRM_ANALOGIX_ANX78XX) += analogix-anx78xx.o`.
- `obj-$(CONFIG_DRM_ANALOGIX_DP) += analogix_dp.o`.

## Control Flow

No runtime flow exists. Kbuild composes and links objects based on Kconfig.

## State And Persistence Behavior

The file only affects build outputs.

## Dependencies And Integration Points

It integrates the local Kconfig symbols with the shared DP core and chip-specific I2C bridge drivers.

## Risks And Edge Cases

If a chip driver selects `DRM_ANALOGIX_DP` but the composite object list misses a required helper, link failures or missing AUX operations can result. Symbol/filename mismatches make Kconfig entries ineffective.

## Test Signals

Build each Analogix bridge as module and built-in, verify `analogix_dp.o` composition, and run modpost for unresolved symbol coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/Makefile -->
