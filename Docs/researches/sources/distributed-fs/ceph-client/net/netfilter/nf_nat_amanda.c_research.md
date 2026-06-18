
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_amanda.c

Purpose: NAT helper for the Amanda backup conntrack helper. It rewrites embedded dynamic port text in UDP control packets and sets expectations so related TCP data connections follow the master NAT mapping.

Important APIs and functions: `help()` is installed through the RCU hook `nf_nat_amanda_hook` and registered via `struct nf_conntrack_nat_helper`. It uses `nf_nat_exp_find_port()`, `nf_nat_mangle_udp_packet()`, and `nf_nat_follow_master()`.

Control flow: When the conntrack Amanda helper detects a port field, NAT helper saves the original expected TCP port, forces the expected connection direction to original, sets `expectfn`, finds an available port, rewrites the decimal port string inside the UDP payload, and accepts. On port exhaustion or mangle failure it logs through conntrack helper facilities, unexpects as needed, and drops.

State and persistence: Static helper registration and an RCU function pointer are the only module state. Expectations live in conntrack.

Dependencies and integration: Depends on Amanda conntrack parser, generic NAT helper mangle functions, conntrack expectations, and NAT follow-master setup.

Risks: Risks are payload offset correctness, UDP length/checksum recalculation, expectation cleanup on failure, and decimal buffer sizing. Test signals should include Amanda control messages with same-port and remapped-port expectations, port exhaustion, checksum verification, and module unload synchronization with RCU hook users.
