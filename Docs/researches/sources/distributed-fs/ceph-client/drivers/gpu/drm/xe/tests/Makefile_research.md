# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/Makefile

## Purpose

The Xe tests `Makefile` wires KUnit test objects into the kernel build when `CONFIG_DRM_XE_KUNIT_TEST` is enabled. It separates live hardware tests from normal unit tests.

## Important APIs, Types, and Definitions

- `obj-$(CONFIG_DRM_XE_KUNIT_TEST) += xe_live_test.o` and `xe_test.o`.
- `xe_live_test-y = xe_live_test_mod.o`.
- `xe_test-y` includes `xe_test_mod.o`, `xe_args_test.o`, `xe_pci_test.o`, `xe_rtp_test.o`, and `xe_wa_test.o`.

## Control Flow

Build-system control flow is controlled by Kconfig. When enabled, Kbuild links the listed object lists into test modules/objects; live tests then register suites from `xe_live_test_mod.c`, and normal tests register through individual test translation units.

## State and Persistence Behavior

There is no runtime state. The persistent effect is build composition: which test suites are included in the generated modules.

## Dependencies and Integration Points

It integrates with Kbuild, `CONFIG_DRM_XE_KUNIT_TEST`, `xe_test_mod.c`, `xe_live_test_mod.c`, and all listed KUnit sources. Some tests in this research set are not listed here because they may be included through other objects or conditional build paths in the wider tree.

## Risks and Edge Cases

- Missing a source from the object list makes its suite unreachable even if it compiles standalone.
- Live tests are hardware-dependent and should remain separated from pure unit tests.
- Build list drift can make test coverage appear present in source while not actually linked.

## Test Signals

Signals are successful `CONFIG_DRM_XE_KUNIT_TEST` builds, KUnit suite discovery for `args`, `xe_pci`, `xe_rtp`, `xe_wa`, and live suite module discovery for `xe_bo`, `xe_dma_buf`, `xe_migrate`, `xe_mocs`, and `xe_guc_g2g`.
