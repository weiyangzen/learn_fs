# Research: subset-b-006829

Grouped research for `subset-b-006829`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_l2_drops.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_l2_drops.sh

## Purpose

mlxsw devlink L2 drop-trap coverage for bridge ingress and forwarding-drop cases.

## Important APIs, Types, and Functions

Defines host setup helpers, a VLAN-aware `br0` switch setup with `clsact` on the egress port, and tests for `source_mac_is_multicast`, `vlan_tag_mismatch`, `ingress_vlan_filter`, `ingress_spanning_tree_filter`, `port_list_is_empty`, `port_loopback_filter`, and `locked_port` traps. It uses `devlink_trap_drop_test`, `devlink_trap_stats_idle_test`, `devlink_trap_group_get`, TC flower counters, bridge VLAN/FDB commands, and mausezahn packet generation.

## Control Flow

Setup maps four netifs into H1/SWP1/SWP2/H2, prepares VRFs, creates simple hosts, enslaves switch ports to a VLAN-filtering bridge, and installs egress counters. Each test first forces a hardware drop condition, starts traffic, verifies the expected trap and TC drop counter, then changes bridge state so the same traffic should forward without trap counter growth. Cleanup kills traffic, deletes filters, restores trap action to drop, tears down bridge state, and removes VRFs.

## State and Persistence Behavior

State is transient kernel networking state: bridge VLAN membership, STP state, flood flags, locked-port flags, FDB entries, TC filters, running mausezahn PIDs, and devlink trap action/stat counters. No persistent repository or device configuration should remain after `cleanup`.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Races are possible around continuous traffic and asynchronous trap counters. The negative assertions depend on restoring PVID, VLAN membership, STP forwarding, flood flags, and FDB entries in the right order. Locked-port tests are sensitive to FDB learning and static entry cleanup. Failures can also come from missing clsact offload, bridge VLAN behavior changes, or trap default-action drift.

## Test Signals

Signals are `log_test` results per trap, successful `devlink_trap_drop_test`, idle trap/group stats when forwarding should resume, and TC flower packet counts proving forwarded packets are not dropped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_l2_drops.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_l3_drops.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_l3_drops.sh

## Purpose

mlxsw devlink L3 drop-trap coverage for malformed, invalid, disabled-RIF, and blackhole routed packets.

## Important APIs, Types, and Functions

Builds a two-host routed topology with IPv4 and IPv6 defaults through SW router ports. Important helpers are `ping_check`, protocol-specific packet constructors, `devlink_trap_drop_test`, `devlink_trap_action_set`, `devlink_trap_rx_packets_get`, and TC flower filters. Tests cover non-IP frames, unicast DIP over multicast DMAC, loopback and multicast SIP/DIP, corrupted IPv4/IPv6 headers, limited broadcast SIP, reserved/interface-local IPv6 multicast destinations, blackhole routes/nexthops, and ingress/egress RIF-disabled traps.

## Control Flow

The script establishes VRFs, enables forwarding, configures router-port addresses, and uses H1 to inject packets toward H2 while egress filters on RP2 identify dropped traffic. Generic tests validate normal ping first, then set trap actions, inject malformed or policy-dropped packets, and assert trap/drop behavior. RIF-disabled tests temporarily create a bridge/RIF state, remove or alter it while traffic is active, and compare devlink trap packet/byte counters.

## State and Persistence Behavior

Runtime state includes forwarding sysctls, VRFs, IPv4/IPv6 routes, blackhole routes, nexthops, TC filters, devlink trap action/stat state, bridge devices used to create/remove RIFs, and background traffic processes.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The largest risks are false negatives from route convergence delay, neighbor resolution, TC filter protocol mismatch, or trap stats not settling before comparison. RIF-disabled cases are order-sensitive because bridge deletion/deslavement must create the exact disabled ingress or egress RIF condition. Packet payload constructors use fixed header bytes, so kernel parser changes can invalidate expected trap names.

## Test Signals

Test signals are successful baseline pings, trap counter growth for each invalid condition, TC drop hits, and cleanup restoring trap actions and forwarding/VRF state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_l3_drops.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_l3_exceptions.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_l3_exceptions.sh

## Purpose

mlxsw devlink exception-trap coverage for packets that should be trapped to CPU instead of silently dropped.

## Important APIs, Types, and Functions

Defines routed H1/RP1/RP2/H2 topology with clsact on H1 and RP2, requires multicast routing daemons (`$MCD`, `$MC_CLI`), and tests `mtu_value_is_too_small`, `ttl_value_is_too_small`, multicast reverse-path forwarding, reject routes, unresolved neighbor variants, and IPv4/IPv6 LPM misses. It uses `devlink_trap_exception_test`, trap action inspection, ICMP TC filters, route manipulation, and multicast daemon control.

## Control Flow

Setup starts the multicast daemon, prepares VRFs/forwarding, and configures router addresses. Tests verify normal ping, confirm the expected default trap action, create a forwarding exception such as DF+oversized packet, low TTL, mroute RPF miss, reject route, missing neighbor, or route-table miss, then assert the devlink exception and any expected ICMP reply/counter. Cleanup stops traffic, removes routes/filters/VRFs, restores forwarding, and kills the daemon.

## State and Persistence Behavior

State includes multicast routing daemon process state, routes and reject routes, MTU changes, neighbor entries, temporary VRFs without routes, TC filters, and devlink trap counters/actions. All state is expected to be local to the test run.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It additionally requires multicast routing helper binaries exposed through `$MCD` and `$MC_CLI`.

## Risks and Edge Cases

Exception tests depend heavily on CPU trap action defaults, ICMP generation, and timing of multicast daemon programming. Missing daemon support or changed ICMP behavior can produce failures unrelated to mlxsw. Route and neighbor cleanup must be exact to avoid influencing later tests.

## Test Signals

Signals include trap action checks, `devlink_trap_exception_test`, ICMP ingress TC hits for MTU/TTL cases, and per-test `log_test` outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_l3_exceptions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_policer.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_policer.sh

## Purpose

Validation of mlxsw devlink trap policer configuration limits and runtime policing behavior.

## Important APIs, Types, and Functions

Creates a routed IPv4 topology with large MTUs and a blackhole route whose trap action is set to `trap`. Key functions are `rate_limits_test`, `burst_limits_test`, `trap_rate_get`, `policer_drop_rate_get`, `rate_test`, and `burst_test`. It uses `devlink trap policer set`, trap and policer statistics, mausezahn traffic, and deferred cleanup helpers from the forwarding library.

## Control Flow

Setup reloads devlink to reset trap settings, prepares VRFs, raises MTUs, configures router ports, adds a blackhole route, and traps `blackhole_route`. Limit tests try invalid and boundary policer rate/burst values. Runtime tests set policer parameters, generate traffic toward the blackhole destination, sample accepted trap rate and policer drop rate over time, and check that configured rate/burst materially affect observed counters.

## State and Persistence Behavior

State includes devlink trap policer rate/burst values, blackhole route, MTU changes, trap action, VRFs, and background traffic. The script uses `defer` extensively so state unwinds even from mid-test failure.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Rate assertions are timing-sensitive and depend on CPU scheduling, traffic generator stability, hardware counter update cadence, and default policer indexing. Boundary values are mlxsw ABI assumptions; firmware changes can shift limits. Devlink reload can disrupt unrelated device state if run on a shared test system.

## Test Signals

