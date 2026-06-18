# sources/distributed-fs/ceph-client/include/net/Space.h

Purpose: This small legacy header declares unified Ethernet adapter probe entry points intended to assign standard `ethN` style names.

Important APIs, types, and functions: It declares `ne_probe(int unit)` and `cs89x0_probe(int unit)`, both returning `struct net_device *`.

Control flow: Legacy network initialization code can call these probe functions with a unit number to discover or instantiate NE-compatible or CS89x0 Ethernet devices.

State and persistence behavior: The header has no state. Device state is returned as `struct net_device` objects owned by probe implementations and the netdev core.

Dependencies and integration points: It forward-uses `struct net_device` and integrates with legacy Ethernet probe code and net_device registration.

Risks: This header lacks include guards and includes no declaration of `struct net_device`, so it depends on caller include order. Legacy probing can conflict with modern bus-managed probing if both are active.

Test signals: Build coverage for include order, successful and failed probe paths for each unit, netdev naming, and coexistence with platform or bus-discovered Ethernet drivers.
