# sources/distributed-fs/ceph-client/drivers/clk/clk-gate_test.c

Purpose: KUnit test coverage for the generic gate clock in `clk-gate.c`. It verifies registration variants, enable/disable hardware bit behavior, inverted polarity, hiword-mask writes, parent propagation, and `is_enabled()` results.

Important APIs, types, and functions: `clk_gate_test_context` owns fake MMIO storage, parent clock, and gate clock. `clk_gate_register_test_*()` exercises device registration, parent-name, parent-data, legacy parent-data, parent-hw, and invalid hiword index paths. Runtime suites use `clk_prepare_enable()`, `clk_disable_unprepare()`, `clk_hw_is_enabled()`, and `clk_hw_is_prepared()`. Test init helpers register fixed-rate parents and gate clocks against fake `__iomem` memory.

Control flow: KUnit creates suites through `kunit_test_suites()`. Registration tests allocate clocks directly and unregister them in-test. Functional tests allocate context in suite `.init`, register a fixed-rate parent plus a gate, perform enable/disable operations, then clean up in `.exit`. Separate suites configure normal gate bit 5, inverted bit 15, hiword bit 9, and one-off `is_enabled` cases.

State and persistence: state is only fake little-endian register memory stored inside the KUnit context. No persistent state exists beyond each test case. The fake register is intentionally placed at the end of the context to let KASAN catch out-of-bounds register access.

Dependencies and integration points: depends on KUnit, platform device registration, fixed-rate clock helpers, common clock APIs, and the exported gate registration APIs. It is the direct test signal for `clk-gate.c`.

Risks and test signals: covers core gate semantics but not big-endian access or locking races. The hiword invalid test asserts bit indexes above 15 fail. The prepare/enable assertions also verify parent clock propagation through the common clock framework.