Signals are explicit pass/fail for rejected invalid values, accepted min/max values, measured trap packet rate, measured policer drop rate, and `log_test` entries for rate and burst behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_policer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_ipip.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_ipip.sh

## Purpose

IPv4-under-IPv4 IPIP decapsulation error trap tests for mlxsw tunnel offload.

## Important APIs, Types, and Functions

Defines a four-netif topology with H1, a switch underlay/overlay side, and VRF2. Helpers create tunnel-facing routes and produce raw IPIP payloads. Tests are organized under `decap_error_test`, combining `ecn_decap_test` and `no_matching_tunnel_test`, and use `devlink_trap_drop_test`, TC filters, mausezahn, and generated byte payloads.

## Control Flow

Setup configures H1 and switch ports with underlay/overlay routes, creates VRF2, enables forwarding, and installs clsact filters. The ECN case sends encapsulated packets whose outer/inner ECN combination should fail decapsulation. The no-matching-tunnel case sends valid-looking IPIP traffic that should not match an installed decap tunnel. Both paths assert the relevant trap and cleanup filters/processes.

## State and Persistence Behavior

State is limited to VRFs, tunnel-related routes, forwarding sysctls, TC filters, and devlink trap statistics/actions. Payload generation is function-local and no persistent files are created.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Raw payload constants must match kernel parser expectations. Neighbor or route setup races can turn a decap error into an ordinary forwarding miss. The tests are sensitive to offload support for IPIP and to exact devlink trap names for tunnel decap failures.

## Test Signals

Signals are devlink drop-trap hits, TC egress/ingress packet counters for generated traffic, and successful cleanup of background mausezahn processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_ipip.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_ipip6.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_ipip6.sh

## Purpose

IPv6-under-IPv4 or IPv6 IPIP tunnel decapsulation error trap tests for mlxsw.

## Important APIs, Types, and Functions

This is the IPv6-flavored counterpart of the IPIP tunnel trap test. It defines H1/VRF2/switch setup, `ipip_payload_get`, `ecn_payload_get`, `ecn_decap_test`, `no_matching_tunnel_test`, and top-level `decap_error_test`, using forwarding helpers, `tc_common.sh`, and `devlink_lib.sh`.

## Control Flow

The control flow mirrors the IPv4 IPIP test: create underlay and overlay reachability, install TC filters, generate crafted encapsulated packets, and assert that invalid ECN or missing tunnel state increments the decap-error trap instead of being forwarded. Cleanup removes filters, VRFs, routes, and traffic processes.

## State and Persistence Behavior

The script mutates only runtime network namespace/device state: VRFs, addresses, routes, filters, forwarding toggles, and devlink counters. It does not persist test artifacts.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The main risk is protocol ambiguity: small payload construction changes can make the packet fail earlier or later than the expected mlxsw trap. IPv6 route and neighbor state must be stable before packet injection. Counter idle tests can race with slow hardware updates.

## Test Signals

Signals are `devlink_trap_drop_test` success for decap-error cases and absence of lingering traffic or filters after cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_ipip6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_vxlan.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_vxlan.sh

## Purpose

VXLAN IPv4 tunnel decapsulation trap tests for malformed VXLAN and multicast overlay source MAC packets.

## Important APIs, Types, and Functions

Builds a VXLAN-capable topology and defines payload builders for ECN mismatch, reserved VXLAN bits, short VXLAN packets, corrupted packets, and multicast source MAC. Top-level tests are `decap_error_test` and `overlay_smac_is_mc_test`, using `devlink_trap_drop_test`, TC filters, and mausezahn raw payload injection.

## Control Flow

Setup creates H1, switch ports, a VRF for overlay routing, and VXLAN-related addressing. `decap_error_test` runs several malformed payload checks that should hit decap-error traps. `overlay_smac_is_mc_test` sends an encapsulated Ethernet frame with multicast SMAC and verifies the separate overlay SMAC trap. Cleanup tears down VXLAN/VRF state and filters.

## State and Persistence Behavior

Runtime state includes VXLAN devices, bridge or VRF memberships, routes, TC clsact filters, trap actions/stats, and background traffic.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Malformed-packet tests are brittle by design: if VXLAN parser validation order changes, a packet may hit a different trap. VXLAN offload requires exact options such as checksum behavior and UDP port. Multicast SMAC tests depend on the inner frame being decapsulated far enough to inspect the overlay Ethernet header.

## Test Signals

Signals are per-payload trap hits, TC packet counters, and `log_test` results for decap errors and overlay multicast SMAC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_vxlan.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_vxlan_ipv6.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_vxlan_ipv6.sh

## Purpose

VXLAN IPv6 tunnel decapsulation trap tests for malformed IPv6-underlay VXLAN traffic.

## Important APIs, Types, and Functions

This mirrors the IPv4 VXLAN trap suite but uses IPv6 underlay addresses and IPv6 payload encodings. It defines H1/switch/VRF setup, ECN/reserved-bits/short/corrupted payload generators, `decap_error_test`, `mc_smac_payload_get`, and `overlay_smac_is_mc_test`.

## Control Flow

Setup prepares IPv6 reachability and VXLAN decap context, then tests malformed VXLAN traffic by injecting crafted frames and checking devlink trap counters. The overlay SMAC case verifies that a multicast source MAC inside a decapsulated VXLAN packet is classified as the `overlay_smac_is_mc` drop.

## State and Persistence Behavior

State is kernel networking state only: IPv6 addresses, routes, VXLAN devices, VRFs, TC filters, trap counters/actions, and traffic PIDs.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

IPv6 neighbor discovery, parser ordering, and VXLAN option support are common failure causes. Tests can be flaky if hardware counters lag traffic generation or if the IPv6 underlay route is not fully resolved before injection.

## Test Signals

Signals are successful devlink drop-trap checks for malformed VXLAN packets and multicast overlay source MAC, with TC counters confirming traffic reached the observed point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_vxlan_ipv6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/egress_vid_classification.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/egress_vid_classification.sh

## Purpose

Tests that egress VID classification selects the correct bridge RIF independent of configuration order.

## Important APIs, Types, and Functions

Creates three hosts and a switch bridge/RIF topology with VLAN 10 and an external routed VLAN subinterface. Helpers `bridge_rif_add`, `bridge_rif_del`, `port_vid_map_rif`, and `rif_port_vid_map` use devlink RIF occupancy and TC flower counters to validate hardware routing.

## Control Flow

Setup builds VRFs, host VLAN subinterfaces, a bridge with controlled IPv6 address generation, switch VLAN devices, neighbor entries, and egress clsact filters. One test creates the port-VID to FID mapping before adding the bridge RIF; the other adds the RIF first and then the mapping. Both ping across the routed boundary and require hardware-forwarded TC hits.

## State and Persistence Behavior

State includes VLAN devices, bridge membership, bridge IP address/RIF allocation, neighbor entries, routes, TC filters, and devlink `rifs` resource occupancy. Cleanup reverses each component.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The test depends on accurate RIF occupancy accounting and on neighbor prepopulation to avoid a first software-forwarded packet. Configuration-order bugs can be masked if TC counters are not offloaded or if routes resolve through software.

## Test Signals

Signals are devlink `rifs` occupancy increasing by one after bridge address addition and TC `skip_sw` packet counts during pings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/egress_vid_classification.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ethtool_lanes.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ethtool_lanes.sh

## Purpose

Validates mlxsw support for ethtool lane selection with autonegotiation and forced link modes.

## Important APIs, Types, and Functions

