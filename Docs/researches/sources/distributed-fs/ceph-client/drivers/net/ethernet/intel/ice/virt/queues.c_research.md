# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/queues.c

## Purpose
Implements virtchnl queue-related VF operations: queue configuration, queue enable/disable, IRQ map programming, queue bandwidth limits, queue quanta profiles, queue-count requests, and max frame size reporting adjusted for host port VLANs.

## Important APIs and Functions
- `ice_vc_get_max_frame_size()` returns port max frame size minus VLAN header when the VF has a hidden port VLAN.
- `ice_vc_cfg_qs_msg()` configures VF Tx/Rx queues from virtchnl queue-pair info.
- `ice_vc_ena_qs_msg()` and `ice_vc_dis_qs_msg()` enable/disable selected queue bitmaps and update VF queue state.
- `ice_vc_cfg_irq_map_msg()` maps VF MSI-X vectors to Rx/Tx queues.
- `ice_vc_cfg_q_bw()` stores and applies per-queue min/max bandwidth.
- `ice_vc_cfg_q_quanta()` selects/programs queue quanta profiles and assigns them to Tx rings.
- `ice_vc_request_qs_msg()` grants or rejects VF queue-count changes, resetting the VF on success.
- `ice_vf_vsi_dis_single_txq()`, `ice_vf_ena_txq_interrupt()`, and `ice_vf_ena_rxq_interrupt()` provide queue-level helpers.

## Control Flow
All virtchnl handlers validate VF ACTIVE state, VSI ID, queue IDs/bitmaps, ring lengths, and allocated queue bounds before programming hardware. Queue config coordinates with LAG reset preparation, supports optional CRC stripping disable only when VF negotiated CRC offload and VLAN stripping is not enabled, writes Tx/Rx ring DMA/count/frame settings, configures Rx descriptor format and PTP timestamp context, and unwinds configured queues on error. Queue enable only explicitly starts Rx rings; Tx queues are already enabled when queue context is configured. Disable can batch-stop all Rx rings when the requested bitmap equals the enabled bitmap.

## State and Persistence
Queue enable state lives in `vf->rxq_ena`, `vf->txq_ena`, and `ICE_VF_STATE_QS_ENA`. Queue bandwidth requests are cached in `vf->qs_bw[]`; quanta profile allocation increments `pf->num_quanta_prof_used`. Ring DMA addresses, lengths, buffer sizes, descriptor formats, max frame size, q_vectors, ITR indices, and quanta profile IDs are stored in VSI ring structures.

## Dependencies and Integration Points
Depends on virtchnl structs, `ice_vf_lib_private.h`, base/lib queue configuration helpers, LAG, scheduler bandwidth APIs, hardware register programming, PTP/flex descriptor capability bits, and PF queue availability accounting. Integrated with virtchnl dispatch and VF reset code.

## Risks
- Queue bitmap validation rejects zero/all-out-of-range but uses `BIT(ICE_MAX_RSS_QS_PER_VF)` boundary assumptions; queue counts must stay within word size.
- Error unwind in `ice_vc_cfg_qs_msg()` uses loop index rather than actual queue IDs configured, so sparse queue config failures should be tested carefully.
- Quanta profile allocation increments a PF counter without visible reclamation in this file.
- Per-queue bandwidth is compared against VF-level min/max limits and can reject configurations that would not take effect.
- Hidden port VLAN frame-size adjustment must stay consistent with netdev MTU and VF expectations.

## Test Signals
Test invalid VSI IDs, inactive VFs, zero/overflow queue bitmaps, invalid ring lengths, queue IDs beyond allocation, sparse queue configs, CRC strip disable with/without capability and VLAN stripping, flex descriptor RXDID validation, PTP timestamp flag, queue enable/disable idempotency, all-Rx batch disable, IRQ vector 0 rejection for queue maps, queue bandwidth min/max constraints, quanta size range/multiple-of-64/profile exhaustion, and queue request success/reset versus shortage response.
