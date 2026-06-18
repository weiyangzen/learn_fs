# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/Kconfig

## Purpose

This Kconfig file declares the VKMS driver and its KUnit test module options. VKMS is a software-only DRM/KMS implementation used for testing and headless display environments.

## Important symbols and dependencies

`DRM_VKMS` is a tristate option depending on `DRM && MMU`. It selects DRM client selection, KMS helper support, GEM shmem helpers, CRC32, and configfs support. `DRM_VKMS_KUNIT_TEST` is a tristate test option depending on `DRM_VKMS && KUNIT`, defaults to `KUNIT_ALL_TESTS`, and is hidden behind the normal KUnit all-tests flow unless explicitly selected.

## Control flow and integration

The configuration controls compilation of the main `vkms` module and the `vkms-kunit-tests` object from the local Makefiles. Selecting configfs here is important because the driver always registers the VKMS configfs subsystem during module initialization.

## State, risks, and test signals

There is no runtime state in this file. Risks are build-configuration related: enabling VKMS pulls configfs and CRC support, while enabling KUnit tests requires exported-for-KUnit symbols in composer/config/format code. The test signal is successful kernel configuration and module build with `CONFIG_DRM_VKMS` and optionally `CONFIG_DRM_VKMS_KUNIT_TEST`.