Uses `lib.sh` and shared `ethtool_lib.sh`. Important helpers are `check_lanes`, `check_unsupported_lanes`, `max_speed_and_lanes_get`, `search_linkmode`, `autoneg`, and `autoneg_force_mode`. It queries supported link modes, maximum speed/lane combinations, and applies ethtool settings on paired ports.

## Control Flow

Setup maps two netifs, brings them into a usable state, and reads driver-reported lane data. The autoneg test searches for matching advertised modes and verifies lane counts. The forced-mode test selects a concrete speed/lane link mode and checks both accepted and unsupported lane requests.

## State and Persistence Behavior

State consists of ethtool link-mode/autoneg settings on the test ports. Cleanup is mostly inherited from shared helpers and relies on the test environment restoring link settings between runs.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It additionally depends on the ethtool selftest helper library.

## Risks and Edge Cases

Risk comes from hardware module capabilities, link partner behavior, supported mode naming, and lane reporting differences across Spectrum generations. A port without matching supported modes can produce skips or false failures.

## Test Signals

Signals are accepted ethtool configuration changes for supported lane counts, rejected unsupported lane counts, and final lane/speed checks from ethtool output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ethtool_lanes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/extack.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/extack.sh

## Purpose

Checks that mlxsw returns driver-specific extended acknowledgements for unsupported netdev/bridge/VXLAN configurations.

## Important APIs, Types, and Functions

Defines `netdev_pre_up_test`, `vxlan_vlan_add_test`, `vxlan_bridge_create_test`, and `bridge_create_test`. It uses plain `ip link` and `bridge vlan` commands, captures stderr/stdout, and greps for `mlxsw_spectrum` in extack messages.

## Control Flow

Setup creates two switch ports and disables IPv6 address generation. Tests intentionally build unsupported scenarios: bringing up a VXLAN/bridge configuration before valid mlxsw constraints, adding VLANs on unsupported VXLAN devices, enslaving ports into bridge/VXLAN combinations, and trying multiple VLAN-aware bridges. Each negative operation must fail and include mlxsw extack text.

## State and Persistence Behavior

State includes temporary bridges, VXLAN devices, port masters, and link up/down state. Cleanup deletes created devices and restores ports.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

These are negative tests, so command failure alone is insufficient; the extack text must survive shell redirection and include the expected driver marker. Kernel message wording changes can fail the grep despite correct rejection behavior. Cleanup must delete partially created VXLAN/bridge devices.

## Test Signals

Signals are `check_fail` for unsupported operations, successful grep for `mlxsw_spectrum`, and per-case `log_test` messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/extack.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/fib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/fib.sh

## Purpose

Wraps shared FIB offload API tests for mlxsw and adds local-table replacement cases.

## Important APIs, Types, and Functions

Sources `fib_offload_lib.sh` and exposes many `ALL_TESTS` wrappers for IPv4/IPv6 add, metric, TOS, replace, delete, prefix length, replay, flush, multipath append/replace/delete, and local replacement. It adds `ipv4_local_replace`, `ipv6_local_replace`, and a `fib_notify_on_flag_change_set` setup path.

## Control Flow

With zero physical netifs, setup creates namespaces and enables FIB notification behavior through shared helpers. Most test functions delegate to generic library routines with namespace `testns1` and `$DEVLINK_DEV`. Local replacement tests create dummy interfaces, install local and main-table routes for the same host prefixes, and verify which routes carry offload/trap flags.

## State and Persistence Behavior

State is namespace-local routes, dummy interfaces, devlink reload/replay state, and kernel FIB offload flags. It does not change source files.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It specifically integrates with `fib_offload_lib.sh` for most assertions.

## Risks and Edge Cases

The suite is sensitive to route flag timing and route-table precedence. Local-table and main-table interactions are subtle; stale dummy routes can contaminate later checks. Replay tests depend on devlink reload preserving and reprogramming route offload state.

## Test Signals

Signals are `fib4_trap_check`/`fib6_trap_check` outcomes, shared FIB library assertions, and successful route replay after devlink operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/fib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/fib_offload.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/fib_offload.sh

## Purpose

Tests IPv6 route offload indication on mlxsw for prefix, multipath, replacement, shared nexthop group, and insertion-rate cases.

## Important APIs, Types, and Functions

Defines TOR/spine topology helpers, `ipv6_offload_check`, route add/replace helpers, `ipv6_route_nexthop_group_share`, and `ipv6_route_rate`. It inspects `ip -6 route show` output for `offload` flags after route operations.

## Control Flow

Setup creates two TOR host ports and two spine router ports with IPv6 /64 links. Tests add prefix and multipath routes with different metrics and nexthops, append and replace them, ensure only the best metric is offloaded, and verify route flags after shared nexthop-group changes. The rate test stresses rapid route additions and checks eventual offload indication.

## State and Persistence Behavior

State consists of IPv6 addresses, route table entries, multipath nexthops, and device offload flags. Cleanup flushes test routes and tears down the topology.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Assertions rely on textual `ip route` output and a short sleep to avoid offload races. Slow hardware programming can make route flags appear late. Multipath replacement semantics in iproute2/kernel can append rather than replace in some cases, which the test intentionally documents and validates.

## Test Signals

Signals are counts from `ipv6_offload_check`, successful route flushes, and per-test `log_test` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/fib_offload.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/hw_stats_l3.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/hw_stats_l3.sh

## Purpose

Minimal mlxsw L3 hardware statistics monitor test.

## Important APIs, Types, and Functions

Uses `hw_stats_monitor_test` from `lib.sh` with a cableless switch port (`NETIF_NO_CABLE`). The sole test, `l3_monitor_test`, toggles an IPv4 address on the port while monitoring L3 hardware statistics support.

## Control Flow

There is no topology setup beyond `setup_wait`. The test invokes the shared monitor helper with an address-add command and matching address-delete command, then relies on the helper to observe the expected hardware statistics events or state changes.

## State and Persistence Behavior

State is limited to adding and removing `192.0.2.1/28` on the selected switch port and any monitor process started by the helper.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Because the file is tiny and delegates almost all behavior, failures usually point to shared helper behavior, unavailable `NETIF_NO_CABLE`, unsupported L3 stats, or address cleanup failure.

## Test Signals

Signals are the shared `hw_stats_monitor_test` result and the kselftest exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/hw_stats_l3.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ingress_rif_conf_1d.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ingress_rif_conf_1d.sh

## Purpose

Tests ingress RIF configuration order for VLAN subinterfaces enslaved to a VLAN-unaware bridge.

## Important APIs, Types, and Functions

Creates H1/H2/H3 VLAN 10 hosts, switch VLAN devices, bridge `br0`, a routed switch VLAN toward H3, and helpers `bridge_rif_add`, `bridge_rif_del`, `port_vid_map_rif`, and `rif_port_vid_map`. It uses devlink RIF occupancy and TC hardware counters.

## Control Flow

Setup disables automatic IPv6 address generation on the bridge, prepares host VLAN interfaces and routes, creates switch VLAN mappings, and preloads a neighbor to avoid software forwarding. One test adds a port-VID mapping before bridge RIF creation; the other creates the RIF before adding the mapping. Both ping H3 from H1.10 and require hardware TC hits on SWP3.

## State and Persistence Behavior

State includes bridge/VLAN interfaces, bridge RIF address, RIF resource occupancy, routes, neighbor entries, and TC filters. Cleanup deletes VLANs, bridge, filters, routes, and VRFs.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Order-sensitive bugs can be hidden by neighbor misses or software forwarding, hence the explicit neighbor replacement and `skip_sw` counters. RIF occupancy checks depend on devlink resource accounting settling after address changes.

