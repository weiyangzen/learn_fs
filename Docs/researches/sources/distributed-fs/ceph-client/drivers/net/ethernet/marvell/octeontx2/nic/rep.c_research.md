# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/rep.c

## Purpose
`rep.c` implements the RVU e-switch representor PCI driver. It exposes one netdev/devlink port per represented PF/VF, shares master RVU resources for TX/RX, relays events to PF/VF firmware, supports TC flower offload through the master MCAM path, and manages representor resources and lifecycle.

## Important APIs, Types, and Functions
Module entry uses `rvu_rep_driver`. Public functions are `rvu_rep_create()`, `rvu_rep_destroy()`, and `rvu_event_up_notify()`. Important helpers include `rvu_rep_mcam_flow_init()`, `rvu_rep_setup_tc()`, `rvu_rep_notify_pfvf()`, `rvu_rep_napi_init()`, `rvu_rep_rsrc_init/free()`, `rvu_get_rep_cnt()`, `rvu_rep_probe()`, and netdev ops open/stop/xmit/stats/MTU/offload stats/setup TC.

## Control Flow
Probe initializes RVU resources and asks firmware for representor count/map, then registers devlink. `rvu_rep_create()` initializes queues/resources, allocates netdevs, registers devlink ports and netdevs, sets NAPI/CQ IRQs, and enables e-switch mode. Representor TX validates length and uses master SQ `rep_id`. TC setup initializes per-representor MCAM flow state on demand, temporarily points master `otx2_nic` fields at representor context, then calls `otx2_setup_tc_cls_flower()`. Stats are fetched asynchronously by mailbox. Destroy disables e-switch, tears down CQs/NAPI/netdevs/devlink/resources.

## State and Persistence
Master `otx2_nic` stores representor count, PF map, shared qset, flags, and reps array. Each `rep_dev` stores netdev, stats, delayed stats work, devlink port, flow config, flags, rep ID, pcifunc, and MAC. Hardware e-switch state, MCAM entries, queue contexts, and firmware-visible representor events persist until destroy/remove.

## Dependencies and Integration Points
The file integrates with PCI, devlink port functions, TC flow blocks, RVU mailbox messages, common MCAM/queue resource helpers, `otx2_txrx.c`, `otx2_tc.c`, and representor events from PF/VF firmware.

## Risks and Edge Cases
`rvu_rep_mcam_flow_init()` allocates `flow_ent` but does not free it in the shown destroy path that only `kfree(rep->flow_cfg)`, so leak review is warranted. TC setup mutates shared master fields and must not race concurrent representor operations. `rvu_rep_state_evt_handler()` trusts `rvu_rep_get_repid()` result before indexing. Partial create unwind must unregister only successfully registered reps. Stats work scheduling after unregister needs cancellation discipline.

## Test Signals
Test representor probe/create/destroy/remove, firmware state events, devlink MAC get/set, MTU and port state notification, TX/RX traffic per representor, offload stats, TC flower add/delete/stats, MCAM allocation failure, e-switch enable/disable, IRQ/NAPI teardown under traffic, and leak detection for flow config.
