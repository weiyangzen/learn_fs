# `sources/distributed-fs/ceph-client/include/linux/if_link.h`

Purpose: kernel-side link metadata supplement for virtual function information, kept separate from the larger UAPI link definitions.

Important APIs/types/functions: `struct ifla_vf_stats` for VF RX/TX packet/byte, multicast/broadcast, and drop counters; `struct ifla_vf_info` for VF MAC, VLAN/QoS, spoof check, link state, min/max TX rate, RSS query enablement, trust, and IB node/port GUIDs.

Control flow and state: no functions. Structures carry snapshot state between netdevice/SR-IOV providers and rtnetlink-style reporting.

Dependencies/integration: used by netdevice VF management and link reporting code; fields mirror netlink attributes.

Risks: ABI/layout drift with UAPI link attributes; partial driver support may leave fields unset; rate and GUID semantics vary by NIC family.

Test signals: SR-IOV VF query through rtnetlink, drivers filling all fields, zero/default behavior for unsupported features, and structure layout compile checks.