## Test Signals

Signals are one new RIF after bridge address addition and TC `skip_sw` egress packet counts during routed pings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ingress_rif_conf_1d.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ingress_rif_conf_1q.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ingress_rif_conf_1q.sh

## Purpose

Tests ingress RIF configuration order for VLAN-aware bridge VID to FID mappings.

## Important APIs, Types, and Functions

The file mirrors the ingress RIF ordering pattern for a VLAN-aware bridge. It defines `vid_map_rif`, `rif_vid_map`, bridge RIF helpers, host/switch setup, and TC/devlink checks.

## Control Flow

Setup creates VLAN 10 endpoints and a VLAN-aware bridge, controls bridge address generation, configures a routed switch-facing VLAN path, and installs TC counters. Tests exercise both orders: VID mapping before RIF and RIF before VID mapping. Each test validates that packets route in hardware after the final configuration is complete.

## State and Persistence Behavior

State includes bridge VLAN database entries, bridge IP/RIF state, host VLAN interfaces, neighbor entries, route entries, and TC filters.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The test is susceptible to bridge VLAN default PVID behavior, neighbor resolution, and timing of RIF creation after address addition. Any failure to remove VLAN entries can affect the second order test.

## Test Signals

Signals are devlink `rifs` occupancy deltas and TC `skip_sw` packet counts for successful hardware routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ingress_rif_conf_1q.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ingress_rif_conf_vxlan.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ingress_rif_conf_vxlan.sh

## Purpose

Tests ingress RIF behavior when VXLAN VNI-to-FID mappings are created before or after a VLAN RIF.

## Important APIs, Types, and Functions

Defines H1, switch VXLAN bridge, VRF/routed port setup, raw payload generation, `vlan_rif_add`, `vlan_rif_del`, `vni_fid_map_rif`, and `rif_vni_fid_map`. It uses VXLAN devices, bridge VLANs, TC counters, and devlink RIF occupancy.

## Control Flow

Setup creates a VXLAN tunnel/bridge context and a routed VRF port, then tests two configuration orders: create VNI/FID mapping then add the VLAN RIF, and add the RIF then create VNI/FID mapping. Crafted payloads are injected to prove decapsulated traffic is routed through the correct RIF in hardware.

## State and Persistence Behavior

State includes VXLAN devices, bridge/VLAN/VNI mappings, VRF and routes, TC filters, devlink RIF counters, and temporary payload traffic.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

VXLAN offload constraints are strict; wrong checksum, bridge, or VNI settings can make the test fail before RIF classification. Raw payload construction and neighbor state are also fragile. Cleanup must remove tunnel devices and bridge mappings in reverse order.

## Test Signals

Signals are RIF occupancy after VLAN RIF addition and TC counter hits showing routed decapsulated packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ingress_rif_conf_vxlan.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/mirror_gre.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/mirror_gre.sh

## Purpose

Functional GRE mirror offload tests for keyful and software GRE modes, TOS, TTL, and failure handling.

## Important APIs, Types, and Functions

Sources `mirror_lib.sh`, `mirror_gre_lib.sh`, and `mirror_gre_topo_lib.sh`. It defines setup/cleanup for keyful and software variants, `test_span_gre_ttl_inherit`, `test_span_gre_tos_fixed`, `test_span_failable`, and wrapper tests `test_keyful`, `test_soft`, `test_tos_fixed`, and `test_ttl_inherit`.

## Control Flow

Setup prepares a six-netif mirror topology with hosts, bridge/switch ports, and GRE tunnel endpoints. Each test configures a mirror action from ingress traffic into a GRE/gretap tunnel, injects traffic, and checks captured mirrored packets for expected key, TOS, TTL, or failure behavior. Cleanup removes mirror filters, tunnels, and topology state.

## State and Persistence Behavior

State includes GRE tunnel devices, bridge membership, TC mirror actions, routes/addresses, and capture filters created by shared mirror helpers.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It relies heavily on the forwarding mirror helper libraries for topology and packet validation.

## Risks and Edge Cases

Risk is concentrated in tunnel option support and capture interpretation. GRE key support, inherited TTL/TOS handling, and offload failure paths vary by kernel and device revision. Shared helper cleanup must remove all TC mirror rules.

## Test Signals

Signals are mirror helper pass/fail results, packet capture checks on GRE tunnel endpoints, and `log_test` wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/mirror_gre.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/mirror_gre_scale.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/mirror_gre_scale.sh

## Purpose

Scale helper for offloading many IPv6 gretap mirror sessions on mlxsw.

## Important APIs, Types, and Functions

This file is intended to be sourced by scale wrappers. It defines `MIRROR_NUM_NETIFS`, IPv6 address generation, `mirror_gre_tunnels_create`, `mirror_gre_tunnels_destroy`, `mirror_gre_test`, `mirror_gre_setup_prepare`, and `mirror_gre_cleanup`. It uses `mirror_lib.sh`, `tunnel_create`, `matchall_sink_create`, batched `tc`, and `mirror_test`.

## Control Flow

Setup creates a bridge with SWP1/SWP2 and a routed SWP3/H3 tunnel side. For each count entry, it creates host and tunnel IPv6 addresses, paired ip6gretap tunnels, a sink on the remote tunnel, and a TC flower mirror rule matching a unique destination. The test sends traffic for each destination and verifies it appears on the matching tunnel.

## State and Persistence Behavior

State includes many IPv6 addresses, ip6gretap tunnel devices, TC mirror filters in a temp batch file, bridge membership, VRFs, and a tunnel count used for cleanup.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Scale failures can reflect resource exhaustion, TC batch partial success, or cleanup order rather than a single mirror bug. Address generation must avoid collisions. If `should_fail` is set, the test must return immediately after expected insertion failure.

## Test Signals

Signals are TC batch insertion status, per-tunnel mirror packet captures, and cleanup destroying the exact number of created tunnels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/mirror_gre_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/mlxsw_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/mlxsw_lib.sh

## Purpose

Shared mlxsw-specific helper library for Spectrum revision gating and descriptor limits.

## Important APIs, Types, and Functions

Initializes `MLXSW_CHIP` from `devlink dev info`, derives `MLXSW_SPECTRUM_REV`, and exports `mlxsw_on_spectrum`, `__mlxsw_only_on_spectrum`, `mlxsw_only_on_spectrum`, and `mlxsw_max_descriptors_get`. It integrates with kselftest logging through `log_test_xfail`.

## Control Flow

When sourced, the file detects the running mlxsw driver/revision. Tests can call `mlxsw_only_on_spectrum` with revisions such as `2` or `3+` to xfail unsupported hardware, or call `mlxsw_max_descriptors_get` to obtain expected descriptor-pool sizes per Spectrum generation.

## State and Persistence Behavior

State is shell-global: `MLXSW_CHIP` and `MLXSW_SPECTRUM_REV` variables. It performs no persistent device changes.

## Dependencies and Integration Points

Depends on `$DEVLINK_DEV`, `devlink -j`, `jq`, bash arithmetic, and the caller's test logging functions.

## Risks and Edge Cases

Unknown driver strings or new Spectrum revisions cause stderr messages or failures until the mapping is updated. Because it exits on missing devlink info during sourcing, callers need a valid devlink-capable mlxsw device.

## Test Signals

Signals are correct revision comparison, xfail logging on unsupported hardware, and descriptor constants matching firmware/hardware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/mlxsw_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/one_armed_router.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/one_armed_router.sh

