# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/mode-1-recovery-updelay.sh

Purpose: Exercises active-backup bond recovery with varied `updelay` values.

Important APIs/functions: Sources `lag_lib.sh`, `cleanup()`, `test_bond_recovery`, bond parameters `mode 1 miimon 100 updelay N`, and trap cleanup.

Control flow: The script sets cleanup trap, then calls `test_bond_recovery` for mode 1 with `updelay` values 0, 200, 500, 1000, 2000, 5000, and 10000 ms.

State and persistence: Network namespaces and bond topology are created/reset by `lag_lib.sh`; cleanup removes them.

Dependencies and integration points: Requires bonding active-backup, miimon, veth/bridge topology, and helper recovery assertions.

Risks and test signals: Failures indicate active-backup carrier recovery or `updelay` timing regressions. Runtime can be long for high updelay values.
