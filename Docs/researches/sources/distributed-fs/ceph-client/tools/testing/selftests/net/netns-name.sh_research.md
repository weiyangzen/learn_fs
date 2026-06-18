<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netns-name.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netns-name.sh

## Purpose
This shell test verifies network device name, ifindex, and alternate-name semantics when devices are created in or moved between network namespaces. It specifically uses netdevsim for notifier-sensitive move coverage.

## Important APIs, Types, And Functions
It sources `lib.sh` and uses `setup_ns`, `create_netdevsim`, `cleanup_netdevsim`, `cleanup_ns`, `ip link set ... netns`, `ip link property add ... altname`, and dummy devices. Local helpers are `cleanup()` and `fail()`.

## Control Flow
The script creates two namespaces, moves a netdevsim device without rename, tests a move rejected due to name conflict, tests conflict resolution by renaming during move, tests alternate-name duplication rejection, tests that an alternate name moves namespace visibility correctly, and validates that identical name/ifindex pairs can exist in separate namespaces.

## State, Persistence, And Dependencies
State includes two namespaces, netdevsim device instance address 2025, dummy devices, alternate names, and selected ifindex values. Cleanup removes netdevsim and namespaces. It depends on netdevsim support and recent iproute2 alternate-name functionality.

## Integration Points
This is net core namespace/name management coverage and exercises notifier paths through netdevsim. It complements netns sysctl and netdev generic-netlink tests by validating namespace isolation at the rtnetlink/iproute2 level.

## Risks
The script relies on helper cleanup even if intermediate device deletion fails. The fixed netdevsim address can collide if parallel tests reuse it. It uses `set -o pipefail` but accumulates failures in `RET_CODE`, so later cleanup/test actions still run.

## Test Signals
The final line prints the script basename with `[  OK  ]` or `[ FAIL ]`. Each failure reports the specific invalid move, missing device, or alternate-name visibility problem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netns-name.sh -->