## Purpose

One-armed router test proving bridge RIF forwarding and forwarding-mark behavior for IPv4 and IPv6.

## Important APIs, Types, and Functions

Creates H1/H2 VRFs connected to two switch ports enslaved to one bridge with multiple router addresses. Tests are `ping_ipv4`, `ping_ipv6`, `fwd_mark_ipv4`, and `fwd_mark_ipv6`. It uses TC `skip_hw`/`skip_sw` counters and mausezahn UDP traffic.

## Control Flow

Setup disables redirects, enables forwarding, creates a bridge with the SWP1 MAC, enslaves both switch ports, assigns both subnets to the bridge RIF, and installs clsact on both ports. Ping tests validate basic reachability. Forwarding-mark tests inject UDP packets that are trapped at ingress because of loopback error but must be hardware-forwarded through the egress port, not software-forwarded.

## State and Persistence Behavior

State includes bridge/RIF addresses, VRFs, routes, sysctls for redirects, TC filters, and generated traffic. Cleanup removes filters, bridge, routes, sysctls, forwarding, and VRFs.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The test relies on loopback-error trapping while preserving ASIC forwarding metadata. TC counter interpretation is subtle: ingress `skip_hw` should see trapped packets, egress `skip_sw` should see hardware-forwarded packets, and egress `skip_hw` should stay zero for software forwarding.

## Test Signals

Signals are IPv4/IPv6 ping success and three TC counter checks per protocol proving trap plus hardware forwarding behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/one_armed_router.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/pci_reset.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/pci_reset.sh

## Purpose

PCI reset validation for mlxsw ports and devlink device behavior.

## Important APIs, Types, and Functions

Defines a single `pci_reset_test` using one netif plus `devlink_lib.sh`. The file checks supported reset methods and verifies that the port ifindex changes after issuing the reset.

## Control Flow

The test records the initial port identity/ifindex, inspects reset method exposure, triggers the supported PCI reset path, waits for the device/port to reappear, and compares the resulting ifindex with the original. A changed ifindex indicates the netdevice was recreated as expected.

## State and Persistence Behavior

State includes transient PCI/device reset state and recreated netdevice identity. It may disrupt live networking on the tested adapter and relies on kselftest cleanup/wait helpers after reset.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

This is disruptive and must run only on a dedicated test device. Reset support depends on PCI/firmware/kernel capabilities. If udev or device recreation is slow, the ifindex check can race.

## Test Signals

Signals are expected reset method filtering, successful reset command, and observed ifindex change after the reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/pci_reset.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/port_range_occ.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/port_range_occ.sh

## Purpose

Resource occupancy test for mlxsw ACL port-range entries.

## Important APIs, Types, and Functions

Defines a two-netif topology with clsact on SWP1, helper `port_range_occ_get`, and `port_range_occ_test`. It uses `devlink_resource_occ_get` and TC flower rules with UDP destination port ranges.

## Control Flow

Setup creates simple H1/SWP1 interfaces and clsact. The test records port-range resource occupancy, inserts an offloaded flower rule containing a port range, checks that occupancy increases, removes the rule, and verifies occupancy returns to the previous value.

## State and Persistence Behavior

State includes one TC ingress filter, clsact qdisc, simple interface state, and devlink resource counters.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The assertion depends on devlink exposing the correct resource name and updating occupancy promptly. If the TC rule is not offloaded, resource occupancy may not change. Cleanup must remove the filter before checking final occupancy.

## Test Signals

Signals are devlink occupancy deltas and TC insertion/removal success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/port_range_occ.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/port_range_scale.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/port_range_scale.sh

## Purpose

Scale helper for inserting many offloaded flower rules with expanding UDP destination port ranges.

## Important APIs, Types, and Functions

This sourced helper defines `PORT_RANGE_NUM_NETIFS`, setup/cleanup, `port_range_rules_create`, `__port_range_test`, and `port_range_test`. It writes a temporary TC batch file containing `flower skip_sw ip_proto udp dst_port 1-N` rules.

## Control Flow

Setup prepares H1/SWP1 and clsact. The test first checks offload capability, then inserts the requested rule count, optionally expecting failure. It reads `tc -j filter show` and counts filters with `options.in_hw == true` to ensure the offload count matches the requested count.

## State and Persistence Behavior

State includes a temp batch file, many TC ingress filters, clsact qdisc, VRF/simple interface state, and JSON parsed TC state.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Partial batch insertion can make counts differ from both success and failure expectations. JSON shape from `tc -j` is assumed. Port-range resource limits vary by ASIC and profile, so callers must pass the correct `count` and `should_fail` values.

## Test Signals

Signals are TC batch exit status and JSON offload count equality, with `check_err_fail` handling expected-failure lanes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/port_range_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/port_scale.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/port_scale.sh

## Purpose

Scale helper for mlxsw physical port resource exhaustion via devlink port splitting.

## Important APIs, Types, and Functions

Defines `PORT_NUM_NETIFS`, an `unsplit` array, `split_all_ports`, `port_test`, and cleanup that unsplits created ports. It reads splittable ports from `devlink -j port show` and checks `physical_ports` resource occupancy.

## Control Flow

The helper loops over all splittable netdevs, splits each to its lane count, tracks the new split base port for cleanup, then reads devlink resource occupancy and compares it with the expected maximum. Cleanup unsplits all tracked ports.

## State and Persistence Behavior

State is disruptive device port split state and the shell `unsplit` array. It persists at the device level until cleanup or manual unsplit succeeds.

## Dependencies and Integration Points

Depends on `devlink`, `jq`, `$DEVLINK_DEV`, and a device whose ports are splittable. It is normally invoked by hardware-specific wrappers that pass expected maxima.

## Risks and Edge Cases

Port splitting can rename or recreate netdevices and can fail if links are in use. Cleanup references a variable in the error message that may not be set, but the unsplit command uses tracked port names. Wrong expected max values create false failures across hardware revisions.

## Test Signals

Signals are successful split commands and `physical_ports` occupancy equaling the expected maximum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/port_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/q_in_q_veto.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/q_in_q_veto.sh

## Purpose

Negative tests ensuring mlxsw rejects unsupported 802.1ad/Q-in-Q configurations with extack text.

## Important APIs, Types, and Functions

Defines twelve tests covering creation of 802.1ad VLAN uppers on front-panel ports, bridge ports, LAGs, 802.1Q and 802.1ad bridges, VLAN uppers on 802.1ad bridges, enslaving ports/LAGs with VLAN uppers to 802.1ad bridges, adding IP to 802.1ad bridges, and switching a bridge from 802.1Q to 802.1ad.

## Control Flow

Setup brings two switch ports up. Each test constructs an unsupported bridge/VLAN/LAG topology, performs an operation that should fail, then repeats it while checking stderr/stdout for `mlxsw_spectrum` extack text. Temporary devices are deleted before the next case.

## State and Persistence Behavior

State includes temporary bridges, bonds, VLAN uppers, port masters, and link state. It intentionally avoids persistent configuration by deleting each topology in-test.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The suite is sensitive to extack wording and shell redirection. Because operations are negative, a kernel allowing a formerly unsupported topology is reported as failure. Cleanup of partially created bonds/VLANs is critical to avoid cascading failures.

## Test Signals

Signals are `check_fail` on unsupported operations, grep success for mlxsw extack, and `log_test` for each veto scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/q_in_q_veto.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_defprio.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_defprio.sh

