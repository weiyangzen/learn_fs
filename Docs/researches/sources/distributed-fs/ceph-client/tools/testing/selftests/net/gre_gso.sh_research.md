# sources/distributed-fs/ceph-client/tools/testing/selftests/net/gre_gso.sh

## Purpose

This selftest verifies GRE over IPv6 GSO/TSO behavior by copying a large random file through GRE tunnel endpoints and checking that TCP transfer succeeds with both TSO enabled and disabled.

## Important APIs, Types, and Functions

It sources `lib.sh` and defines `setup`, `cleanup`, `get_linklocal`, `gre_create_tun`, `gre_gst_test_checks`, `gre6_gso_test`, `gre_gso_test`, `usage`, and `log_test`. It uses `ip tunnel`, `socat`, `ss`, `ethtool -K tso`, `dd`, `timeout`, and namespace helpers.

## Control Flow

The main parser handles `-t`, pause, and verbose flags, validates root and required commands, cleans stale state, then runs `gre_gso_test`. That creates a namespace and veth pair, generates a 2 MiB random file, derives link-local IPv6 addresses on both veth endpoints, creates matching `ip6gre` tunnels, assigns IPv4 and IPv6 addresses to the tunnel, starts a `socat` listener in the namespace, copies the file with TSO enabled, disables TSO on the outer veth, copies again to exercise GSO, restores TSO, and cleans up.

## State and Persistence Behavior

Temporary state includes a namespace, veth pair, `gre1` tunnel devices in both namespaces, tunnel IP addresses, a random temporary file, a background `socat` listener PID, and ethtool TSO feature state on `veth0`. Cleanup removes the temp file, kills the listener, deletes links, and removes the namespace.

## Dependencies and Integration Points

The test depends on root, `ip`, `socat`, `ss`, `ethtool`, GRE/IP6GRE kernel support, veth link-local IPv6 addresses, and the kselftest namespace helpers. It integrates with the kernel GRE tunnel, segmentation offload, and TCP data paths.

## Risks and Edge Cases

The listener readiness loop increments an undeclared `i` and has no explicit timeout, so a failed listener can hang. `timeout 1 socat` assumes the file transfer completes quickly. Link-local address discovery must succeed on both veth endpoints. The cleanup kills `$PID` if set, which is important after failed transfers.

## Test Signals

Success is two `log_test` OK entries for GREv6 carrying IPv4 and two for GREv6 carrying IPv6: one copy with TSO and one copy with software GSO after disabling TSO.
