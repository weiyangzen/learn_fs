# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipvtap_test.sh

Purpose: Concurrent ipvtap/ipvlan address assignment stress test, checking that many namespaces do not retain duplicate IPv4 or IPv6 addresses after random add/delete churn.

Important commands: Sources `lib.sh`, uses `setup_ns`, `cleanup_all_ns`, veth, `ip link add ... type ipvtap mode l2 bridge`, `timeout`, background jobs, associative bash arrays, and `ip address` inspection.

Control flow: `test_ip_setup_env` creates a host namespace, physical namespace, veth pair, and 32 ipvtap namespaces each with `ipvlan0` linked to the host veth. `test_ip_set` starts one timed worker per namespace; workers bring `ipvlan0` up and repeatedly add random IPv4/IPv6 addresses from a small range then delete random addresses. After all workers finish, it scans every namespace's `ipvlan0` addresses and fails if any address appears in more than one namespace.

State and persistence: Temporary namespaces and ipvtap devices only. Cleanup deletes the host veth and all namespaces.

Dependencies and integration: Requires bash, root, `ip`, timeout, and ipvtap support.

Risks: Randomized stress can be timing-dependent. The address range is intentionally small to create conflicts, so the correctness check must handle expected add failures.

Test signals: `log_test "test multithreaded ip set"` passes if no duplicate final addresses are found after concurrent churn.