## Purpose

QoS default priority test for bridged traffic on mlxsw.

## Important APIs, Types, and Functions

Creates a two-netif bridge-like topology with H1 and SWP1 and defines `ping_ipv4`, `__test_defprio`, and `test_defprio`. It uses `ip link` VLAN priority maps or traffic-class counters through shared helpers.

## Control Flow

Setup initializes host/switch interfaces and forwarding context. The ping test confirms reachability. The default-priority test changes default priority handling, sends traffic, and verifies packets are accounted in the expected priority/queue path before restoring defaults.

## State and Persistence Behavior

State is limited to link priority/QoS settings, simple interface state, routes, and temporary counters.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Default priority behavior is affected by VLAN tagging, ingress/egress qos maps, and driver defaults. Counter assertions can fail if previous tests leave priority maps or if traffic is classified before the setting takes effect.

## Test Signals

Signals are ping success and counter/log checks in `test_defprio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_defprio.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_dscp_bridge.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_dscp_bridge.sh

## Purpose

DSCP-to-priority QoS classification test for bridged mlxsw traffic.

## Important APIs, Types, and Functions

Defines H1/H2 bridge setup, `ping_ipv4`, `dscp_ping_test`, and `test_dscp`. It uses IPv4 ping/traffic with selected DSCP values and observes priority counters or forwarding behavior through the shared library.

## Control Flow

Setup creates two hosts connected through switch bridge ports. `dscp_ping_test` sends traffic with chosen DSCP values and validates the expected priority mapping. `test_dscp` runs the configured DSCP cases after confirming basic connectivity.

## State and Persistence Behavior

State includes bridge membership, addresses/routes, DSCP/prio maps, and interface counters. Cleanup removes bridge and host state.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Results depend on DSCP preservation across the bridge path and on the driver's current DSCP-to-priority map. Any previous QoS map changes can leak into this test if cleanup fails.

## Test Signals

Signals are successful ping and per-DSCP classification checks in `test_dscp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_dscp_bridge.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_dscp_router.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_dscp_router.sh

## Purpose

DSCP rewrite and priority behavior tests for routed mlxsw traffic.

## Important APIs, Types, and Functions

Defines reprioritization helpers `zero` and `three`, H1/H2 routed setup, `dscp_ping_test`, `test_update`, `test_no_update`, `test_pedit_norewrite`, and `test_dscp_leftover`. It uses route forwarding plus DSCP and pedit behavior.

## Control Flow

Setup creates two routed host interfaces and switch router ports. The tests send DSCP-marked traffic through the router, optionally apply reprioritization or pedit-style modifications, and check whether DSCP-derived priority is updated, left unchanged, or cleared as expected.

## State and Persistence Behavior

State includes router addresses/routes, QoS/DSCP maps, pedit or prioritization rules, counters, and forwarding sysctls.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The tricky cases are update-vs-no-update and leftover DSCP state after edits. Hardware may classify before or after rewrite depending on pipeline behavior, so the expected results encode mlxsw-specific semantics.

## Test Signals

Signals are ping reachability and classification checks from `dscp_ping_test` under each named scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_dscp_router.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_ets_strict.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_ets_strict.sh

## Purpose

ETS strict-priority scheduler validation under mlxsw with measured traffic rates.

## Important APIs, Types, and Functions

Builds a six-netif topology, sources `qos_lib.sh`, and uses devlink pool helpers. Important functions are H1/H2/H3 setup, `switch_create`, `rel`, `run_hi_measure_rate`, and `test_ets_strict`.

## Control Flow

Setup configures hosts, switch ports, ETS qdiscs, traffic priorities, shaping, and devlink buffer/pool state. The test measures baseline and high-priority rates, then verifies strict scheduling behavior by comparing relative throughput while competing traffic is present.

## State and Persistence Behavior

State includes ETS qdisc hierarchy, VLAN priority maps, shapers, devlink pool thresholds, bridge/routing setup, and traffic generator processes.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It also depends on `qos_lib.sh` rate measurement helpers.

## Risks and Edge Cases

Throughput assertions are inherently noisy and require stable link speed, no external traffic, and correct shaper operation. Hardware generation differences can require xfail gating. Cleanup must remove qdiscs and restore devlink thresholds.

## Test Signals

Signals are ping success, measured rates above expected thresholds, relative-rate checks, and `log_test` for strict ETS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_ets_strict.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_headroom.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_headroom.sh

## Purpose

DCB headroom and buffer-size validation for mlxsw lossless/lossy priority groups and TC qdisc mode.

## Important APIs, Types, and Functions

With zero cabled netifs, selects `$NETIF_NO_CABLE` and defines getters/checkers for priority-to-PG/PFC/TC mapping, buffer size, total buffer size, and tests for defaults, DCB ETS, MTU, TC MTU, PFC, TC priority map, TC sizes, internal buffers, and TC internal buffers.

## Control Flow

Each test applies DCB ETS/PFC or TC qdisc configuration, reads DCB buffer state and devlink cell size/total buffer data, and checks expected size/mapping relationships. PFC cases turn priorities 5-7 lossless and vary cable delay. Internal buffer tests add SPAN/mirror qdiscs and ensure invisible buffer accounting changes and restores correctly.

## State and Persistence Behavior

State includes DCB ETS/PFC settings, DCB buffer sizes, MTU changes, TC qdisc roots/clsact filters, mirred actions, and devlink buffer accounting. Cleanup calls `pre_cleanup` and individual tests restore their settings.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

This suite is sensitive to cell-size rounding, hardware headroom formulas, port lane count, DCB tool behavior, and hidden internal buffers. Missing restore after an early failure can affect many later QoS tests.

## Test Signals

Signals are exact or relational `check_*` assertions for priority maps and buffer sizes, plus `log_test` messages for each buffer/headroom scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_headroom.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_lib.sh

## Purpose

Small shared QoS measurement helper library.

## Important APIs, Types, and Functions

Exports `check_rate` and `measure_rate`. `check_rate` compares measured ingress/egress rates against expectations, while `measure_rate` samples ethtool byte counters over time and returns human-readable or numeric throughput values for callers.

## Control Flow

Callers pass devices, counters, and labels. The helpers sample counters, sleep, calculate rates with `bc`/shell arithmetic, and report errors through kselftest `check_err` style functions.

## State and Persistence Behavior

State is invocation-local except for reading interface counters. It does not modify network configuration.

## Dependencies and Integration Points

Depends on ethtool-stat helper functions from the broader forwarding library, `sleep`, arithmetic tools, and caller-provided logging/check functions.

## Risks and Edge Cases

Counter wrap, low traffic volume, or asynchronous counter updates can skew rates. The helpers assume the named counters exist on the target devices and that no unrelated traffic contaminates measurements.

## Test Signals

Signals are returned rate values and caller-visible check failures when measured throughput falls outside expected bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_max_descriptors.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_max_descriptors.sh

## Purpose

Validates that mlxsw descriptor pool configuration can absorb a large shaped egress burst without unexpected descriptor drops.

## Important APIs, Types, and Functions

Sources `mlxsw_lib.sh`, computes `MAX_POOL_SIZE`, and defines host/switch setup, `percentage_used`, and `max_descriptors`. It manipulates devlink pool sizes/thresholds, TC ETS/TBF qdiscs, DCB buffers, VLAN qos maps, bridges, and ethtool descriptor/drop counters.

## Control Flow

