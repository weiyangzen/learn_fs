# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_encap.h

Purpose: declares the public tunnel encap/decap lifecycle API used by mlx5 TC flow parsing and offload paths. It hides the shared object caches, route table, FIB notifier, and neighbor update internals implemented in `tc_tun_encap.c`.

Important APIs and types: exports attach/detach functions for encap destinations and decap reformat objects, route attach/detach for decap flows, bulk destination set/unset helpers, `mlx5e_dup_tun_info`, RX tunnel attribute extraction, and `mlx5e_tc_tun_init`/`mlx5e_tc_tun_cleanup`. It includes `tc_priv.h` so callers operate on private flow and flow-attribute structures.

Control flow: TC flow setup calls `mlx5e_tc_tun_encap_dests_set` after parse attributes contain tunnel info and mirred ifindexes; teardown calls the matching unset path. L3-to-L2 decap setup uses `mlx5e_attach_decap`; RX tunnel route tracking uses `mlx5e_tc_set_attr_rx_tun` and `mlx5e_attach_decap_route`. Driver open/close paths create or destroy the tunnel encap manager through init/cleanup.

State and persistence: no state is defined here directly. It defines ownership boundaries: attach functions take references and add flow list links, detach functions drop them, and init/cleanup own notifier lifetime.

Dependencies and integration points: depends on private TC flow structures and through them on eswitch flow attrs, encap entries, decap entries, and route entries. The API is primarily consumed by `en_tc.c` and related TC action code.

Risks and test signals: because this is a lifecycle boundary, callers must pair every successful attach with detach and must not free parse tunnel info before unset. Test signals are leak-free TC add/delete cycles, failure unwind after partial multi-destination attach, decap attach failure, and cleanup with live or recently completed FIB work.
