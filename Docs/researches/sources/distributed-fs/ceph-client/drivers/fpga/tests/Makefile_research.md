# sources/distributed-fs/ceph-client/drivers/fpga/tests/Makefile

Purpose: build mapping for FPGA subsystem KUnit test objects. It connects `CONFIG_FPGA_KUNIT_TESTS` to the manager, bridge, and region KUnit suites.

Important APIs and control flow: the single object rule appends `fpga-mgr-test.o`, `fpga-bridge-test.o`, and `fpga-region-test.o` to `obj-$(CONFIG_FPGA_KUNIT_TESTS)`. Standard kernel build logic compiles these objects when the Kconfig symbol is enabled.

State and persistence: build-time only. It creates no runtime state, but determines which KUnit test object files are linked into the kernel or module set.

Dependencies and integration points: depends on `drivers/fpga/tests/Kconfig` selecting `CONFIG_FPGA_KUNIT_TESTS` and on the corresponding test source files in the same directory. It integrates with Kbuild and the FPGA subsystem's test coverage.

Risks and test signals: risks include stale object names if tests are renamed or split and no per-test granularity in Kconfig. Test signals are successful Kbuild resolution, generated test objects, and KUnit execution reporting manager, bridge, and region suite results.