Setup creates VLAN 111 endpoints and bridge forwarding, enlarges ingress/egress pools, binds priority 1 to selected pools, shapes egress, and configures ETS. The test sends a burst, checks `tc_no_buffer_discard_uc_tc_1` does not increase, reads transmit queue bytes, and verifies descriptor usage percentage is high enough relative to expected capacity.

## State and Persistence Behavior

State includes large devlink pool/threshold changes, qdisc hierarchy, DCB buffer maps, VLAN interfaces, bridge state, and ethtool counters. `defer` restores pool and qdisc settings.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It relies on `mlxsw_max_descriptors_get` for ASIC-specific expectations.

## Risks and Edge Cases

Risk is high because pool sizes, descriptor accounting, and expected percentages are hardware/firmware-specific. Traffic size and shaper rate must be sufficient to pressure descriptors without causing unrelated drops.

## Test Signals

Signals are no increase in egress no-buffer discard counters and descriptor/transmit queue usage percentage meeting the expected threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_max_descriptors.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_mc_aware.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_mc_aware.sh

## Purpose

Tests multicast-aware buffer admission so multicast overload does not unduly degrade unicast traffic, and vice versa.

## Important APIs, Types, and Functions

Defines a six-netif topology with H1/H2/H3, bridge domains, VLAN 111, pool-threshold tuning, `run_uc_measure_rate`, `test_mc_aware`, and `test_uc_aware`. It uses mausezahn, ping/ARP, ethtool per-priority counters, TBF/prio qdiscs, and `qos_lib.sh`.

## Control Flow

Setup configures unicast and multicast/ARP traffic paths, maps traffic to distinct priorities, shapes the egress side, and deliberately makes ingress quotas smaller than egress quotas. `test_mc_aware` measures UC throughput with and without MC overload and checks degradation bounds. `test_uc_aware` sends broadcast ARPs while UC overload is present and verifies responses continue to pass.

## State and Persistence Behavior

State includes bridges, VLAN priority maps, qdiscs, devlink pool thresholds, per-priority counters, and traffic generator loops. Defer cleanup restores thresholds and qdiscs.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It uses `qos_lib.sh` for rate measurement.

## Risks and Edge Cases

Rate-based checks are noisy and can fail on slow links, non-isolated hardware, or counter drift. The intended degradation window is narrow, so shaper and pool configuration must be exact. ARP/broadcast behavior also depends on bridge learning and flooding state.

## Test Signals

Signals are measured ingress/egress UC and MC throughput, bounded degradation percentages, and successful ARP response counts under overload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_mc_aware.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_pfc.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_pfc.sh

## Purpose

End-to-end Priority Flow Control test for lossless traffic through overflow and PFC pools.

## Important APIs, Types, and Functions

Builds a six-netif topology and documents a two-stage path where priority-1 traffic fills a PFC pool, pauses an upstream port, and drains through shaped egress. It configures devlink pools 0/4, 1/5, 2/6, ETS qdiscs, DCB buffers/PFC, VLAN qos maps, bridges, and shapers.

## Control Flow

Setup creates H1/H2, four switch ports, VLAN 111, two bridge domains, static pool sizes, per-port pool thresholds, ETS scheduling, PFC on SWP3/SWP4, and headroom sizing that accounts for port lanes. The test sends a 10 MB priority-1 burst, samples ingress and egress priority counters, and checks that received bytes closely match sent bytes despite backpressure.

## State and Persistence Behavior

State is extensive runtime QoS state: devlink pool sizes/thresholds, DCB PFC and buffer settings, qdiscs, VLAN devices, bridges, shapers, and ethtool counters. Cleanup restores pools in reverse order and deletes qdiscs/bridges/VLANs.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

This is one of the most stateful scripts in the group. It is sensitive to cell-size rounding, lane count, shaper rate, pool sizing, pause behavior, and counter precision. Any missed restore can poison subsequent QoS tests.

## Test Signals

