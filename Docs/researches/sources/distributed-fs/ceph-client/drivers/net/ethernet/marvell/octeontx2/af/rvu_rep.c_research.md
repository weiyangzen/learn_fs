# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_rep.c

## Purpose

`rvu_rep.c` implements AF-side support for RVU representor mode. It forwards PF/VF state and MAC events to the representor PF, reports NIX LF stats, builds VLAN-based MCAM steering rules between represented functions and the representor, and handles mailbox requests for e-switch mode and representor count/map discovery.

## Important APIs, Types, And Functions

- `MBOX_UP_REP_MESSAGES` expands allocation helpers for AF-to-PF representor up messages.
- `rvu_rep_up_notify()` sends `rep_event` messages to the representor PF and updates AF cached MAC state on MAC-change events.
- `rvu_rep_wq_handler()` drains `rvu->rep_evtq_head` and serializes up-notification through `rvu->mbox_lock`.
- `rvu_mbox_handler_rep_event_notify()` queues PF/VF-originated representor events from mailbox context.
- `rvu_rep_notify_pfvf_state()` notifies the representor PF when a CGX-mapped PF/VF is enabled or disabled.
- `rvu_mbox_handler_nix_lf_stats()` reads NIX LF RX/TX stats or delegates reset to `rvu_mbox_handler_nix_stats_rst()`.
- VLAN helpers `rvu_rep_tx_vlan_cfg()`, `rvu_rep_rx_vlan_cfg()`, and `rvu_rep_get_vlan_id()` allocate/derive per-representee tags.
- `rvu_rep_install_rx_rule()` and `rvu_rep_install_tx_rule()` install MCAM rules for representor-to-representee and representee-to-representor paths.
- `rvu_rep_install_mcam_rules()`, `rvu_rep_update_rules()`, and `rvu_rep_pf_init()` drive representor mode setup and per-function rule enablement.
- `rvu_mbox_handler_esw_cfg()` and `rvu_mbox_handler_get_rep_cnt()` expose representor mode control and mapping discovery.

## Control Flow

Representor discovery starts when the representor PF sends `get_rep_cnt`; the handler records `rvu->rep_pcifunc`, allocates `rep2pfvf_map`, counts CGX-mapped PFs/VFs, and returns the map. When e-switch setup later enables `rvu->rep_mode`, `rvu_switch_enable()` calls `rvu_rep_pf_init()` and `rvu_rep_install_mcam_rules()`. The installer walks each CGX-mapped PF and its VFs, sets the NIX block address, skips VFs without attached NIX LFs, and installs four MCAM entries per represented function: RX/TX rules for representor traffic and RX/TX rules for represented-function traffic.

RX rules match LBK-channel VLAN tags. Representor-bound rules use the representor pcifunc and unicast action index derived from the representor id; return traffic rules target the represented pcifunc and default RX action. TX rules configure VLAN insertion for the source function, then steer packets to `RVU_SWITCH_LBK_CHAN` on the correct LBK id derived from NIX0/NIX1.

Event flow is asynchronous. PF/VF mailbox events allocate a `rep_evtq_ent` with `GFP_ATOMIC`, append it under `rep_evtq_lock`, and queue `rep_evt_work`. The worker removes one entry at a time, calls `rvu_rep_up_notify()`, and frees it. Up-notification holds `mbox_lock`, allocates an up message for the representor PF, waits for any previous up mailbox message to clear, sends, waits for response, and unlocks.

## State And Persistence

State lives in `struct rvu`: `rep_pcifunc`, `rep_mode`, `rep_cnt`, `rep2pfvf_map`, the representor workqueue/list/spinlock, and `rvu->rswitch` MCAM entry metadata. The AF also updates `struct rvu_pfvf::mac_addr`, `sdp_info`, flags, and NIX interface fields through helper calls. Hardware persistence is in NIX VLAN config, NPC MCAM entries/counters, LBK link scheduler state, and NIX LF stats. No disk persistence exists.

## Dependencies And Integration Points

The file depends on AF helpers in `rvu.h`, register definitions in `rvu_reg.h`, NIX/NPC mailbox handlers, `is_pf_cgxmapped()`, `nix_get_nixlf()`, `rvu_get_pf_numvfs()`, `rvu_get_nix_blkaddr()`, and `rvu_switch_enable_lbk_link()`. It integrates with the NIC representor driver through mailbox up events and with `rvu_switch.c` for shared MCAM allocation and update hooks.

## Risks

- `rvu_mbox_handler_get_rep_cnt()` reallocates `rep2pfvf_map` without guarding repeated calls; repeated discovery can leak devm memory or change mappings while rules exist.
- Rule count assumptions must match `rvu_switch_enable()` allocation (`rep_cnt * 4` in representor mode); missed VFs or skipped NIX LFs can leave unused entries in the allocated range.
- Event queue allocation in atomic context can fail and drop events.
- Up-notification waits under a global mailbox lock; stuck representor mailbox response can delay unrelated AF mailbox paths.
- VLAN id is derived from representor index and uses bit 8 to distinguish direction; growth beyond the expected bit width could collide with protocol semantics.

## Test Signals

Useful tests include representor count/map discovery, e-switch enable/disable, PF/VF state notification, MAC address change propagation, bidirectional representor traffic over LBK, VLAN insertion/strip behavior, NIX LF stat reads and resets, NIX0/NIX1 represented functions, VFs without NIX LF attached, and mailbox allocation/response timeout fault injection.
