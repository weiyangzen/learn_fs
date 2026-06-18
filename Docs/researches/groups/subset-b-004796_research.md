# Research Group: subset-b-004796

This grouped report covers the Broadcom `brcmfmac` firmware ABI, firmware-signaling flow control, firmware-vendor dispatch, PCIe msgbuf transport, Open Firmware platform data, and Wi-Fi Direct/P2P support files listed in the work item. Each source file section is bounded with the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwil_types.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwil_types.h

Purpose: this header is the central firmware-interface layout catalog for `brcmfmac`. It defines little-endian wire structs, constants, bit flags, and variable-length payload shapes used by cfg80211, P2P, scan, security, WoWLAN, PNO/gscan, packet filters, CLM download, and station/statistics firmware iovars.

Important APIs/types: there are no functions; the important contract is binary layout. Key families include scan/escan (`brcmf_scan_params_le`, v2 scan params, `brcmf_escan_params_le`, `brcmf_escan_result_le`), association and join (`brcmf_join_params`, `brcmf_ext_join_params_le`, join preferences), P2P/action frames (`brcmf_fil_p2p_if_le`, `brcmf_fil_action_frame_le`, `brcmf_fil_af_params_le`), security (`brcmf_wsec_key[_le]`, PMK/SAE/PMKSA v2/v3 structs), station information (`brcmf_sta_info_le`), management RX (`brcmf_rx_mgmt_data`), WoWLAN wake/filter structs, preferred network offload structs, CLM download chunks, packet counts, GTK rekey material, gscan buckets/config, and keep-alive packets.

Control flow and state: consumers allocate one of these structs, fill fixed fields in host order converted to `__le*` or `__be*` as declared, then pass it through firmware iovar/command helpers. Persistence is in firmware, not in this header: country codes, PMKSA entries, PNO lists, WoWLAN patterns, and gscan config persist only as long as firmware/driver state keeps them. Variable-length structs rely on explicit length/count fields and flexible arrays, so callers must compute allocation sizes from counts and fixed offsets.

Dependencies and integration: the header depends on kernel WLAN constants, endian typedefs, `BIT()`, flexible arrays, and values consumed by `fwil.c`, `cfg80211.c`, `p2p.c`, `feature.c`, `pno.c`, WoWLAN code, and vendor-specific firmware implementations. It is an ABI boundary with the dongle firmware; field order and endian annotations are part of the contract.

Risks: any layout drift, missing endian conversion, wrong count/length arithmetic, or misuse of flexible-array allocation can corrupt firmware requests or parse firmware responses incorrectly. Security-sensitive material such as keys, PMKSA, SAE passwords, GTK rekey data, and action-frame payloads require exact sizing. Scan result parsing must respect `ie_offset`, `ie_length`, and record `length`; trusting malformed firmware data would risk out-of-bounds reads in consumers.

Test signals: compile-time struct size/offset regressions, scan/escan with v1 and v2 parameters, P2P interface/action-frame flows, SAE/PMKSA setup, WoWLAN/PNO/gscan configuration, CLM download chunking, and firmware interoperability on devices with different firmware vendors and feature sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwil_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwsignal.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwsignal.c

Purpose: implements BDCv2 firmware signaling for host/firmware flow control, per-peer power-save queues, TX status tracking, FIFO credits, TIM bitmap signaling, and AMPDU RX reorder. It sits between netdev/cfg80211 traffic and the lower protocol/bus layer.

Important APIs/functions: exported entry points are `brcmf_fws_attach`, `brcmf_fws_detach`, `brcmf_fws_debugfs_create`, `brcmf_fws_process_skb`, `brcmf_fws_hdrpull`, interface add/reset/delete helpers, `brcmf_fws_bustxcomplete`, `brcmf_fws_bus_blocked`, `brcmf_fws_queue_skbs`, `brcmf_fws_fc_active`, and `brcmf_fws_rxreorder`. Internal core types are `brcmf_fws_info`, `brcmf_fws_mac_descriptor`, the hanger table, per-FIFO credit arrays, and the per-descriptor packet queues.

Control flow: attach allocates state, creates a single-thread dequeue workqueue, registers firmware event handlers for credit maps and BCMC credit support, enables TLV signaling and host RX reorder iovars when supported, initializes the hanger and default descriptor. TX goes through `brcmf_fws_process_skb`: classify FIFO, find a MAC descriptor, allocate a hanger slot, enqueue into the descriptor PSQ, then schedule dequeue. The worker drains FIFOs by priority, honors bus blockage, consumes explicit/implied credits, borrows credits across access categories, pushes TLV headers, and transmits via `brcmf_proto_txdata`. RX-side `brcmf_fws_hdrpull` parses TLVs, updates descriptors/credits, handles TX statuses, captures reorder metadata, and schedules more dequeue work.

