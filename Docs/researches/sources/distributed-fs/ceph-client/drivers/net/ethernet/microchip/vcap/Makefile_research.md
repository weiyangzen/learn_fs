# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/Makefile

## Purpose
`vcap/Makefile` builds the shared Microchip VCAP library objects and optional KUnit/debugfs components based on Kconfig symbols.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_VCAP) += vcap.o` builds the composite VCAP library.
- `obj-$(CONFIG_VCAP_KUNIT_TEST) +=  vcap_model_kunit.o` builds KUnit tests.
- `vcap-$(CONFIG_DEBUG_FS) += vcap_api_debugfs.o` adds debugfs support to the composite object.
- `vcap-y += vcap_api.o vcap_tc.o` always includes the core API and tc integration when `vcap.o` is built.

## Control Flow
Kbuild evaluates the symbol-expanded object lists. If `CONFIG_VCAP` is enabled, `vcap.o` is linked from the listed `vcap-y` and conditional `vcap-*` members. If KUnit test config is enabled, the model test object is built separately.

## State and Persistence Behavior
The file has no runtime state. It controls which object files exist in the kernel build. Inclusion of `vcap_api_debugfs.o` determines whether debugfs support code is linked into the VCAP composite.

## Dependencies and Integration Points
It depends on Linux Kbuild conventions and symbols from `vcap/Kconfig`. It integrates the VCAP core (`vcap_api.o`), tc bridge (`vcap_tc.o`), optional debugfs (`vcap_api_debugfs.o`), and tests (`vcap_model_kunit.o`) with Microchip switch drivers such as Sparx5.

## Risks and Edge Cases
- The extra spacing before `vcap_model_kunit.o` is harmless but visually inconsistent.
- New VCAP source files must be added to the correct composite list or they will compile in some configs but not link into the library.
- Debugfs code must remain optional because non-debugfs builds omit `vcap_api_debugfs.o`.

## Test Signals
- Build with `CONFIG_VCAP=y` and `CONFIG_DEBUG_FS` toggled.
- Build with `CONFIG_VCAP_KUNIT_TEST=y` and run VCAP KUnit tests.
- Link checks should verify Sparx5 resolves VCAP symbols in all supported configs.
