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
