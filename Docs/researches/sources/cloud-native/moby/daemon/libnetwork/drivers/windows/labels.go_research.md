# sources/cloud-native/moby/daemon/libnetwork/drivers/windows/labels.go

Purpose: Defines Windows driver label constants used to pass HNS/network/endpoint configuration through generic Docker network options.

Important APIs and constants: labels include network name, HNS ID, HNS ownership, routing domain, interface, QoS policies, VLAN, VSID, DNS suffix/servers, MAC pool/source MAC, ICC/DNS/gateway DNS controls, outbound NAT enablement, and outbound NAT exceptions.

Control flow: declarative constants only.

State and persistence: no state. Labels become part of network option maps and may be persisted by higher-level network config/state code.

Dependencies and integration points: consumed by Windows local drivers and Windows overlay code when parsing `netlabel.GenericData`.

Risks: label strings are user/plugin compatibility surface; renaming breaks existing network configs.

Test signals: no direct tests in this file.
