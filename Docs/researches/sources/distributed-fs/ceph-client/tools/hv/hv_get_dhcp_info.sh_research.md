<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_get_dhcp_info.sh -->
# sources/distributed-fs/ceph-client/tools/hv/hv_get_dhcp_info.sh

Purpose: Example external helper for the Hyper-V KVP daemon to report whether DHCP is enabled on a network interface.

Important APIs/types/functions: Takes one positional interface name. Builds `/etc/sysconfig/network-scripts/ifcfg-$1`, greps for `dhcp`, and prints `Enabled` if found or `Disabled` otherwise.

Control flow: A single grep decides the output. Missing files or grep errors are ignored through stderr redirection and treated as disabled.

State and persistence: No state is modified. Output is a single status string consumed by the KVP daemon.

Dependencies/integration: Assumes Red Hat-style network-scripts configuration files. It is installed by the Hyper-V Makefile under `hypervkvpd/hv_get_dhcp_info` for daemon invocation.

Risks/tests: Risks include unquoted interface-derived path, false positives for any `dhcp` substring, incompatibility with NetworkManager/systemd-networkd/netplan, and no distinction between static config and missing config. Test signals are fixtures for DHCP/static/missing ifcfg files and interface names with unusual characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_get_dhcp_info.sh -->
