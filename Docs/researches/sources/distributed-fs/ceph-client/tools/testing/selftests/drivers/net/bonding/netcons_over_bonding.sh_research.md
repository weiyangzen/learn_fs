# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/netcons_over_bonding.sh

Purpose: Disruptive regression test for netpoll/netconsole interactions with bonding, including allowed netconsole on a bond and rejected netconsole on enslaved or unsupported interfaces.

Important APIs/functions: `setup_bonding_ifaces()`, `create_ifaces_bond()`, `link_ifaces_bond()`, `create_all_ifaces()`, `configure_ifaces_ips()`, `test_enable_netpoll_on_enslaved_iface()`, `test_delete_bond_and_reenable_target()`, `test_send_netcons_msg_through_bond_iface()`, `test_enslave_netcons_enabled_iface`, `test_enslave_iface_to_bond`, `test_enslave_iff_disabled_netpoll_iface`, `enable_netcons_ns()`, and `lib_netcons.sh` helpers.

Control flow: The script loads netdevsim, netconsole, bonding, and veth; creates TX/RX namespaces; creates four netdevsim ports and links them through netdevsim sysfs; bonds two TX and two RX ports; configures IPs; creates a dynamic netconsole target; sends a `/dev/kmsg` message through the bond; then tests rejection and disablement scenarios when netpoll is attached to enslaved devices or when enslaving devices into netpoll-enabled bonds.

State and persistence: Mutates kernel modules, configfs netconsole targets, namespaces, netdevsim devices, bonds, veths, `/proc/sys/kernel/printk`, and temporary output under `/tmp`. Cleanup removes targets and devices.

Dependencies and integration points: Requires configfs, netconsole dynamic target support, netdevsim, bonding, veth, socat, namespace helpers, and root privileges.

Risks and test signals: Highly stateful and disruptive. Failures indicate netpoll reference/eligibility bugs, bonding/netconsole coexistence issues, or cleanup ordering problems.
