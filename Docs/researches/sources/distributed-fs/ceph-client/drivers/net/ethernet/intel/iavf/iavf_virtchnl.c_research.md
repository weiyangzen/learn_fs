# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_virtchnl.c

## Purpose
Implements the IAVF virtchnl control plane used by the VF to negotiate capabilities and request PF-owned operations. It sends AdminQ messages to the PF, polls or handles asynchronous replies, configures queues, IRQ maps, MAC/VLAN filters, promiscuous mode, RSS, VLAN offloads, PTP, QoS, ADq channels, cloud filters, Flow Director, advanced RSS rules, reset, and link events.

## Important APIs, Types, and Functions
Key send/get functions include `iavf_send_api_ver`, `iavf_verify_api_ver`, `iavf_send_vf_config_msg`, `iavf_get_vf_config`, `iavf_send_vf_offload_vlan_v2_msg`, `iavf_get_vf_vlan_v2_caps`, `iavf_send_vf_supported_rxdids_msg`, `iavf_get_vf_supported_rxdids`, `iavf_send_vf_ptp_caps_msg`, and `iavf_get_vf_ptp_caps`. Queue and interrupt control uses `iavf_configure_queues`, `iavf_enable_queues`, `iavf_disable_queues`, and `iavf_map_queues`. Feature operations include MAC/VLAN add/delete, promiscuous mode, stats, RSS key/LUT/hash/hfunc, VLAN stripping/insertion v1/v2, PTP command send, QoS quanta/bandwidth, channel enable/disable, cloud filters, FDIR filters, advanced RSS, and `iavf_request_reset`. `iavf_virtchnl_completion` is the central response dispatcher.

## Control Flow
Most request functions first check `adapter->current_op == VIRTCHNL_OP_UNKNOWN`, build a virtchnl message, clear the relevant `aq_required` bit, set `current_op`, and send with `iavf_send_pf_msg`. Initialization can also poll specific replies synchronously through `iavf_poll_virtchnl_msg`, which detects reset-impending events. Asynchronous completions handle PF events first, then log and repair request-specific failures, then update success state by opcode. Queue setup sends ring lengths, DMA addresses, descriptor IDs, CRC settings, PTP Rx timestamp flags, and max frame sizes. Filter operations batch within AQ buffer limits and maintain local pending/active states. PTP commands are dequeued under `ptp.aq_cmd_lock` and sent one at a time.

## State and Persistence
Persistent adapter state includes `current_op`, `aq_required`, negotiated PF/API version, `vf_res`, `vsi_res`, VLAN v2 caps, supported Rx descriptor IDs, PTP caps and cached PHC time, queue counts, link state/speed, netdev features, MAC/VLAN filter lists, RSS key/LUT/hashcfg/hfunc, QoS caps, queue shaper update flags, channel config state, cloud filter list, FDIR list, advanced RSS list, and current stats. Hardware/PF state persists after successful virtchnl requests until reset or later reconfiguration.

## Dependencies and Integration Points
Depends on AdminQ helpers, `iavf.h`, `iavf_ptp.h`, `iavf_prototype.h`, Intel `libie` Rx helpers, virtchnl structures and opcodes, netdev queue/carrier APIs, VLAN capability helpers, ethtool/TC-derived filter state, and reset/workqueue orchestration in `iavf_main.c`. It directly coordinates with `iavf_txrx.c` by configuring ring descriptors and with `iavf_ptp.c` by delivering PTP capability and time responses.

## Risks
The single `current_op` gate serializes most control operations; missed completion or send failure can stall later requests unless explicitly reset. Batched filter updates must correctly preserve `aq_required` when more messages are needed. Error paths mutate local MAC/VLAN/FDIR/RSS/cloud state and can diverge from PF state if not carefully matched to PF return status. Message length validation is uneven across opcodes. PTP time reads depend on timely completion wakeups. Reset events can arrive while synchronous polling expects another opcode.

## Test Signals
Signals include VF probe negotiation across PF API versions, queue configure/enable/disable/map, reset during configuration, link change events, MAC address changes and rejection, VLAN v1/v2 add/delete and stripping/insertion toggles, RSS get/set/hfunc rollback on failure, stats polling, PTP caps/time reads, QoS quanta and bandwidth programming, ADq channel setup/teardown, cloud/FDIR/advanced RSS add/delete success and failure paths, oversized filter batches, and PF communication failure behavior.
