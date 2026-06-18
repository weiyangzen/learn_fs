# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/Makefile

## Purpose

This Makefile builds the VKMS KUnit aggregate test object.

## Important build entries

`vkms-kunit-tests-y` includes `vkms_config_test.o`, `vkms_format_test.o`, and `vkms_color_test.o`. `obj-$(CONFIG_DRM_VKMS_KUNIT_TEST) += vkms-kunit-tests.o` links them only when the KUnit test option is enabled.

## Integration and risks

The tests import symbols from the main VKMS module through the `EXPORTED_FOR_KUNIT_TESTING` namespace. Build failures indicate missing visibility annotations, missing source objects, or stale test object names. Runtime test signal is discovery of the `vkms-config`, `vkms-format`, and `vkms-color` suites by KUnit.
