# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_topo_2d1c.sh

Purpose: Shared two-downlink, one-client bonding topology library for mode 1/5/6 tests.

Important APIs/functions: `gateway_create()`, `gateway_destroy()`, `server_create()`, `bond_reset()`, `server_destroy()`, `client_create()`, `client_destroy()`, `setup_prepare()`, `cleanup()`, `bond_check_connection()`, forwarding `lib.sh`, `simple` namespace/veth/bridge operations, and TC clsact setup.

Control flow: Callers use `setup_prepare()` to create gateway, server, and client namespaces. The server owns `bond0` with two veth slaves connected to a gateway bridge; the client connects to the same bridge. `bond_reset()` deletes and recreates `bond0` with caller-supplied options while preserving slave links and IP addresses.

State and persistence: Defines global namespace names, IPv4/IPv6 addresses, MAC array, and helper functions. It creates transient namespaces, bridge, veths, bond, addresses, and TC qdiscs; `cleanup()` removes them.

Dependencies and integration points: Used by `bond_macvlan_ipvlan.sh` and can be extended by `bond_topo_3d1c.sh`. Requires forwarding library, bonding, bridge, veth, IPv6, and TC.

Risks and test signals: As a shared fixture, bugs in cleanup or `bond_reset()` cascade into many tests. IPv6 DAD wait is handled with `slowwait`.
