# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/Kconfig

## Purpose
Kconfig entry for the TI Keystone Display SubSystem DRM driver. It exposes `CONFIG_DRM_TIDSS` as a tristate option for Keystone-family SoCs and compile-test builds.

## Important APIs, Types, And Functions
The file defines `config DRM_TIDSS` with prompt `DRM Support for TI Keystone`. It depends on `DRM && OF`, and on `ARM || ARM64 || COMPILE_TEST`. It selects `DRM_CLIENT_SELECTION`, `DRM_KMS_HELPER`, `DRM_DISPLAY_HELPER`, `DRM_BRIDGE_CONNECTOR`, and `DRM_GEM_DMA_HELPER`.

## Control Flow
There is no runtime control flow. During kernel configuration, enabling this option allows the Makefile to build `tidss.o` as built-in or module depending on the selected tristate value.

## State And Persistence
The persistent state is the generated kernel configuration value for `CONFIG_DRM_TIDSS`. That value controls compilation and module availability.

## Dependencies And Integration Points
The option integrates the TIDSS driver with the DRM core, Open Firmware/device-tree based platform discovery, KMS helpers, display helpers, bridge connector support, and DMA GEM helpers. The help text documents target SoCs: 66AK2Gx, AM65x, and J721E.

## Risks And Maintenance Notes
Incorrect dependencies could expose the driver on unsupported architectures or hide compile-test coverage. Missing selected helper libraries would surface as link errors. The prompt says Keystone while the supported family list spans multiple TI DSS variants; update help text if supported SoCs change.

## Test Signals
Signals are build-time: `CONFIG_DRM_TIDSS=y/m` should compile and link the objects from the tidss Makefile on supported or compile-test configurations, and be unavailable when core DRM/OF dependencies are absent.
