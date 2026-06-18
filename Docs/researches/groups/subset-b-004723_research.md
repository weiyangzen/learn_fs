# subset-b-004723

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/usb.c

## Purpose
`usb.c` implements the ath10k USB HIF bus backend for Qualcomm Atheros USB 802.11ac devices. It binds a USB interface to an `ath10k` core instance, discovers endpoint pipes, manages URB pools, moves HTC frames between USB bulk pipes and the ath10k HTC/WMI/HTT layers, exposes BMI and diagnostic control-message access, and registers the Linux `usb_driver`.

## Important APIs, Types, and Functions
The HIF surface is `ath10k_usb_hif_ops`, with implementations for `tx_sg`, BMI exchange, diagnostic read/write, start/stop, service-to-pipe mapping, queue accounting, and power hooks. USB lifecycle entry points are `ath10k_usb_probe()`, `ath10k_usb_disconnect()`, and the optional PM callbacks. Pipe and URB management is centered on `ath10k_usb_alloc_urb_from_pipe()`, `ath10k_usb_free_urb_to_pipe()`, `ath10k_usb_alloc_pipe_resources()`, `ath10k_usb_setup_pipe_resources()`, `ath10k_usb_flush_all()`, and `ath10k_usb_cleanup_pipe_resources()`. Runtime I/O flows through `ath10k_usb_post_recv_transfers()`, `ath10k_usb_recv_complete()`, `ath10k_usb_transmit_complete()`, and `ath10k_usb_io_comp_work()`.

## Control Flow, State, and Persistence
Probe assumes USB devices are QCA9377-class, creates `struct ath10k` with USB-private storage, adds NAPI, initializes `struct ath10k_usb`, maps USB descriptors into logical pipes, and registers the ath10k core as a high-latency device. `ath10k_usb_create()` initializes locks, per-pipe work queues and skb queues, diagnostic buffers, and endpoint resources. Start enables NAPI, posts RX URBs on `ATH10K_USB_PIPE_RX_DATA`, and sets TX wake thresholds to half of each TX URB pool. Stop, power-down, suspend, disconnect, and destroy all converge on killing anchored URBs and canceling pipe work.

RX completion validates URB status and length, queues received skbs to a per-pipe completion queue, returns the URB context to the free list, and reposts receives when free contexts exceed a threshold. Worker context parses the HTC header, validates service connection and payload/trailer lengths, processes HTC trailers, strips headers/trailers, calls the endpoint `ep_rx_complete()` callback, and schedules NAPI when the core is registered. TX completion returns the URB context and forwards the transmitted skb to HTC completion handling. The persistent state is in `struct ath10k_usb` and each `struct ath10k_usb_pipe`: USB device/interface pointers, pipe descriptors, free URB context lists, counts, anchors for submitted URBs, completion queues, and diagnostic command/response buffers.

## Dependencies and Integration Points
The file depends on Linux USB, workqueue, skb, NAPI, and module infrastructure, plus ath10k `core`, `hif`, `htc`, `htt`, `bmi`, and `debug` layers. It maps HTC services so WMI/control traffic uses TX control and RX data pipes, while HTT data uses TX data low priority and RX data. BMI and diagnostic transactions use vendor control requests on endpoint zero. RX frames are handed to HTC endpoint callbacks and HTT high-latency receive processing via `ath10k_htt_rx_hl_indication()`. The USB device table currently binds Linksys WUSB6100M.

## Risks and Test Signals
The driver warns that USB support is incomplete, so the highest risks are lifecycle races and protocol mismatches rather than stable production behavior. Important risks include URB context leaks, double ownership of skbs across completion paths, RX repost starvation after allocation or submit failures, malformed HTC trailer handling, invalid endpoint descriptors, partial PM support, the fixed QCA9377 hardware assumption, and service-to-pipe mapping that ignores unsupported services. Control-message helpers copy fixed response sizes and do not use the returned byte count to adjust `resp_len`, so diagnostic/BMI response-size behavior should be checked carefully.

