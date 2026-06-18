<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/Kconfig -->
# sources/distributed-fs/ceph-client/net/bridge/Kconfig

Purpose: defines configuration symbols for the Linux Ethernet bridge module and optional bridge features.

Important APIs, types, and functions: no C APIs are defined. Symbols include `BRIDGE`, `BRIDGE_IGMP_SNOOPING`, `BRIDGE_VLAN_FILTERING`, `BRIDGE_MRP`, and `BRIDGE_CFM`. `BRIDGE` is tristate and selects `LLC` and `STP`; the others are boolean feature gates depending on `BRIDGE` and, for VLAN filtering, `VLAN_8021Q`.

Control flow: Kconfig choices determine which bridge source files are compiled by the bridge Makefile and which code paths appear behind `IS_ENABLED(CONFIG_...)` in bridge implementation files. Defaults enable IGMP/MLD snooping but leave VLAN filtering, MRP, and CFM off unless selected.

State and persistence: the file controls build-time state only. User choices persist in kernel `.config` and affect module contents and runtime feature availability.

Dependencies and integration points: integrates with the networking Kconfig tree, LLC/STP protocol support, inet multicast support for snooping, VLAN support, MRP, and CFM code. Help text also documents the user-visible bridge module name and firewall implications.

Risks: changing defaults or dependencies changes kernel footprint and feature availability. Enabling bridge netfilter behavior has operational consequences because bridged IP/ARP traffic can appear in firewall paths. Optional feature gates must match Makefile object lists and source `#if` guards.

Test signals: configuration build tests for built-in, module, and disabled bridge states; feature combinations for snooping, VLAN filtering, MRP, CFM, bridge netfilter, IPv6, and switchdev; runtime smoke tests that verify requested features expose netlink options only when compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/Kconfig -->
