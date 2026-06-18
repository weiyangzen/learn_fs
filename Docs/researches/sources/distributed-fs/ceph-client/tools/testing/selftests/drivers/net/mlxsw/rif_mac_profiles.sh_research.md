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