State and persistence: state is in-memory per driver instance: FIFO credits and credit maps, descriptor occupancy/open/closed state, requested credits/packets, suppressed-packet queues, hanger slots waiting for TX status, statistics, reorder flows, and bus-flow blocked flags. Firmware provides authoritative events; detach/interface delete flushes queues and frees SKBs. No on-disk persistence exists.

Dependencies and integration: depends on `brcmu_pktq`, sk_buff control buffer storage, netdev flow blocking, firmware event handlers, `fwil` iovars, BDC/proto TX paths, bus TX queues, cfg80211 priority mapping, and `debugfs`. It integrates with `core` interface lifetime and with protocol-specific transmit completion.

Risks: correctness depends on strict locking around queue, credit, descriptor, and hanger mutation. Lost TX status, hanger slot mismatch, malformed TLVs, negative credits, queue-full paths, or interface removal while packets are queued can leak or double-free SKBs. Credit borrowing and suppression reorder logic are subtle and can cause starvation, packet reordering, or netdev flow-control stalls. RX reorder trusts firmware-provided flow IDs and indices enough that malformed metadata should be tested carefully.

Test signals: high-throughput TCP/UDP with all AC priorities, AP/STA multicast, suspend/resume, bus flow-block/unblock, interface delete under traffic, firmware credit-map changes, suppressed TX status storms, AMPDU reorder with holes/flush/delete flow, debugfs `fws_stats`, and kernels built with lockdep/KASAN/KCSAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwsignal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwsignal.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwsignal.h

Purpose: declares the firmware-signaling interface used by the rest of `brcmfmac` and defines the firmware FIFO/access-category numbering shared with `fwsignal.c`.

Important APIs/types: `enum brcmf_fws_fifo` maps firmware FIFOs to background, best-effort, video, voice, BCMC, and ATIM queues. Function declarations cover attach/detach, debugfs creation, queueing/flow-control queries, header pull/push path entry through `brcmf_fws_process_skb` and `brcmf_fws_hdrpull`, interface lifetime hooks, bus TX completion/blocking, and RX reorder.

Control flow and state: callers do not own state directly; they hold or pass `struct brcmf_fws_info *` returned by attach and use interface callbacks as netdevs are added or removed. Header users can branch on `brcmf_fws_queue_skbs()` and `brcmf_fws_fc_active()` to decide whether the firmware-signaling queues are active.

Dependencies and integration: integrates with `core.h` types (`brcmf_pub`, `brcmf_if`), Linux `sk_buff`, bus/proto TX completion, and cfg80211 interface lifecycle. The header intentionally hides queue and descriptor internals from other compilation units.

Risks: callers must pair attach/detach and invoke interface add/delete hooks consistently; otherwise queued packets can be tied to stale descriptors. FIFO enum order is semantically significant because `fwsignal.c` maps priorities and credit arrays by index.

Test signals: compile/link coverage for all protocol modes, interface add/delete under traffic, and flow-control-active transitions when firmware does or does not supply credit maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwsignal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwvid.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwvid.c

Purpose: provides firmware-vendor dispatch for Broadcom/Cypress/BCA/WCC variants. It selects a vendor operation table for a driver instance, supports modular vendor implementations, tracks attached buses per vendor, and removes affected buses when a vendor module unregisters.

Important APIs/functions: `brcmf_fwvid_register_vendor` and `brcmf_fwvid_unregister_vendor` are exported when `brcmfmac` is modular. Core-facing functions are `brcmf_fwvid_attach`, `brcmf_fwvid_detach`, and `brcmf_fwvid_vendor_name`. The static vendor table stores vendor name, `brcmf_fwvid_ops`, attached driver list, optional module pointer, and registration completion.

Control flow and state: attach validates `bus_if->fwvid`, locks `fwvid_list_lock`, optionally requests `brcmfmac-<vendor>` and waits for registration, then installs `drvr->vops` and links the bus into the vendor list. Detach clears `drvr->vops` and removes the bus list node. Unregister walks attached buses, drops the lock around `brcmf_bus_remove`, then clears the module/ops and reinitializes completion.

Dependencies and integration: depends on `firmware.h` vendor IDs, vendor `vops.h` tables, bus removal, module auto-loading, completions, mutexes, and the inline wrappers in `fwvid.h`. It is the gate for vendor-specific feature attach, event allocation, cfg80211 operation selection, SAE password handling, and event registration.