Test signals should include probe/disconnect with repeated bind/unbind, endpoint discovery with all expected USB endpoint addresses, RX/TX URB submission failure injection, zero-length and errored URB completions, HTC trailer-only and malformed frames, BMI firmware boot exchange, diagnostic read/write, NAPI receive budget behavior, PM suspend/resume paths when enabled, and leak checks for `urb_alloc == urb_cnt` after teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/usb.h

## Purpose
`usb.h` defines the private USB bus contract used by `usb.c`: endpoint constants, control request IDs, diagnostic message formats, logical pipe IDs, pipe/device state containers, URB context state, and the helper that retrieves USB-private data from `struct ath10k`.

## Important APIs, Types, and Functions
Constants define 32 TX and 32 RX URB contexts per mapped pipe and a 4096-byte RX buffer. Endpoint address macros map firmware application endpoints to logical pipe IDs: control/data/data2/interrupt IN endpoints and control/low/medium/high data OUT endpoints. Vendor control request IDs cover BMI send/receive and diagnostic command/response transactions. Packed structures `ath10k_usb_ctrl_diag_cmd_write`, `ath10k_usb_ctrl_diag_cmd_read`, and `ath10k_usb_ctrl_diag_resp_read` define the little-endian USB diagnostic protocol. `enum ath10k_usb_pipe_id` defines the logical pipe namespace, and `ath10k_usb_priv()` casts `ar->drv_priv` to `struct ath10k_usb`.

## Control Flow, State, and Persistence
`struct ath10k_usb_pipe` persists all per-endpoint runtime state: free URB context list, submitted URB anchor, total and available URB counts, repost threshold, USB pipe handle, endpoint address, logical pipe number, max packet size, TX flag, completion work, skb completion queue, and endpoint descriptor pointer. `struct ath10k_usb` persists global USB state: the spinlock protecting pipe free lists and counts, Linux USB device/interface, all pipes, diagnostic buffers, and the owning `ath10k` pointer. `struct ath10k_urb_context` binds a submitted or free URB context to its pipe and current skb.

## Dependencies and Integration Points
The header relies on Linux USB, skb, list, workqueue, and bit macros made available through the including C file and ath10k headers. Its structures are consumed by `usb.c` and are sized as the private tail allocated by `ath10k_core_create()`. Endpoint constants must agree with the USB firmware interface and with `ath10k_usb_get_logical_pipe_num()` in `usb.c`; diagnostic structures must agree with target firmware control-message parsing.

## Risks and Test Signals
Risks are mostly ABI and state-layout risks. Endpoint address changes, diagnostic command-size changes, or new chipset pipe layouts require synchronized updates in both the header and pipe setup logic. `ATH10K_USB_PIPE_INVALID` aliases `ATH10K_USB_PIPE_MAX`, so bounds checks must reject it before indexing. The shared `cs_lock` protects only the free list and count, not every pipe field. Test signals include compile coverage for the private structures, descriptor-to-pipe mapping tests, validation of packed diagnostic payload sizes and endianness, and teardown checks that all allocated URB contexts return to the pipe free list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wmi-ops.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wmi-ops.h

## Purpose
`wmi-ops.h` is the ath10k WMI abstraction layer. It defines the firmware-family-specific `struct wmi_ops` vtable and provides inline wrappers that validate operation availability, call TLV/main/10.x generators or parsers, and send generated command skbs with the command IDs from `ar->wmi.cmd`.

