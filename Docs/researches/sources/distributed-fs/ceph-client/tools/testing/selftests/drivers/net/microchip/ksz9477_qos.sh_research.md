
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/microchip/ksz9477_qos.sh`

## Purpose
Tests QoS classification behavior on Microchip KSZ switch ports, covering port default priority, apptrust ordering between PCP and DSCP, and the global DSCP priority map.

## Important APIs, Types, And Functions
- Topology helpers `h1_create()`, `h2_create()`, `switch_create()`, `setup_prepare()`, and `cleanup()` build a two-host bridge through switch ports.
- `set_apptrust_order()`, `port_default_prio_get()`, `port_get_default_apptrust()`, DSCP map helpers, and `restore_priorities()` manipulate DCB app/apptrust state.
- `run_test()` is the core packet/counter validator, deriving expected internal priority and high-priority counter behavior.
- `test_port_default()`, `test_port_apptrust()`, and `test_global_dscp_map()` are the exported test cases.

## Control Flow
After setup, tests manipulate DCB default priority, apptrust order, and DSCP maps, then call `run_test()` for IPv4 and IPv6 traffic. `run_test()` primes the MAC table, samples port packet/byte and `rx_hi`/`tx_hi` ethtool stats, sends crafted mausezahn packets with DSCP and optional VLAN PCP, waits for counters, then compares high-priority byte counters against expected classification.

## State And Persistence
Mutates bridge membership, link state, IPv6 disable sysctls, DCB apptrust/default-prio/DSCP maps, and switch counters indirectly. Cleanup restores sysctls, bridge, VRFs, and DCB state using saved originals.

## Dependencies And Integration Points
Depends on forwarding test libraries, `dcb`, `jq`, `mausezahn`, ethtool stats helpers, stable MAC addresses, and Microchip KSZ `rx_hi`/`tx_hi` counters.

## Risks
The test encodes switch-specific thresholds: ingress high priority for internal priority > 0, egress high priority for > 1. Counter comparison adjusts for Ethernet FCS length and waits six seconds for hardware stats to update, which is device-specific.

## Test Signals
Pass signals are expected packet counts on ingress/egress ports, exact high-priority byte counter behavior, successful DCB apptrust/default-prio readback, and restoration of original DSCP/apptrust/default settings.
