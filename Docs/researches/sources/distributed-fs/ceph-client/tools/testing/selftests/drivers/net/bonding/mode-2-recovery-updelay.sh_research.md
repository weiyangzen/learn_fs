# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/mode-2-recovery-updelay.sh

Purpose: Exercises balance-xor bond recovery with varied `updelay` values.

Important APIs/functions: Sources `lag_lib.sh`, `cleanup()`, `test_bond_recovery`, bond parameters `mode 2 miimon 100 updelay N`, and trap cleanup.

Control flow: It runs the shared recovery helper for mode 2 with `updelay` values from 0 through 10000 ms, checking traffic recovery after link disturbances.

State and persistence: Temporary network topology and bond state are created by `lag_lib.sh`; cleanup removes namespaces/devices.

Dependencies and integration points: Requires bonding balance-xor mode, veth/bridge, miimon support, and helper library.

Risks and test signals: Failures indicate mode 2 recovery, hashing, carrier, or updelay regressions. High delay cases intentionally extend runtime.