## Important APIs, Types, and Functions
The central type is `struct wmi_ops`. It groups receive dispatch (`rx`), service bitmap mapping, event pull/parsing callbacks, command skb generators, cleanup hooks, firmware statistics formatting, vdev subtype translation, and feature-specific command builders. Inline wrappers include receive and parser helpers such as `ath10k_wmi_rx()`, `ath10k_wmi_pull_scan()`, `ath10k_wmi_pull_mgmt_rx()`, `ath10k_wmi_pull_svc_rdy()`, `ath10k_wmi_pull_fw_stats()`, and `ath10k_wmi_pull_wow_event()`. Command wrappers cover pdev, scan, vdev, peer, power-save, WMM, beacon/probe templates, management TX, debug/pktlog, thermal, block-ack, WOW, TDLS, adaptive QCS, survey, echo, radar, spectral, GPIO, and per-peer-per-TID operations.

## Control Flow, State, and Persistence
Most wrappers follow the same pattern: check that the relevant `ar->wmi.ops` callback exists, generate or parse data, translate `ERR_PTR()` to a negative errno, then call `ath10k_wmi_cmd_send()` or `ath10k_wmi_cmd_send_nowait()` with the corresponding ID from `ar->wmi.cmd`. Pull wrappers return parsed common ath10k argument structures without owning persistent state. Send wrappers transfer command skb ownership to the WMI command path on success. A few wrappers have special behavior: management TX without firmware ACK support marks the original mac80211 skb ACKed immediately; beacon DMA uses the nowait send path and frees the command skb on failure; `ath10k_wmi_get_txbf_conf_scheme()` returns an unsupported enum when absent; and unsupported callbacks consistently return `-EOPNOTSUPP`.

## Dependencies and Integration Points
This header connects high-level ath10k MAC/core code to firmware-specific WMI implementations such as `wmi-tlv.c`. It depends on `struct ath10k`, `struct ath10k_wmi`, command maps, parameter maps, WMI argument structures, mac80211 skb metadata, and the common command send functions. It is the primary integration contract that lets shared code call the same `ath10k_wmi_*()` helpers regardless of whether the device uses TLV, mainline, or older WMI encodings.

## Risks and Test Signals
The main risks are incomplete vtable implementations, mismatched command IDs, and ownership mistakes when a generator succeeds but command send fails. Callers must tolerate `-EOPNOTSUPP` for firmware families that do not implement a feature. Some wrappers assume callbacks exist without a guard, notably `ath10k_wmi_vdev_wmm_conf()`, so attach-time ops completeness matters. `ath10k_wmi_gpio_output()` checks `gen_gpio_config` instead of `gen_gpio_output`, which is a review target because it can report support based on the wrong callback. Test signals include build coverage across all WMI variants, feature probes that exercise unsupported paths, command-send failure injection to verify skb ownership, management TX completion/cleanup tests, and static checks that every wrapper uses the correct command ID and vtable member.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wmi-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wmi-tlv.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wmi-tlv.c

## Purpose
`wmi-tlv.c` implements the WMI TLV firmware protocol variant for ath10k. It parses TLV-encoded firmware events into common ath10k event arguments, generates TLV-encoded command skbs, maps generic command/parameter/flag names to TLV IDs, and attaches this implementation to `ar->wmi`.

## Important APIs, Types, and Functions
Core TLV parsing helpers are `ath10k_wmi_tlv_iter()`, `ath10k_wmi_tlv_parse()`, `ath10k_wmi_tlv_parse_alloc()`, and `ath10k_wmi_tlv_len()`, backed by `wmi_tlv_policies[]` minimum-length checks. Receive dispatch is `ath10k_wmi_tlv_op_rx()`, which strips the WMI command header, traces the event, allows testmode consumption, and switches over TLV event IDs. Event handlers include beacon TX status, peer stats info, diagnostic data, P2P notice-of-absence, TX pause, rfkill state, temperature, TDLS peer teardown, peer delete response, and many common events delegated to shared WMI handlers.

