<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink_notification.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink_notification.sh

## Purpose

`rtnetlink_notification.sh` verifies that rtnetlink multicast notifications are emitted for multicast and anycast address changes. It creates a dummy interface, watches iproute2 monitor streams, and checks that expected add/delete notifications appear.

## Important APIs, Types, and Functions

The script sources `lib.sh` for `defer`, `kill_process`, `check_err`, `log_test`, `tests_run`, `EXIT_STATUS`, and `require_command`. `kci_test_mcast_addr_notification` runs `ip monitor maddr`; `kci_test_anycast_addr_notification` runs `ip monitor acaddress`. Both use `mktemp`, background monitors, `grep -cE`, and a fixed dummy device name `test-dummy1`.

## Control Flow

Startup checks for root and the `ip` command. Each test starts an `ip monitor` process, defers removal of the temp file and monitor kill, waits briefly for subscription setup, creates/activates/deletes a dummy interface, then counts matching monitor lines. If the monitor process exits immediately, the test treats iproute2 support as missing and skips.

## State and Persistence Behavior

The only intended kernel state is transient: one dummy link and a sysctl write enabling IPv6 forwarding on that dummy for the anycast case. Temp files are removed through `defer`, and monitor processes are killed. No persistent report state is written by the source script.

## Dependencies and Integration Points

This integrates with rtnetlink notification paths and iproute2 monitor subcommands. It depends on dummy link support, IPv4 multicast default address notification, IPv6 all-nodes multicast notification, IPv6 anycast behavior for link-local routes under forwarding, and root privileges.

## Risks and Edge Cases

The test relies on sleeps rather than explicit synchronization with monitor readiness. It assumes exactly four multicast matches and two anycast matches; extra notifications or changed iproute2 formatting can produce false failures. If dummy creation fails, later cleanup relies on deletion commands not being needed.

## Test Signals

Expected success is a kselftest OK for both cases. Multicast notification should produce two add and two delete matches for `224.0.0.1` and `ff02::1`; anycast should produce add/delete matches for `fe80::` after enabling IPv6 forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink_notification.sh -->
