# sources/distributed-fs/ceph-client/tools/testing/radix-tree/xarray.c

Purpose: userspace shim that compiles and runs the kernel `lib/test_xarray.c` suite.

Important APIs/types/functions: includes `xarray-shared.h`, `test.h`, undefines `XA_DEBUG`, includes `../../../lib/test_xarray.c`, defines `xarray_tests()` as `xarray_checks()` plus `xarray_exit()`, and provides a weak standalone `main()`.

Control flow: standalone mode registers the RCU thread, initializes radix-tree/XArray infrastructure, runs XArray checks, simulates CPU teardown, waits for RCU, reports nonzero `nr_allocated`, unregisters RCU, and exits.

State and persistence: no file state; heap/XArray state is created by the imported kernel test and cleaned by `xarray_exit()`/RCU barriers.

Dependencies/integration: bridges kernel XArray selftest code into the userspace tools test harness. The weak `main()` lets another runner link this file without duplicate main conflicts.

Risks and test signals: correctness depends on imported `test_xarray.c`; nonzero `nr_allocated` after `rcu_barrier()` signals leaks.