Pull callbacks translate TLV payloads into common structures for scan, management RX/TX completion, bundled management TX completion, channel info, vdev start, peer kickout, SWBA, PHY error header, service ready, ready, service available, firmware stats, roam, WOW, and echo events. Command generators cover pdev suspend/resume/regdomain/params/WMM/quiet/temperature, init/resource config, scans, vdev lifecycle and keys, peer lifecycle and association, power save, scan channel lists, beacon/probe/P2P templates, stats requests, management TX send, debug/pktlog, WOW and PNO, TDLS, adaptive QCS, echo, and spectral configuration. `wmi_tlv_cmd_map`, `wmi_tlv_pdev_param_map`, `wmi_tlv_peer_param_map`, `wmi_tlv_vdev_param_map`, `wmi_tlv_ops`, and `wmi_tlv_peer_flags_map` provide the attach-time protocol maps.

## Control Flow, State, and Persistence
Incoming WMI skbs enter `ath10k_wmi_tlv_op_rx()`. The function reads the command ID, removes `struct wmi_cmd_hdr`, traces the raw event, optionally lets testmode consume it, then dispatches by event ID. Most TLV event parsing allocates a tag-indexed table, validates required tags, copies little-endian fields into common argument structures, and frees the table. More complex events use iterator state machines: service-ready parsing separates ABI, regulatory capabilities, service bitmap, and memory requests; SWBA parsing expects matching TIM and NOA arrays for each vdev in the bitmap; management TX bundle parsing records ordered `ARRAY_UINT32` sections for descriptor IDs, status, PPDU IDs, and optional ACK RSSI.

Outgoing commands allocate an skb of exact TLV size, write one or more `struct wmi_tlv` headers, fill firmware structures with little-endian values, and append variable arrays or nested TLVs as needed. Persistent state is not owned by this file, but it reads and updates `ar->wmi` state: service maps, memory chunks, RX decap mode, pending management TX IDR, WOW limits, command maps, and parameter maps. Management TX send allocates an IDR descriptor under `ar->data_lock`, stores the original skb and DMA address, writes the descriptor ID into the WMI command, and later `cleanup_mgmt_tx_send` removes and frees the pending record. `ath10k_wmi_tlv_attach()` installs all TLV maps and ops into the device.

## Dependencies and Integration Points
The implementation depends on ath10k core, MAC, hardware parameters, WMI common helpers, WMI TLV structure definitions, P2P, testmode, TX/RX state, debug tracing, Linux bitfield helpers, mac80211, cfg80211 rfkill, RCU, IDR, and skb APIs. It integrates upward through the `wmi_ops` contract in `wmi-ops.h` and downward through firmware-defined TLV tags, event IDs, command IDs, service bits, and resource configuration fields. It delegates common event handling and common structure filling to shared WMI helpers where possible, while supplying TLV-specific ABI checks and layout generation.

## Risks and Test Signals
The largest risks are protocol layout drift, incomplete length validation for variable or nested arrays, and ownership/state mistakes in asynchronous management TX. TLV parser policy coverage is partial, so unlisted tags depend on downstream handlers for structure-size safety. Several generator lengths are manually computed and must stay aligned with firmware expectations; examples include scan arrays, beacon/probe template payloads, WOW pattern lists, PNO lists, TDLS channel arrays, and host memory chunks. The service-ready ABI check rejects mismatched firmware namespaces/versions, making firmware compatibility explicit but brittle. Some features are intentionally unimplemented in `wmi_tlv_ops`, so callers must use `-EOPNOTSUPP` paths.

Test signals should include fuzzing TLV event parsing with truncated headers, oversized lengths, missing required tags, duplicate ordered arrays, and invalid nested SWBA/peer-stat structures. Runtime coverage should exercise service-ready/ready boot, init resource config with and without extended DMA addresses, scan start/stop, vdev start/restart, peer association rate arrays, key install validation, management TX send and completion cleanup, rfkill and thermal events, WOW pattern and PNO start/stop, TDLS peer updates, firmware stats parsing including extended peer duration, and command-send failure paths under allocation pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wmi-tlv.c -->
