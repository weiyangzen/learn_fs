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
