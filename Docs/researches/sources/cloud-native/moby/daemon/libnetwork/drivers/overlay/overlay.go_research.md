# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay.go

Purpose: Defines the Linux overlay driver core, registration, one-time OS configuration, transport address discovery, and discovery event handling.

Important APIs and types: constants define `NetworkType`, veth naming, VXLAN encapsulation overhead, and `secureOption`. `driver` stores OS init, encryption state, nftables table cache, bind/advertise addresses, and network table with explicit lock hierarchy. `Register` registers global data/connectivity scope. `configure` applies OS tweaks and cleans nftables if using iptables. `isIPv6Transport` infers VTEP family from advertise address. `nodeJoin` records self discovery bind/advertise addresses. `DiscoverNew` handles node discovery, initial encryption keys, and key updates. `DiscoverDelete` is currently no-op.

Control flow: configuration is lazy and one-time. Discovery type switches validate payload types before updating driver state or encryption keys.

State and persistence: all state is in memory; kernel state is changed by `configure` and encryption helpers.

Dependencies and integration points: implements `discoverapi.Discover` and `driverapi.TableWatcher`, integrates with swarm discovery, encryption key distribution, nftables backend selection, and scope registration.

Risks: overlay transport cannot be configured until self discovery provides a valid advertise address; encryption setup depends on this. Lock hierarchy must be preserved across future changes.

Test signals: `overlay_test.go` covers registration and type only.
