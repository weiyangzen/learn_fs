# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_dcbnl.c

`otx2_dcbnl.c` implements IEEE DCBNL Priority Flow Control for PF devices under `CONFIG_DCB`. It exposes DCB callbacks, programs CGX/RPM PFC pause behavior through mailbox messages, allocates per-priority transmit scheduler queues, remaps SQ contexts to PFC scheduler queues, and maps receive queues to per-priority backpressure IDs.

Important entry points are `otx2_dcbnl_set_ops`, `otx2_config_priority_flow_ctrl`, `otx2_update_bpid_in_rqctx`, `otx2_pfc_txschq_alloc`, `otx2_pfc_txschq_config`, `otx2_pfc_txschq_update`, and `otx2_pfc_txschq_stop`. DCBNL callbacks are `otx2_dcbnl_ieee_getpfc`, `otx2_dcbnl_ieee_setpfc`, `otx2_dcbnl_getdcbx`, and `otx2_dcbnl_setdcbx`.

The main flow begins with `ieee_setpfc`: store the old bitmap, validate that enabled priorities have TX queues, configure CGX PFC pause state, disable NIX-CPT backpressure by default, enable NIX backpressure when PFC is active, and update scheduler queues. The update path frees disabled priorities after SMQ flush, allocates missing priority schedulers, updates SQ-to-SMQ mapping via NIX AQ messages, and configures all active PFC scheduler levels.

State lives in `pfvf->pfc_en`, `queue_to_pfc_map`, `pfc_schq_list`, `pfc_alloc_status`, and `bpid[]`. It is runtime-only but is reused during hardware resource initialization while the device remains bound. Dependencies include mailbox CGX PFC messages, NIX/NPA AQ writes, scheduler helpers, DCBNL netdev hooks, and queue/carrier stop-start APIs.

Risks include queue topology changes after PFC configuration, partial mailbox failures while queues are stopped, and the ambiguous use of zero in `queue_to_pfc_map` when priority zero is valid. Test with `dcb pfc` get/set across priorities and queue counts, confirm scheduler allocation/free and BPID updates, and run traffic while enabling/disabling PFC and injecting mailbox failures.
