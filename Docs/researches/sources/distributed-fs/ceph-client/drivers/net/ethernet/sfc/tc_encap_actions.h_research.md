# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_encap_actions.h

Purpose: defines tunnel encap and neighbour-binding state for SFC TC offload.

Important types/APIs: `struct efx_neigh_binder` tracks the route/neighbour backing one or more encap actions, including namespace, IPv4/IPv6 key, hardware address, validity, TTL, egdev references, refcount, users, work, and owning NIC. `EFX_TC_MAX_ENCAP_HDR` caps generated headers at 126 bytes. `struct efx_tc_encap_action` stores type, `ip_tunnel_key`, destination m-port, header bytes, neighbour pointer, user lists, rhashtable linkage, refcount, and firmware id. Public functions initialize/finalize, create/release encap metadata, check rule readiness, unregister egress devices, and receive netevents.

State and integration: compiled under `CONFIG_SFC_SRIOV`, includes tunnel-key action definitions, and is consumed by flower parsing and counter work. Runtime state is firmware-backed but not persisted across driver reload.

Risks and tests: structure layout participates in rhashtable keys and list ownership; changes need careful lifetime tests. Build with IPv6 enabled/disabled and test tunnel offload with neighbour churn.
