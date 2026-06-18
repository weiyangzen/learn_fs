# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_nolocalbypass.sh

## Purpose
`test_vxlan_nolocalbypass.sh` verifies the VXLAN `localbypass`/`nolocalbypass` device option. It creates two VXLAN devices in the same namespace and confirms that local delivery is allowed by default, suppressed after `nolocalbypass`, and restored after setting `localbypass`.

## Important APIs, Functions, and Types
The script defines local `log_test`, `run_cmd`, and `tc_check_packets` helpers and uses `lib.sh` namespace cleanup helpers. `setup` creates namespace `ns1`, loopback VTEP addresses, `vx0` with `nolearning`, and `vx1` with a different destination port. `nolocalbypass` is the sole test and uses `bridge fdb`, `ip -d -j link show`, `jq`, `tc flower`, and `mausezahn`.

## Control Flow
Main parses `-t`, pause, and verbose flags; checks root and command availability; verifies `ip link help vxlan` includes `localbypass`; and then runs selected tests with setup/cleanup around each. The test adds an FDB entry on `vx0` pointing to a local loopback VTEP and port `4790`, installs a `tc` ingress counter on `vx1`, and installs a loopback ingress drop filter for encapsulated UDP port `4790`. It first checks JSON link data reports `localbypass == true`, sends one frame, and expects `vx1` ingress count one. It then sets `nolocalbypass`, confirms JSON reports false, sends again, and expects the `vx1` counter to remain one. Finally, it re-enables `localbypass`, sends again, and expects the counter to become two.

## State and Persistence
All state is in namespace `ns1`: VXLAN links, loopback addresses, FDB entries, qdiscs, filters, and packet counters. The script maintains only shell counters and exits with `ret`; no persistent files are written.

## Dependencies and Integration Points
Dependencies are root, `ip`, `bridge`, `mausezahn`, `jq`, `tc`, and kernel/iproute2 VXLAN localbypass support. It integrates with VXLAN local receive bypass semantics, bridge FDB remote-port selection, link JSON introspection, and `tc` packet counters.

## Risks and Test Signals
The main risk is feature skew: older iproute2 may not expose `localbypass`, and counter checks rely on short sleeps. The test’s signal is exact counter behavior across three sends and link JSON truth values, proving that the option toggles whether locally destined encapsulated traffic bypasses the underlay.
