# sources/distributed-fs/ceph-client/drivers/fpga/tests/Kconfig

Purpose: Kconfig entry for FPGA subsystem KUnit tests. It creates `FPGA_KUNIT_TESTS`, allowing the FPGA manager, bridge, and region unit tests to be built when the relevant subsystem dependencies and KUnit are enabled.

Important APIs and control flow: `config FPGA_KUNIT_TESTS` is tristate and is visible unless `KUNIT_ALL_TESTS` selects it implicitly. It depends on `FPGA`, `FPGA_REGION`, `FPGA_BRIDGE`, and `KUNIT=y`; it defaults to `KUNIT_ALL_TESTS`. The help text explains that it builds unit tests for the FPGA subsystem and points readers to KUnit documentation.

State and persistence: this file controls build-time state only. It does not create runtime state, but its selected value determines whether FPGA KUnit test modules/objects are compiled.

Dependencies and integration points: depends on the main FPGA framework symbols and KUnit. It integrates with the local test Makefile through `CONFIG_FPGA_KUNIT_TESTS`.

Risks and test signals: risks include tests being unavailable when KUnit is modular or disabled, dependency drift if new tests require additional framework symbols, and limited visibility when `KUNIT_ALL_TESTS` auto-selects defaults. Test signals are Kconfig dependency resolution, `CONFIG_FPGA_KUNIT_TESTS=y/m`, and successful build/run of `fpga-mgr-test`, `fpga-bridge-test`, and `fpga-region-test`.
