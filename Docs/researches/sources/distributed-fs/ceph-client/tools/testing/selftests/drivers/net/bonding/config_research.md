# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/config

Purpose: Kselftest kernel config fragment for bonding tests.

Important entries: `CONFIG_BONDING`, `CONFIG_BRIDGE`, `CONFIG_DUMMY`, `CONFIG_INET_ESP`, `CONFIG_INET_ESP_OFFLOAD`, `CONFIG_IPV6`, `CONFIG_IPVLAN`, `CONFIG_MACVLAN`, `CONFIG_NET_ACT_GACT`, `CONFIG_NET_CLS_FLOWER`, `CONFIG_NET_CLS_MATCHALL`, `CONFIG_NETCONSOLE`, `CONFIG_NETDEVSIM`, `CONFIG_NET_IPGRE`, `CONFIG_NET_SCH_INGRESS`, `CONFIG_NLMON`, `CONFIG_VETH`, `CONFIG_VLAN_8021Q`, and `CONFIG_XFRM_USER`.

Control flow: No executable flow; it declares kernel capabilities expected for the bonding test suite.

State and persistence: Build-time/test-environment configuration only.

Dependencies and integration points: Maps directly to the devices and subsystems used by bonding scripts: veth/dummy/nlmon, bridge/VLAN, TC, XFRM/IPsec, netconsole, netdevsim, and IPv6.

Risks and test signals: Missing config causes skips or false failures. Offload tests need ESP/XFRM and netdevsim support beyond basic bonding.