Risks: `brcmf_fwvid_attach` returns early on module request failure without unlocking the mutex in the visible control path, which is a high-value audit target. Vendor unregister removes live buses, so list integrity and lock dropping/reacquisition must be correct. Built-in and module builds differ significantly; missing `alloc_fweh_info` is rejected only on registration.

Test signals: built-in vendor boot, modular vendor autoload, bad/unknown firmware vendor ID, vendor module unregister while devices are attached, repeated attach/detach, and lockdep around request-module failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwvid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwvid.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwvid.h

Purpose: defines the vendor-operation contract used to abstract firmware-family differences and provides inline dispatch helpers from generic `brcmfmac` code to selected vendor ops.

Important APIs/types: `struct brcmf_fwvid_ops` contains hooks for feature attach, SAE password setup, firmware event allocation, event activation, cfg80211 op selection, and event handler registration. Exported functions register/unregister vendors and attach/detach a driver to the selected vendor. Inline helpers call through `drvr->vops` or `ifp->drvr->vops`, returning `-EOPNOTSUPP`/`-EIO` when hooks are absent where appropriate.

Control flow and state: the header does not store state; it assumes `brcmf_fwvid_attach()` has populated `drvr->vops`. Some helpers tolerate missing optional hooks, while `brcmf_fwvid_feat_attach()` assumes `ifp->drvr->vops` is valid before checking `feat_attach`.

Dependencies and integration: includes firmware/vendor IDs and cfg80211 types. It is consumed by common cfg80211, feature, firmware-event, and security setup paths that need vendor-specific behavior without hard-coding a vendor.

Risks: helper nullability is uneven. Callers must know whether `drvr->vops` has been attached before invoking helpers, especially `brcmf_fwvid_feat_attach`. Optional hooks need graceful fallback behavior in callers.

Test signals: firmware variants with partial op tables, SAE password calls on unsupported vendors, event activation after attach, cfg80211 ops registration, and detach/reprobe cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwvid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/msgbuf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/msgbuf.c

Purpose: implements the PCIe-style msgbuf protocol backend. It manages common rings and per-peer flow rings, DMA-mapped packet IDs, ioctl request/response buffers, RX buffer posting, event delivery, TX completion, and protocol operation registration.

Important APIs/functions: externally visible functions are `brcmf_proto_msgbuf_attach`, `brcmf_proto_msgbuf_detach`, `brcmf_proto_msgbuf_rx_trigger`, and `brcmf_msgbuf_delete_flowring`. Internal paths cover packet ID allocation/release, ioctl send/wait, flowring create/delete workers, TX queueing/drain, RX data/control buffer posting, message-type dispatch, and debugfs stats. Main state lives in `struct brcmf_msgbuf`.

Control flow: attach allocates msgbuf state, workqueue, bitmaps, coherent ioctl buffer, packet-ID arrays, flowring state, protocol callbacks, and posts initial RX/event/ioctl buffers. Data TX looks up or creates a flowring keyed by destination/priority/interface, enqueues SKBs in flowring state, schedules `msgbuf_txflow`, maps payload DMA, writes `MSGBUF_TYPE_TX_POST`, and waits for TX status messages to finalize SKBs. RX trigger drains RX, TX, and control completion rings, dispatching message types to ioctl completion, events, TX status, RX frames, and flowring create/delete responses.

State and persistence: state is in RAM and DMA-visible rings only. Packet ID tables retain mappings from firmware request IDs to SKBs/DMA addresses until completion or detach. `rxbufpost`, `cur_eventbuf`, and `cur_ioctlrespbuf` track posted host buffers. Flowring status persists until firmware delete completion, bus down, or detach.

Dependencies and integration: depends on `commonring`, `flowring`, DMA mapping APIs, `brcmf_proto`, `bus_if->msgbuf`, `brcmf_fweh_process_skb`, `brcmf_netif_rx`, monitor-mode RX, and debugfs. It installs the proto callback table used by core transmit, ioctl, peer, and debug paths.

Risks: packet-ID allocation uses atomic slots but `last_allocated_idx` is shared state; concurrency assumptions rely on surrounding serialization. DMA mapping/unmapping must match every completion and failure path. Flowring deletion waits for outstanding TX with bounded retries and then may forcibly zero outstanding count. RX buffer accounting under allocation failure can starve firmware if not refilled. `brcmf_msgbuf_hdrpull` and `rxreorder` are stubs, so this protocol path relies on firmware/msgbuf framing rather than BCDC-style header parsing.

