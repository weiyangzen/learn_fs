# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/Makefile

## Purpose

This Makefile defines the compilation units for the VKMS module and conditionally descends into the KUnit tests directory.

## Important build entries

`vkms-y` links the core implementation objects: driver registration, plane/output/writeback/connector setup, format conversion, CRTC/composer logic, config/configfs support, color pipeline setup, and LUT tables. `obj-$(CONFIG_DRM_VKMS) += vkms.o` builds the module when VKMS is enabled. `obj-$(CONFIG_DRM_VKMS_KUNIT_TEST) += tests/` includes the test subdirectory for KUnit builds.

## Integration and risks

The object order makes all core VKMS helpers part of one module, so symbol visibility is mostly internal except KUnit-exported helpers. The Makefile must stay aligned with new source files; missing an object would surface as link errors or unregistered feature paths. Test signal is a successful module build with both normal and KUnit configurations.
