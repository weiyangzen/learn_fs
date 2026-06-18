# sources/distributed-fs/ceph-client/include/drm/bridge/aux-bridge.h

Purpose: declares optional helper bridges for DisplayPort AUX and HPD bridge auxiliary devices.

Important APIs, types, and flow: with `CONFIG_DRM_AUX_BRIDGE`, `drm_aux_bridge_register()` registers an AUX bridge under a parent device; otherwise it is a no-op success. With `CONFIG_DRM_AUX_HPD_BRIDGE`, devm helpers allocate/add an HPD bridge auxiliary device, a non-devm register helper creates a bridge device from parent and device node, and `drm_aux_hpd_bridge_notify()` reports connector status changes. Disabled stubs return NULL/0 or do nothing.

State and persistence: state is auxiliary-device and devm-managed bridge objects in implementation code. No persistence exists.

Dependencies and integration: depends on DRM connector status, auxiliary bus, device tree nodes, and DP bridge users.

Risks and test signals: disabled stubs returning success can hide missing bridge functionality unless callers account for Kconfig. Signals include AUX/HPD bridge registration tests, devm cleanup on probe failure, hotplug notify behavior, device-tree binding tests, and disabled-Kconfig build/runtime coverage.