Test signals: PCIe probe/remove, ioctl timeout and success paths, TX under many peers/TIDs, flowring creation failure/delete while traffic is outstanding, RX buffer exhaustion/refill, WL event delivery, monitor 802.11 frames, DMA API debug, and debugfs `msgbuf_stats`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/msgbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/msgbuf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/msgbuf.h

Purpose: declares msgbuf protocol constants and public entry points for builds with `CONFIG_BRCMFMAC_PROTO_MSGBUF`.

Important APIs/types: ring depths and item sizes define control, RX post, completion, TX completion, RX completion, and flowring dimensions. `struct msgbuf_buf_addr` is the shared 64-bit DMA address representation split into little-endian low/high words. Public functions attach/detach the msgbuf proto, trigger RX processing from bus interrupts, and request flowring deletion.

Control flow and state: the header switches behavior at compile time. With msgbuf enabled, callers get the real attach/detach/RX/delete functions. Without it, attach/detach become no-op inline stubs so non-msgbuf builds do not need the implementation.

Dependencies and integration: used by bus/protocol setup code and `msgbuf.c`. The constants must match firmware ring ABI and bus-provided ring memory.

Risks: ring item sizes differ for pre-v7 and newer completion formats; any mismatch with bus firmware setup causes completion parsing corruption. Compile-time stubs can hide missing protocol support if callers do not check bus capabilities separately.

Test signals: build both with and without `CONFIG_BRCMFMAC_PROTO_MSGBUF`, validate ring sizes against PCIe firmware capabilities, and exercise RX trigger/delete flowring paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/msgbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/of.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/of.c

Purpose: reads device-tree properties into `brcmf_mp_device` platform settings, mainly for embedded/Apple ARM64 and SDIO designs.

Important APIs/functions: `brcmf_of_probe` is the public entry point. `brcmf_of_get_country_codes` parses `brcm,ccode-map` string arrays or the `brcm,ccode-map-trivial` boolean into country-code mapping settings.

Control flow and state: probe reads board type, antenna SKU, optional calibration blob, falls back to root `compatible` as board type with slashes replaced by dashes, enables optional 32.768 kHz LPO clock, and then only applies the Broadcom FMAC-compatible node-specific settings. It reads country map, MAC address, SDIO drive strength, and optional out-of-band IRQ mapping/trigger flags. Allocations use devm where appropriate; stored pointers refer to device-tree property memory or devm-managed memory.

Dependencies and integration: depends on OF APIs, clock APIs, IRQ mapping, `of_get_mac_address`, `brcmf_mp_device`, and SDIO platform data. It feeds later firmware selection, NVRAM/calibration, regulatory country mapping, MAC assignment, and OOB interrupt setup.

Risks: malformed country map strings log errors but still leave partially initialized entries. `brcmf_of_probe` dereferences `dev->of_node` for early property reads, so it assumes callers only invoke it with an OF node when `CONFIG_OF` implementation is used. Optional failures are intentionally ignored in several places, which is correct for broad platform compatibility but can make board-data issues quiet.

Test signals: DTs with explicit and trivial country maps, Apple board-type/antenna/cal-blob properties, missing OF node, deferred MAC address provider, optional LPO clock failure, SDIO drive strength, and OOB IRQ trigger mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/of.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/of.h

Purpose: exposes the device-tree probe hook and provides a no-op fallback when Open Firmware support is not compiled.

Important APIs/types: declares `brcmf_of_probe(struct device *dev, enum brcmf_bus_type bus_type, struct brcmf_mp_device *settings)` under `CONFIG_OF`; otherwise defines a static stub returning success.

Control flow and state: this header lets common bus setup call `brcmf_of_probe` unconditionally. State mutation happens only in `of.c`; the fallback intentionally leaves platform settings unchanged.

Dependencies and integration: depends on `struct device`, `enum brcmf_bus_type`, and `struct brcmf_mp_device` being visible from including files. It integrates OF platform data with bus-independent driver initialization.

Risks: the fallback returning 0 means builds without OF silently skip DT-derived settings. The header lacks its own include guard, relying on small size and normal include patterns; repeated inclusion is harmless for the declaration but less conventional.

Test signals: compile with and without `CONFIG_OF`, probe on non-DT platforms, and verify bus setup handles unchanged settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/of.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/p2p.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/p2p.c

Purpose: implements Wi-Fi Direct/P2P behavior for cfg80211: discovery enable/disable, P2P scans, remain-on-channel/listen, action-frame TX/RX and retries, common-channel search, GO negotiation handling, P2P virtual interface creation/deletion, and P2P device attach/detach.

