# sources/distributed-fs/ceph-client/tools/testing/selftests/pcie_bwctrl/Makefile

Purpose: registers PCIe bandwidth-control shell tests with kselftest.

Important settings: `TEST_PROGS` is `set_pcie_cooling_state.sh`, the top-level executable. `TEST_FILES` is `set_pcie_speed.sh`, a helper installed beside the runner.

Control flow/integration: `../lib.mk` handles install and run integration. The top-level script discovers sysfs devices and invokes the helper.

State/dependencies: no build products. Runtime depends on sysfs, thermal cooling devices, and PCIe link-speed attributes.

Risks: helper must be installed in the working directory because the runner invokes `./set_pcie_speed.sh`.

Test signals: shell scripts print pass/fail/skip and return kselftest-compatible status.
