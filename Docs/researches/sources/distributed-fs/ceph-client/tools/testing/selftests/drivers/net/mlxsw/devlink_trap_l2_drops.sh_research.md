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