Signals are ping reachability, priority-1 ingress/egress byte deltas, percentage bounds for injected traffic, loss check between ingress and egress, and final `log_test PFC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_pfc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_bridge.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_bridge.sh

## Purpose

RIF lifecycle tests for a bridge backed by LAG ports on mlxsw.

## Important APIs, Types, and Functions

Creates two LACP team devices, a VLAN-aware bridge, enslaves LAG1 to the bridge, and attaches SWP1/SWP2 to LAGs. Tests cover bridge RIF add, LAG deslavement/remaster, address handling while enslaved, and physical port deslavement/remaster.

## Control Flow

Each test snapshots devlink `rifs` occupancy, changes address or master state, sleeps for propagation, and checks expected occupancy increase/decrease/no-change. The address test proves a LAG address does not create a separate RIF while enslaved but does when the LAG is removed from the bridge.

## State and Persistence Behavior

State includes team/LAG devices, bridge `br1`, switch-port masters, bridge and LAG addresses, and devlink RIF occupancy. Cleanup deletes teams and bridge and resets ports.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It requires teamd support through `REQUIRE_TEAMD=yes`.

## Risks and Edge Cases

Occupancy timing is asynchronous and guarded only by sleeps. LAG creation requires teamd and can fail in minimal environments. If a test changes master state and fails before restoration, later tests can see wrong baseline occupancy.

## Test Signals

Signals are exact `rifs` occupancy deltas for each lifecycle operation and `log_test` messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_bridge.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_counter_scale.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_counter_scale.sh

## Purpose

Scale helper for enabling and validating L3 hardware counters on many VLAN RIFs.

## Important APIs, Types, and Functions

Defines address generation helpers, H1/H2 setup, `rif_counter_test`, `rif_counter_traffic_test`, and cleanup. It creates many VLAN subinterfaces on H2, enables `l3_stats` in a batched `ip` file, then sends traffic to selected VLANs.

## Control Flow

Setup prepares two simple interfaces and VRFs. `rif_counter_test` creates `count` VLAN RIFs and batches `stats set dev ... l3_stats on`, optionally expecting failure. `rif_counter_traffic_test` sends UDP traffic to logarithmically selected VLANs and waits until the per-RIF hardware stats show one received packet.

## State and Persistence Behavior

State includes many VLAN devices, a temporary batch file, enabled per-RIF L3 stats, VRFs, and hardware counter state. Cleanup destroys VLANs and removes the temp file.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Large counts can exhaust RIF/counter resources or be slow to program. Address generation must remain unique for all counts. Hardware stats are asynchronous, so `busywait` timeout must match device update latency.

## Test Signals

Signals are batch enablement status and `hw_stats_get l3_stats <dev> rx packets` reaching one for sampled VLAN RIFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_counter_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_lag.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_lag.sh

## Purpose

RIF lifecycle tests for a standalone LAG netdevice.

## Important APIs, Types, and Functions

Creates a LACP team `lag1` with one switch port and tests `lag_rif_add`, `lag_rif_nomaster`, `lag_rif_remaster`, and `lag_rif_nomaster_addr` using devlink RIF occupancy.

## Control Flow

Setup creates the LAG, disables address generation, assigns the LAG MAC, and enslaves SWP1. Tests add an IP address to create a RIF, remove the physical port to drop the RIF, re-enslave the port to recreate it, and verify address/master interactions. Cleanup deletes the LAG and resets ports.

## State and Persistence Behavior

State includes team/LAG device, port master state, LAG IP addresses, and devlink RIF counters.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It requires teamd/LACP support.

## Risks and Edge Cases

Asynchronous RIF creation/destruction and teamd availability are main risks. Port down/up ordering matters when remastering. Leftover addresses can keep RIF occupancy elevated.

## Test Signals

Signals are expected RIF occupancy deltas after address addition, port deslavement, and port reenslavement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_lag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_lag_vlan.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_lag_vlan.sh

## Purpose

RIF lifecycle tests for VLAN subinterfaces on a LAG.

## Important APIs, Types, and Functions

This is the VLAN-on-LAG variant of `rif_lag.sh`. It creates a LAG, a VLAN upper, and tests RIF add/drop/remaster behavior for the VLAN RIF with `lag_rif_add`, `lag_rif_nomaster`, `lag_rif_remaster`, and `lag_rif_nomaster_addr`.

## Control Flow

Setup creates team/LAG state, enslaves the switch port, creates the VLAN upper, and disables uncontrolled address generation. Tests add addresses to the VLAN interface, remove/readd master relationships, and compare devlink RIF occupancy before and after each operation.

## State and Persistence Behavior

State includes team device, VLAN upper, switch-port master state, VLAN RIF address, and devlink RIF occupancy. Cleanup removes VLAN/LAG and restores ports.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It requires teamd and VLAN support.

## Risks and Edge Cases

VLAN upper lifetime adds cleanup risk: removing the LAG before VLAN cleanup can cascade errors. Occupancy checks can race with delayed mlxsw RIF updates.

## Test Signals

Signals are precise `rifs` occupancy changes and successful remaster/deslavement operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_lag_vlan.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_mac_profile_scale.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_mac_profile_scale.sh

## Purpose

Scale helper for exhausting or validating RIF MAC profile resources.

## Important APIs, Types, and Functions

Defines `RIF_MAC_PROFILE_NUM_NETIFS`, `rif_mac_profiles_create`, `rif_mac_profile_test`, setup, and cleanup. It creates VLAN RIFs with distinct MAC addresses from a generated `ip -b` batch and checks `rif_mac_profiles` resource occupancy.

## Control Flow

Setup disables IPv6 on the two ports to avoid automatic link-local RIF creation, then brings links up. The test creates `count` VLAN devices with different MAC addresses and IPv4 addresses, optionally expecting failure, then reads devlink resource occupancy and expects it to equal `count`.

## State and Persistence Behavior

State includes many VLAN devices, unique MAC addresses, IPv6 disable sysctls, link state, and devlink resource counters.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Generated MAC octets must stay valid for the requested count. IPv6 link-local suppression is required; otherwise unexpected RIF profiles inflate occupancy. Resource sizes vary by ASIC, so wrappers must pass correct expected counts.

## Test Signals

Signals are `ip -b` success/failure according to expectation and `rif_mac_profiles` occupancy matching the requested count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_mac_profile_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_mac_profiles.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_mac_profiles.sh

## Purpose

Functional tests for selecting correct RIF source MAC profiles during routed forwarding.

## Important APIs, Types, and Functions

Builds an H1/RP1/RP2/H2 routed topology, records router-port MACs, and defines `h1_to_h2`, `h2_to_h1`, `smac_test`, and `mac_profile_test`. It uses TC ingress/egress filters to verify both hardware forwarding and source MAC rewrite.

## Control Flow

Setup prepares VRFs, routes, router port addresses, and clsact on hosts/router ports. The test changes RIF MAC profile inputs and sends UDP traffic in both directions. TC `skip_sw` filters on egress router ports prove hardware forwarding, while host ingress filters match expected source MACs.

## State and Persistence Behavior

State includes router/host routes, RIF MAC addresses/profiles, neighbor entries, TC filters, and forwarding/VRF state.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The first packet can be software-forwarded due to unresolved neighbor, so the script replaces neighbors before measurement. Source MAC expectations depend on current RIF profile selection; stale MAC changes can make both directions fail.

## Test Signals

Signals are TC egress hardware packet hits and host ingress source-MAC packet hits for both traffic directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_mac_profiles.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_mac_profiles_occ.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_mac_profiles_occ.sh

## Purpose

Occupancy and consolidation tests for the mlxsw RIF MAC profile resource.

## Important APIs, Types, and Functions

Defines `create_max_rif_mac_profiles`, replacement, consolidation, shared replacement, and edit tests under `rif_mac_profile_edit_test`. It reads `rif_mac_profiles` resource size/occupancy and uses `devlink_reload` to reset baseline state.

## Control Flow

Setup disables IPv6 auto-addressing, brings two ports up, and reloads devlink. Tests create the maximum number of distinct profiles, replace one profile, consolidate profiles by making two RIFs share a MAC, verify a shared profile cannot be replaced beyond limits, and edit profile users while checking occupancy.

## State and Persistence Behavior

State includes VLAN/RIF devices with assigned MACs, devlink resource occupancy, and device reload state. Cleanup removes devices and resets links.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Resource accounting must be exact. Consolidation assertions can race with delayed occupancy updates. Devlink reload is disruptive and should run only on isolated test hardware. Shared replacement expected-failure logic depends on correct max-profile creation.

## Test Signals

Signals are resource occupancy equaling max, decreasing after consolidation, failing expected shared replacement, and `log_test` per edit scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_mac_profiles_occ.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/router_bridge_lag.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/router_bridge_lag.sh

## Purpose

mlxsw-specific wrapper for the shared router/bridge/LAG forwarding topology test.

## Important APIs, Types, and Functions

Defines `ALL_TESTS` and configuration hooks `config_devlink_reload`, `config_enslave_h1` through `config_enslave_h4`, then sources the generic `net/forwarding/router_bridge_lag.sh` implementation.

## Control Flow

The wrapper injects mlxsw-specific behavior into the shared test: reload the devlink device as part of configuration and provide host-enslavement hooks for the topology. After sourcing, control flow is owned by the common router/bridge/LAG library, which runs configuration waits and IPv4/IPv6 pings.

## State and Persistence Behavior

State is mostly created by the shared implementation: bridges, LAGs, host and switch port masters, routes, and forwarding settings. The wrapper itself only defines hooks and all-tests order.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It integrates directly with the shared `router_bridge_lag.sh` forwarding test.

## Risks and Edge Cases

Because behavior is delegated, wrapper risk is in hook naming and devlink reload side effects. Any mismatch with the shared library's expected hook names silently changes coverage.

## Test Signals

Signals are the shared library's config, wait, IPv4 ping, and IPv6 ping tests running under the mlxsw hook set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/router_bridge_lag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/router_scale.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/router_scale.sh

## Purpose

Scale helper for programming many routes through a two-port mlxsw router.

## Important APIs, Types, and Functions

Defines `router_h1_create`, `router_h2_create`, `router_create`, `router_routes_create`, `router_routes_destroy`, `wait_for_routes`, `router_test`, and cleanup. It creates host routes and many switch routes, then verifies reachability/offload behavior.

## Control Flow

Setup creates H1/H2 with routed subnets and switch router ports. `router_routes_create` programs a requested number of routes, `wait_for_routes` waits for programming/offload to settle, and `router_test` validates behavior for the count and expected-failure mode. Cleanup deletes routes and tears down router/host state.

## State and Persistence Behavior

State includes large route tables, host routes, router-port addresses, forwarding sysctls, and any offload state associated with the programmed routes.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Scale route insertion can be slow and resource-dependent. Expected counts must match ASIC route capacity and profile. If route cleanup misses entries, later scale iterations can start from a polluted table.

## Test Signals

Signals are successful route insertion or expected failure, route wait completion, and traffic/reachability validation from the helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/router_scale.sh -->
