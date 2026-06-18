# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb_host.sh

## Purpose
`bridge_mdb_host.sh` is a focused kselftest for host MDB entries, meaning MDB entries whose port is the bridge device itself (`port br0`). It verifies add, display, delete, and default/permanent flag semantics for IPv4, IPv6, and raw L2 multicast host groups.

## Important APIs, Functions, and Control Flow
`ALL_TESTS` contains only `mdb_add_del_test`. `setup_prepare` assigns `$h1` and `$swp1`, prepares VRFs, configures `$h1` with IPv4 and IPv6 addresses, creates `br0` with multicast snooping enabled, enslaves `$swp1`, and brings the bridge and port up. `do_mdb_add_del` is the core helper. It runs `bridge mdb add dev br0 port br0 grp $group $flag`, checks `bridge mdb show dev br0` for the group and expected flag, deletes the entry, and checks that the group disappears. If no flag is supplied it expects `temp`, which is the default for IP multicast host entries. `mdb_add_del_test` calls the helper for a permanent L2 group and temporary IPv4/IPv6 groups.

## State, Dependencies, Integration Points, and Risks
State is limited to one bridge, one bridge slave, one host namespace/VRF endpoint, and the MDB entries under test. The script depends on `lib.sh`, `ip`, `bridge`, grep text output, and kselftest helper functions. It is intentionally narrow and does not test forwarding; it tests userspace/kernel MDB host-entry configuration behavior. The main risk is reliance on textual `bridge mdb show` formatting for flag detection rather than JSON output.

## Test Signals
The signal is a sequence of `check_err` and `check_err_fail` assertions plus `log_test "MDB add/del group ..."`. Any failure to add, observe, delete, or remove an MDB record increments `RET` and contributes to `$EXIT_STATUS`.
