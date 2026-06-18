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
