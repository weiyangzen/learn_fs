# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-eth-type-change.sh

Purpose: Tests bond device ARPHRD type transitions while a bond is enslaved to another bond, ensuring `MASTER` and `SLAVE` flags remain correct.

Important APIs/functions: `bond_check_flags()`, `bond_test_enslave_type_change()`, `bond_test_unsuccessful_enslave_type_change()`, `bond_test_successful_enslave_type_change()`, `ip link add type nlmon`, `ip link add type bond`, `ip -d link`, and forwarding `tests_run`.

Control flow: Each case creates nested bond devices and a non-Ethernet `nlmon` device. It optionally switches the inner bond to active-backup so non-Ethernet enslave can succeed, attempts type changes through enslave/nomaster cycles, restores Ethernet type by enslaving another bond, verifies flags, and deletes devices.

State and persistence: Temporary link devices are removed in-test. The global `RET`/`EXIT_STATUS` convention comes from `lib.sh`.

Dependencies and integration points: Requires bonding, nlmon, iproute support for detailed JSON/link flags, and forwarding test harness.

Risks and test signals: Failures indicate bond type restoration or flag propagation regressions. Cleanup is manual within the test body, so early command failures rely on harness behavior.