Important APIs/functions: external functions include attach/detach, add/delete vif, interface role change, start/stop P2P device, scan prep, remain/cancel ROC, listen-complete notification, action-frame RX/TX-complete notification, action-frame send, scan-result common-channel detection, probe-request notification, and P2P device interface removal. Internal helpers parse P2P/GAS action frames, configure firmware discovery, build P2P escans, find listen channel attributes, run AFX worker searches, handle GON collisions, and request/disable/release firmware P2P interfaces.

Control flow: attach records primary vif and optionally creates the P2P_DEVICE. Scan prep detects wildcard `DIRECT-` SSID requests, extracts listen channel, enables discovery, and overrides escan execution. Remain-on-channel enables discovery, sets firmware listen state, increments a cookie, and notifies cfg80211; firmware listen-complete clears bits and expires ROC. Action-frame send classifies public/GAS/P2P action frames, tunes dwell/MPC/search behavior, aborts active scans, optionally searches for peer channel with a workqueue/completion loop, sends `actframe` iovars with retries, waits for firmware completion events, and optionally extends listen time for expected responses.

State and persistence: `brcmf_p2p_info` holds status bits, P2P device/interface addresses, bss index to vif mappings, remain-on-channel state/cookie, expected action subtype, completions, AFX work state, sent-channel/timing, GON collision flags, and dynamic-device mode. Firmware persists discovery state, p2p interface state, and action-frame operations until explicitly disabled, deleted, or reset by detach.

Dependencies and integration: depends on cfg80211/nl80211, firmware iovars (`p2p_disc`, `p2p_state`, `p2p_scan`, `actframe`, `p2p_ifadd`, `p2p_ifdel`, `p2p_ifupd`), `fwil_types.h` P2P structs, feature flags such as RSDB, cfg80211 vif-event synchronization, firmware event dispatch, scan code, MPC power-save control, and netdev attach/remove.

Risks: it is a timeout-heavy asynchronous state machine. Races between scans, listen completion, action-frame completion, vif deletion, and GON collision handling can leave bits/completions stale. Channel filtering must avoid DFS/no-IR channels. Action-frame length/subtype parsing assumes sufficiently validated cfg80211 input. Interface creation/deletion relies on firmware events; timeout handling must free vifs and clear armed events. MPC toggling around GO negotiation must be restored on all exits.

Test signals: `p2p_find`, social/progressive scans, remain-on-channel cookies, GO negotiation request/response/confirm, provision discovery and GAS, peer common-channel search, no-ACK and retry paths, active scan abort during action TX, P2P client/GO interface add/delete, RSDB second P2P connection, dynamic versus forced P2P_DEVICE, and supplicant interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/p2p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/p2p.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/p2p.h

Purpose: declares the P2P subsystem's public interface and state structures shared between cfg80211, event handlers, and `p2p.c`.

Important APIs/types: `enum p2p_bss_type` maps primary, discovery device, and up to two P2P connection BSS configs. `struct p2p_bss` stores per-BSS vif pointers. `enum brcmf_p2p_status` defines bit positions for enablement, interface add/delete/change, action-frame progress, GO negotiation, listen, response wait, and common-channel search. `struct afx_hdl` stores action-frame channel-search work/completion state. `struct brcmf_p2p_info` is the main state object embedded in cfg80211 info. Function declarations expose attach/detach, vif add/delete, role change, start/stop, scan prep, remain/cancel ROC, event notifications, action-frame send, common-channel scan hook, and probe-request notification.

Control flow and state: the header makes `brcmf_p2p_info` visible so other driver components can embed and inspect P2P state. Status bits are used as a compact state machine across cfg80211 ops and firmware event callbacks. Completions synchronize action-frame send and channel-search flows.

Dependencies and integration: includes cfg80211 and references `brcmf_cfg80211_info`, `brcmf_cfg80211_vif`, `brcmf_if`, `brcmf_fil_af_params_le`, `brcmf_bss_info_le`, and firmware event messages. It is the contract between generic cfg80211 glue and the P2P implementation.

Risks: status enum ordering is ABI-like within the driver because bits are stored in `unsigned long status`; reordering changes behavior. Shared mutable fields such as `remain_on_channel_cookie`, `next_af_subtype`, `block_gon_req_tx`, and AFX channel fields require disciplined locking or single-thread assumptions from callers/events. Public structure exposure increases coupling.

Test signals: build coverage of cfg80211/P2P users, lifecycle tests for all bss index slots, concurrent action-frame and remain-on-channel operations, and event callbacks after interface removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/p2p.h -->
