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
