# sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression.h

Purpose: small header declaring the four radix-tree regression test entry points.

Important APIs/types/functions: declares `regression1_test()`, `regression2_test()`, `regression3_test()`, and `regression4_test()` behind `__REGRESSION_H__`.

Control flow: no executable flow; it is included by the main radix-tree runner and individual regression sources to share prototypes.

State and persistence: no state and no persistence.

Dependencies/integration: provides the C linkage contract among the regression sources and the radix-tree userspace test harness.

Risks and test signals: risk is limited to prototype drift if regression implementations are renamed or signatures change; build failures are the main signal.
