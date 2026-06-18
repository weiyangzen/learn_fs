# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_selftest.h

Purpose: Declares the QED selftest API used by higher-level driver diagnostics.

Important APIs/types/functions: Exposes `qed_selftest_memory()`, `qed_selftest_interrupt()`, `qed_selftest_register()`, `qed_selftest_clock()`, and `qed_selftest_nvram()`, all taking `struct qed_dev *` and returning an integer status.

Control flow: No runtime logic. Kernel-doc comments describe each diagnostic entry point.

State and persistence: No state is stored in the header.

Dependencies/integration: Includes Linux types and relies on `struct qed_dev` being declared by including contexts.

Risks: The header does not provide disabled-build stubs, so link coverage must match object inclusion. Comments use generic `Return: Int.` and do not document specific negative errno values.

Test signals: Compile/link diagnostics consumers and verify each declared function is reachable from ethtool or equivalent selftest paths.
