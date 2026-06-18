# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_bindings.c

Purpose: wires the SFC `ndo_setup_tc` and indirect TC callbacks into the driver flower offload engine. It owns `struct efx_tc_block_binding`, which records the NIC, optional representor, target netdev, and flow block used to route TC flower changes to `efx_tc_flower()`.

Important APIs and control flow: `efx_tc_setup()` rejects VFs and non-TC NIC state, then dispatches direct `TC_SETUP_CLSFLOWER` or `TC_SETUP_BLOCK`. `efx_tc_setup_block()` accepts only ingress clsact blocks, creates a binding on bind, allocates a `flow_block_cb`, and removes it on unbind. `efx_tc_indr_setup_cb()` is the indirect block path; it handles supported ingress blocks and rejects OVS internal/egress cases currently not offloaded. `efx_tc_netdev_event()` forwards unregister events to `efx_tc_unregister_egdev()` for tunnel egress cleanup.

State and dependencies: state is in `efx->tc->block_list`; RTNL is assumed for lookup. Dependencies include Linux flow block APIs, `tc.h` for flower programming, and encap-action egress-device teardown. Persistence is runtime-only; bindings are freed through the flow-block callback release path.

Integration, risks, and tests: this file is the entry point from netdev TC into MAE offload, so duplicate bind/unbind handling and teardown ordering are the main risks. Test signals are TC flower add/delete/stats on PFs and representors, indirect block registration through tunnel/bridge devices, netdev unregister while offloads exist, and driver teardown with already-unbound blocks.
