# sources/distributed-fs/ceph-client/drivers/regulator/dbx500-prcmu.c

Purpose: Implements shared UX500 regulator support for DBX500 PRCMU-backed regulators, specifically the active power-state reference counter and optional debugfs inspection.

Important APIs, types, and functions: `power_state_active_enable()` increments a spinlock-protected global count, and `power_state_active_disable()` decrements it with unbalanced-call detection. Under `CONFIG_REGULATOR_DEBUG`, `struct ux500_regulator_debug` stores debugfs root, regulator array, counts, and suspend-state snapshots. Debugfs show callbacks expose the active count and per-regulator current/before/after states. `ux500_regulator_debug_init()` creates `ux500-regulator/status` and `ux500-regulator/power-state-count`; `ux500_regulator_debug_exit()` removes the tree and frees snapshots.

Control flow: DB8500 regulators call the power-state helpers from enable/disable paths. DB8500 probe calls debug init with the static regulator array; remove calls debug exit. Debugfs reads format live information from the shared regulator array.

State and persistence: `power_state_active_cnt` is a process-global integer protected by `power_state_active_lock`. Debug state is stored in a single static `rdebug` object. Snapshot arrays are allocated during debug init and freed at exit, though this file does not itself populate before/after suspend snapshots.

Dependencies and integration points: This file depends on regulator descriptors from `dbx500-prcmu.h`, platform devices, debugfs, seq_file, and module infrastructure. It is shared support for platform-specific files such as `db8500-prcmu.c`.

Risks and test signals: Test unbalanced disable detection, concurrent enable/disable with IRQ-safe spinlock coverage, debugfs file creation failure tolerance, and cleanup after partial debug init allocation failure. Since the active count is global, tests should not assume per-device isolation.
