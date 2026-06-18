# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_cgx.c

## Purpose
`rvu_cgx.c` connects RVU AF resource management to physical CGX/RPM MAC ports. It maps CGX/RPM LMACs to RVU PFs, initializes MAC event handling, forwards link changes to PF drivers over AF-to-PF mailbox messages, exposes CGX/RPM mailbox handlers for link, stats, MAC addresses, promiscuous mode, PTP RX timestamping, pause/PFC, loopback, FEC, and link mode, and coordinates CGX start/stop reference counts across PF/VF NIX users.

## Important APIs, Types, and Functions
- `struct cgx_evq_entry` wraps queued link events for workqueue delivery.
- `is_mac_feature_supported()`, `is_cgx_config_permitted()`, `rvu_cgx_pdata()`, `rvu_first_cgx_pdata()`, `cgxlmac_to_pf()`, and mapping helpers provide lookup and permission checks.
- `rvu_map_cgx_lmac_pf()` builds `pf2cgxlmac_map` and `cgxlmac2pf_map`, allocates NPC pkinds, maps CGX links to NIX blocks, and counts CGX-mapped PFs/VFs.
- `cgx_lmac_event_handler_init()`, `cgx_lmac_postevent()`, `rvu_cgx_send_link_info()`, `cgx_evhandler_task()`, and `cgx_notify_pfs()` implement asynchronous link notifications.
- `rvu_cgx_init()`, `cgx_start_linkup()`, and `rvu_cgx_exit()` own CGX/RPM integration lifecycle.
- MAC control helpers include `rvu_cgx_config_rxtx()`, `rvu_cgx_tx_enable()`, `rvu_cgx_config_tx()`, `rvu_cgx_start_stop_io()`, `rvu_cgx_disable_dmac_entries()`, and `rvu_mac_reset()`.
- Mailbox handlers cover stats, FEC stats, MAC address set/add/del/get/reset/update/max, promiscuous enable/disable, PTP RX enable/disable, link event enable/disable, link info, features, internal loopback, pause frame config, PFC config, PHY FEC stats, FEC mode, aux firmware link info, and link mode changes.

## Control Flow
During `rvu_setup_hw_resources()`, `rvu_cgx_init()` discovers the maximum CGX ID, stores CGX private data pointers, maps active LMACs to PF IDs starting at `PF_CGXMAP_BASE`, clears X2P reset on MAC blocks, registers link event callbacks, creates an event workqueue, and initializes `cgx_cfg_lock`. After NIX initialization, `cgx_start_linkup()` enables RX for all LMACs and starts firmware link-up.

CGX/RPM link changes arrive through a callback that can run in interrupt context. The callback allocates an event entry with `GFP_ATOMIC`, pushes it to a spinlock-protected queue, and queues work. The worker sends link events to mapped PFs that enabled notifications. It serializes mailbox-up sends with `rvu->mbox_lock`, allocates an AF-to-PF message, waits for mailbox availability, sends, and waits for the PF response.

Mailbox requests from PFs enter handlers that typically validate the caller is a CGX-mapped PF, translate PF to `(cgx_id,lmac_id)`, fetch `mac_ops`, and call the MAC-specific CGX/RPM helper. PTP RX enable also configures NPC timestamp parser shifting, marks `pfvf->hw_rx_tstamp_en`, and informs MCS. CGX start/stop uses `cgx_cfg_lock` and `parent_pf->cgx_users` so the physical MAC starts when the first PF/VF NIX user starts and stops when the last user stops.

## State and Persistence Behavior
`rvu_cgx.c` fills CGX-related fields in `struct rvu`: `cgx_idmap`, `pf2cgxlmac_map`, `cgxlmac2pf_map`, `cgx_mapped_pfs`, `cgx_mapped_vfs`, notification bitmap, event queue/list/workqueue, and `cgx_cfg_lock`. Per-function state in `struct rvu_pfvf` tracks MAC address, default MAC, CGX in-use flag, user count on the parent PF, and PTP RX timestamp enablement. Hardware state persists in CGX/RPM MAC registers, DMAC filters or NPC exact-match tables, link mode/FEC configuration, pause/PFC state, loopback, PTP timestamp prepending, and Rx/Tx enable bits.

## Dependencies and Integration Points
The file depends on CGX/RPM APIs from `cgx.h` and `lmac_common.h`, MAC ops, NPC exact-match and parser configuration, NIX cumulative stats, MCS PTP configuration, RVU mailbox infrastructure, firmware CGX link data in `rvu_fwdata`, and RVU resource mappings from `rvu.h`. It is called by `rvu.c` during init/exit and by NIX/FLR paths for MAC start/stop and reset.

## Risks and Edge Cases
- Permission checks differ by handler: some reject VFs, some acknowledge unmapped functions, and MAC address set only checks PF mapping; caller expectations need coverage.
- Event delivery waits synchronously for PF mailbox responses from the event worker, so a non-responsive PF can delay later link events.
- `rvu_map_cgx_lmac_pf()` assumes PF IDs starting at 1 are available and that active LMAC count fits allocated mapping arrays.
- `rvu_cgx_exit()` loops through `cgx <= cgx_cnt_max` while `rvu_cgx_pdata()` rejects `>= cgx_cnt_max`; harmless but easy to misread.
- PTP RX enable changes both MAC and NPC parser behavior; partial failure can leave MAC timestamp prepending enabled if NPC configuration fails after the MAC write.
- Pause/PFC configuration depends on both MAC feature bits and shared verification against PF/VF flow-control ownership.
- `rvu_cgx_start_stop_io()` reference counting must remain balanced across PF/VF start/stop and FLR paths.

## Test Signals
- Probe with no CGX devices, sparse CGX IDs, multiple LMACs per CGX, RPM2 eight-LMAC layouts, and NIX1-connected links.
- Link event tests for notification disabled/enabled, current-link replay, mailbox-up timeout/failure, and queue cleanup on exit.
- Mailbox permission tests for PF, VF, LBK VF, non-CGX PF, and exact-match-enabled variants.
- PTP RX enable/disable tests covering MAC, NPC parser, `hw_rx_tstamp_en`, and MCS side effects, including injected NPC failure.
- Pause/PFC conflict tests and flow-control ownership validation across PF/VF users.
- Start/stop/FLR tests validating `cgx_users`, `cgx_in_use`, MAC reset, DMAC cleanup, and stats reset behavior.
