# Research: subset-b-004827

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/main.c

## Purpose

`mei/main.c` implements the Intel wireless host-to-CSME SAP transport over the Linux MEI client bus. It binds to the WLAN MEI UUID, allocates DMA shared memory, starts the SAP handshake, exports the iwlwifi-facing `iwl_mei_*` API, and coordinates NIC ownership, AMT state, NVM retrieval, PLDR reset, rfkill/link notifications, CSME packet forwarding, netdev RX handler registration, debugfs, probe, and teardown.

## Important APIs, Types, and Functions

Central state is `struct iwl_mei`, which holds wait queues, shared-memory pointers, cached firmware data, RCU filters, ownership flags, work items, sequence counters, and debugfs state. `struct iwl_mei_cache` buffers iwlwifi-provided callbacks and configuration while no MEI device is bound. Exported APIs include `iwl_mei_is_connected()`, `iwl_mei_get_nvm()`, `iwl_mei_pldr_req()`, `iwl_mei_get_ownership()`, `iwl_mei_alive_notif()`, association/rfkill/NIC/MCC/SAR/netdev setters, device-up/down notification, and driver register/unregister functions.

Key helpers allocate/init the SAP shared area (`iwl_mei_alloc_shared_mem()`, `iwl_mei_init_shared_mem()`), write circular queues (`iwl_mei_write_cyclic_buf()`), signal CSME with `SAP_ME_MSG_CHECK_SHARED_AREA`, parse inbound SAP notification/data queues, and dispatch SAP message handlers.

## Control Flow

Probe allocates `struct iwl_mei`, initializes work and wait queues, maps a SAP v4 shared area with fallback to v3, initializes queue layout, enables the MEI client, registers the RX callback, sends `SAP_ME_MSG_START`, and finally publishes `iwl_mei_global_cldev`. `SAP_ME_MSG_START_OK` validates the negotiated SAP version and sets the connected bit. Later `AMT_STATE` starts the cached initial configuration flow: WiFi-driver-up, ownership query, cached host link, MCC, SAR, NIC info, and rfkill messages.

SAP payloads move through shared circular queues. Host-to-CSME notification/data writes update write pointers and then send a MEI doorbell unless throttled. CSME-to-host doorbells cause notification queue parsing, per-message dispatch, data queue parsing into skbs, and deferred `dev_queue_xmit()` outside `iwl_mei_mutex`.

## State and Persistence Behavior

Long-lived state is split between global connection state, the singleton MEI device pointer, shared DMA queue metadata, cached iwlwifi configuration, and RCU-published netdev/filter pointers. Ownership, AMT enablement, link-protection, device-down, PLDR, and throttle flags determine whether messages are sent or callbacks are invoked. Remove carefully sends `HOST_GOES_DOWN`, waits for host-to-ME queues to drain, clears the connected bit under `data_q_lock`, unregisters RX handlers, disables MEI outside the mutex, cancels work, wakes waiters, unmaps DMA memory, and frees cached dynamic state.

## Dependencies and Integration Points

This file integrates the MEI client bus, iwlwifi's `iwl-mei.h` callback contract, Linux netdev RX handlers, RCU, wait queues, debugfs, skbs, cfg80211/mac80211 connection data, and SAP protocol definitions in `sap.h`. `net.c` supplies the packet filters and DHCP copy path. Tracepoints in `trace.h` and `trace-data.h` instrument SAP commands and packet payloads.

## Risks and Edge Cases

The file is concurrency-heavy: `iwl_mei_mutex`, `data_q_lock`, RCU, RTNL, work cancellation, and MEI RX callback shutdown must remain ordered. Circular queue pointer validation protects against corrupt CSME state, but full/empty accounting uses simple read/write positions and no reserved slot, so queue-size assumptions are important. `iwl_mei_send_sap_msg_payload()` calls `iwl_mei_write_cyclic_buf(q_head, notif_q, ...)`, whose first parameter is typed as `struct mei_cl_device *`; the function does not dereference it except in error paths, making the call compile but fragile if logging is refactored. Timeout-based NVM, ownership, and PLDR waits must tolerate device removal and wakeups during teardown.

## Test Signals

Useful signals are MEI bind/unbind, suspend/resume, AMT enabled/disabled transitions, ownership steal/retake, PLDR success/failure, netdev replacement under RTNL, SAP v3/v4 allocation fallback, queue wraparound, invalid pointer/length injection, NVM timeout, and packet forwarding with CSME filters enabled. Dynamic validation should watch tracepoints, rfkill callbacks, absence of IOMMU errors on remove, and no UAF after RX-handler unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/net.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/net.c

## Purpose

`net.c` implements CSME packet selection for iwlmei. It evaluates CSME-provided out-of-band filters against received Ethernet/IP/ARP traffic, copies selected inbound frames into the SAP shared-memory data queue, and exports a TX-side helper that mirrors DHCP client packets to CSME.

## Important APIs, Types, and Functions

The public functions are `iwl_mei_rx_filter()` and `iwl_mei_tx_copy_to_csme()`. Local filters include `iwl_mei_rx_filter_eth()` for multicast L2 filters, `iwl_mei_rx_filter_arp()` for IPv4 ARP request/reply policy, `iwl_mei_rx_filter_ipv4()` for IPv4 and ICMP handling, `iwl_mei_rx_filter_tcp_udp()` for flex TCP/UDP port filters, and a stub `iwl_mei_rx_filter_ipv6()`.

## Control Flow

The netdev RX handler in `main.c` calls `iwl_mei_rx_filter()`. This first asks `iwl_mei_rx_pass_to_csme()` whether CSME should receive the frame and whether the host stack should still see it. If CSME should receive a pass-through packet, the code copies the skb; if CSME consumes it, it reuses the original. It restores the MAC header, appends a SAP data header through `iwl_mei_add_data_to_ring()`, and frees only copied skbs.

The TX mirror path is narrower. `iwl_mei_tx_copy_to_csme()` only copies IPv4 UDP DHCP client-to-server frames, reconstructs an Ethernet header from the 802.11 header, strips 802.11/IV/SNAP bytes while preserving the ethertype, wraps it in `SAP_MSG_CB_DATA_PACKET`, and queues it to CSME.

## State and Persistence Behavior

`net.c` itself stores no durable state. It consumes immutable snapshots of `struct iwl_sap_oob_filters` published by `main.c` and mutates transient skb header offsets while filtering. Packet copies become persistent only after `iwl_mei_add_data_to_ring()` writes them into shared SAP memory.

## Dependencies and Integration Points

It depends on Linux skb pull/headroom helpers, Ethernet/ARP/IP/UDP/ICMP headers, cfg80211/mac80211 802.11 header helpers, SAP filter structures, and `iwl_mei_add_data_to_ring()` from `main.c`.

## Risks and Edge Cases

IPv6 filtering is explicitly TODO, except for an ICMPv6 branch inside the IPv4 parser that is unreachable for true IPv6 packets. TCP filtering intentionally reads only a UDP-sized header, which matches the first source/destination port fields but relies on the earlier pull length. Header offset manipulation in the DHCP TX path is sensitive to IV length and SNAP assumptions. Filter arrays stop scanning after the first disabled entry, so CSME must send filters packed without holes.

## Test Signals

Exercise multicast L2 stop/copy flags, ARP target matching and wildcarding, ICMP echo suppression, TCP/UDP flex filters with and without IP matching, pass/copy/consume outcomes, truncated skb handling, DHCP TX mirroring, and IPv6 non-support behavior. KUnit or packet-injection tests should verify skb ownership and that consumed originals are freed only by the RX handler caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/sap.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/sap.h

## Purpose

`sap.h` is the protocol contract for SAP, the Intel wireless host/CSME interface used by iwlmei. It documents the handshake, ownership model, host driver state messages, and data forwarding model, then defines all wire-format MEI messages, SAP notifications, data headers, ownership values, connection data, filters, NVM payloads, rfkill flags, SAR limits, and PLDR structures.

## Important APIs, Types, and Functions

The header has no functions; its public surface is packed protocol data. Core types include `struct iwl_sap_me_msg_hdr`, `struct iwl_sap_me_msg_start`, `struct iwl_sap_me_msg_start_ok`, `enum iwl_sap_msg`, `struct iwl_sap_hdr`, `struct iwl_sap_msg_dw`, `enum iwl_sap_nic_owner`, `struct iwl_sap_notif_connection_info`, host link up/down/NIC/MCC/SAR structures, `struct iwl_sap_nvm`, filter structures, `struct iwl_sap_oob_filters`, `struct iwl_sap_csme_filters`, `struct iwl_sap_cb_data`, and PLDR request/ack/end payloads.

## Control Flow

The defined flow is: MEI client startup sends `SAP_ME_MSG_START`, CSME replies `SAP_ME_MSG_START_OK`, and both sides then use MEI `CHECK_SHARED_AREA` messages as shared-memory doorbells. Host lifecycle messages advertise WiFi-driver up/down, host link state, country/SAR/NIC/radio state, ownership requests/confirmations, and host shutdown. CSME messages report AMT state, filters, connection status, NVM data, ownership requests, and PLDR acknowledgements.

## State and Persistence Behavior

All multi-byte fields intended for the wire are little-endian unless explicitly network-order IP/port fields are used. Most structures are `__packed`, so both host and CSME must preserve exact layout. The filter block can persist across many packets after `main.c` RCU-publishes it. NVM, rekey, radio, connection, and ownership fields are not stored here but are cached by `main.c` consumers.

## Dependencies and Integration Points

The header maps SAP auth/cipher enumerations to public iwlmei constants from `mei/iwl-mei.h`. It is consumed by `main.c`, `net.c`, and tracepoint headers. External integration depends on CSME firmware using the same numeric message IDs and packed layouts.

## Risks and Edge Cases

Protocol drift is the main risk: changing enum values, packing, array sizes, or endian annotations breaks firmware compatibility. Several documented fields are marked TODO/TBD, which limits validation of host-suspend and filter behavior. `struct iwl_sap_cb_data` has a flexible payload and a special DHCP filter bit, so length checks must happen in users. IPv6 and VLAN filter definitions exist even though current `net.c` support is incomplete.

## Test Signals

Compile-time checks should validate expected structure sizes where firmware ABI demands them. Runtime tests should cover SAP v3/v4 negotiation, message length validation in `main.c`, filter application in `net.c`, NVM conversion, PLDR request/ack, and ownership transfer message ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/sap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/trace-data.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/trace-data.h

## Purpose

`trace-data.h` defines the iwlmei SAP data tracepoint when `CONFIG_IWLWIFI_DEVICE_TRACING` is enabled, and compiles to a no-op macro when tracing is disabled. It lets developers trace packet payload movement between CSME, the air interface, and DHCP TX mirroring without adding runtime instrumentation in normal builds.

## Important APIs, Types, and Functions

The exported macro/function interface is `trace_iwlmei_sap_data(skb, trace_type)`. `enum iwl_sap_data_trace_type` distinguishes RX-to-air packets, TX data from air, RX data dropped from air, and TX DHCP copies. `iwlmei_sap_data_offset()` chooses how much SAP header material to skip before copying packet bytes into the dynamic trace array.

## Control Flow

When tracing is enabled, the trace event copies `skb->len - offset` bytes from the skb into a dynamic trace payload and records the trace type. `main.c` emits this trace around shared-memory data queue writes, CSME-to-host transmissions, and drops; `net.c` indirectly uses it through `iwl_mei_add_data_to_ring()`.

## State and Persistence Behavior

There is no driver state. Trace records persist only in the kernel tracing buffers selected by the user. Offsets depend on the SAP wrapping type, so trace consumers see packet data rather than the SAP data header for most host-to-CSME cases.

## Dependencies and Integration Points

The header depends on tracepoint infrastructure, skb helpers, and `sap.h`. It is included by `trace.c` with `CREATE_TRACE_POINTS` and by instrumented code as a normal trace header.

## Risks and Edge Cases

Bad offset selection could make `skb_copy_bits()` read an invalid range, so every new SAP data wrapper type needs a matching offset rule and a disabled-tracing stub. Dynamic payload tracing can expose packet contents; enablement should be treated as debug-only.

## Test Signals

Build with tracing disabled to verify the no-op macro path, and with tracing enabled to verify tracepoint generation. Exercise all four trace types with packet sizes at and below wrapper lengths to catch offset issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/trace-data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/trace.c

## Purpose

`trace.c` is the tracepoint instantiation unit for iwlmei. It defines `CREATE_TRACE_POINTS` and includes the command and data trace headers so the kernel tracepoint definitions are emitted exactly once.

## Important APIs, Types, and Functions

The file has no runtime functions. Its important symbols are the tracepoints declared in `trace.h` and `trace-data.h`: `iwlmei_sap_cmd`, `iwlmei_me_msg`, and `iwlmei_sap_data`. It includes `linux/module.h` and avoids tracepoint macro expansion under sparse by excluding the body when `__CHECKER__` is defined.

## Control Flow

Build-time control flow is the whole file: with sparse disabled, `CREATE_TRACE_POINTS` causes included trace headers to instantiate tracepoint storage and metadata. With sparse checking, the file compiles without expanding tracepoint macros.

## State and Persistence Behavior

There is no persistent driver state here. Tracepoint state is owned by Linux tracing infrastructure.

## Dependencies and Integration Points

This file integrates with the kernel trace framework and the local iwlmei trace headers. It must be compiled into the same module that references these tracepoints.

## Risks and Edge Cases

Including this file or `CREATE_TRACE_POINTS` in more than one translation unit would cause duplicate tracepoint definitions. Excluding it from the module would leave trace references unresolved in tracing-enabled builds.

## Test Signals

Build the module with `CONFIG_IWLWIFI_DEVICE_TRACING=y` and sparse enabled/disabled. Runtime smoke tests can list the iwlmei trace events under tracing and enable them while sending SAP commands/data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/trace.h

## Purpose

`trace.h` declares iwlmei tracepoints for SAP command messages and MEI doorbell messages. It provides no-op stubs when device tracing is disabled and full tracepoint definitions when enabled.

## Important APIs, Types, and Functions

The callable tracing hooks are `trace_iwlmei_sap_cmd(const struct iwl_sap_hdr *, bool tx)` and `trace_iwlmei_me_msg(const struct iwl_sap_me_msg_hdr *, bool tx)`. `iwlmei_sap_cmd` records a dynamic copy of the SAP command plus direction, type, length, and sequence. `iwlmei_me_msg` records ME message type, sequence, and direction.

## Control Flow

Instrumented code in `main.c` calls these hooks before sending commands and after receiving ME/SAP messages. Tracepoint metadata is included through `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` so `trace.c` can instantiate it.

## State and Persistence Behavior

No state is stored in the driver. Trace events are transient records in ftrace/perf buffers. SAP command tracing copies the full command payload, so it observes the command as it was at trace time.

## Dependencies and Integration Points

It depends on Linux tracepoint macros and SAP protocol structures. The include path uses `"mei/sap.h"` and a local `TRACE_INCLUDE_PATH .`, so build include paths must match the iwlwifi directory layout.

## Risks and Edge Cases

Tracing command payloads can expose firmware-control data. Any new SAP command structure can be traced without header-specific decoding, but the length field must be validated by callers before they hand a pointer to this tracepoint. Stub parity must be maintained when adding new trace hooks.

## Test Signals

Compile both tracing-disabled and tracing-enabled configurations, enable trace events during SAP startup/ownership/NVM flows, and verify printed type/length/sequence values match driver logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/Makefile

## Purpose

The MLD `Makefile` defines how the `iwlmld.o` opmode object is built. It selects the module under `CONFIG_IWLMLD`, includes KUnit tests under `CONFIG_IWLWIFI_KUNIT_TESTS`, and conditionally adds debugfs, LED, and D3 power-management objects.

## Important APIs, Types, and Functions

The key build variables are `obj-$(CONFIG_IWLMLD)`, `obj-$(CONFIG_IWLWIFI_KUNIT_TESTS)`, `iwlmld-y`, and conditional `iwlmld-$(CONFIG_IWLWIFI_DEBUGFS)`, `iwlmld-$(CONFIG_IWLWIFI_LEDS)`, and `iwlmld-$(CONFIG_PM_SLEEP)`. `subdir-ccflags-y += -I$(src)/../` exposes parent iwlwifi headers to all MLD sources.

## Control Flow

Kbuild composes `iwlmld.o` from core files such as `mld.o`, `mac80211.o`, `fw.o`, `power.o`, `iface.o`, `link.o`, `rx.o`, `scan.o`, `sta.o`, `tx.o`, `agg.o`, `ap.o`, `mlo.o`, `ftm-initiator.o`, and others. Feature flags add optional files only when their kernel configuration symbols are enabled.

## State and Persistence Behavior

There is no runtime state. The file determines which code paths exist in a given kernel image or module.

## Dependencies and Integration Points

It integrates MLD with Kbuild, parent iwlwifi headers, KUnit tests, debugfs, LEDs, and PM sleep support. Missing an object here makes matching prototypes unusable at link time.

## Risks and Edge Cases

Feature-guard drift is the main risk: code that references debugfs, LED, or D3 symbols must be compiled only when the matching object is present. The broad parent include path can hide missing local includes.

## Test Signals

Build with `CONFIG_IWLMLD=y/m`, with and without debugfs, LEDs, PM sleep, and KUnit tests. Link failures and undefined references are the primary regression signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/agg.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/agg.c

## Purpose

`agg.c` implements MLD RX Block Ack aggregation support: firmware BAID allocation/removal, software reorder buffering per BAID/RX queue, release notifications, BAR-driven releases, BA session timeout handling, and station-mask updates when MLO station IDs change.

## Important APIs, Types, and Functions

Public functions are `iwl_mld_reorder()`, `iwl_mld_ampdu_rx_start()`, `iwl_mld_ampdu_rx_stop()`, `iwl_mld_handle_frame_release_notif()`, `iwl_mld_handle_bar_frame_release_notif()`, `iwl_mld_del_ba()`, and `iwl_mld_update_sta_baids()`. Local helpers release stored frames, process firmware release notifications, start/stop BA in firmware with `RX_BAID_ALLOCATION_CONFIG_CMD`, initialize/free reorder buffers, and expire inactive sessions through mac80211's BA timer callback.

## Control Flow

Starting an A-MPDU RX session allocates cacheline-aligned per-queue reorder entries, sends an ADD BAID command, records the firmware BAID in station TID state, initializes per-queue windows, starts an inactivity timer if requested, and publishes BAID data through RCU. Incoming MPDUs with valid BAIDs are verified against station mask and TID, duplicate/old frames are dropped, immediately releasable frames pass upward, and out-of-order frames are queued by sequence number. Firmware release or BAR notifications release buffered lists up to NSSN. Stopping a session removes it from firmware unless restarting, synchronizes RX queues with an internal DELBA notification, purges unexpected leftovers, clears the RCU pointer, and frees by `kfree_rcu()`.

## State and Persistence Behavior

Persistent state includes `mld->fw_id_to_ba[]`, `mld->num_rx_ba_sessions`, each station's `tid_to_baid[]`, BAID station masks, reorder windows, per-queue stored frame lists, inactivity timers, and last-RX timestamps. RCU protects RX-side lookups from teardown races.

## Dependencies and Integration Points

The file depends on mac80211 sequence arithmetic, skb queues, MLD station/link helpers, firmware RX BAID API structures, command sending in `hcmd.h`, RX queue sync, and packet delivery through `iwl_mld_pass_packet_to_mac80211()`.

## Risks and Edge Cases

Reorder correctness is sensitive to A-MSDU subframes: NSSN is ignored until the last subframe to avoid advancing past missing subframes. BAID/station-mask mismatch falls back to passing packets, which is safer than dropping but can hide firmware mapping bugs. Timer expiry may run during failed restart flows where station pointers are absent. Teardown relies on RX queue synchronization to release all stored skbs; leftover frames trigger WARN and purge.

## Test Signals

KUnit should cover `iwl_mld_reorder()` for in-order, holes, duplicates, old SN, A-MSDU first/last subframes, BAR release, and invalid BAID. Integration tests should verify ADDBA/DELBA firmware commands, BAID exhaustion, MLO station-mask update, restart stop path, timer expiry, and no skb leaks on teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/agg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/agg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/agg.h

## Purpose

`agg.h` declares the MLD RX aggregation/reorder data structures and APIs used by RX, station, and mac80211 operation code.

## Important APIs, Types, and Functions

It defines `struct iwl_mld_reorder_buffer`, `struct iwl_mld_reorder_buf_entry`, `struct iwl_mld_baid_data`, `struct iwl_mld_delba_data`, and `enum iwl_mld_reorder_result`. Prototypes expose BA session start/stop, reorder processing, firmware release notification handlers, internal DELBA release, and station BAID mask update.

## Control Flow

Callers use `iwl_mld_ampdu_rx_start()` and `iwl_mld_ampdu_rx_stop()` from mac80211 AMPDU callbacks. RX uses `iwl_mld_reorder()` per MPDU and follows the returned pass/buffer/drop decision. Notification dispatch calls the frame/BAR release handlers, while RX queue synchronization uses `iwl_mld_del_ba()` to drain buffers during teardown.

## State and Persistence Behavior

The structures are stateful: reorder buffers track head sequence numbers and stored-frame counts per RX queue, entries hold skb lists, BAID data owns session timers and RCU lifetime, and `sta_mask` ties a BAID to one or more firmware station IDs for MLO.

## Dependencies and Integration Points

The header depends on `mld.h`, firmware RX API definitions, skb queues, timers, and RCU conventions. Its exported prototypes are implemented in `agg.c`.

## Risks and Edge Cases

`IWL_MAX_RX_HW_QUEUES` sizes the inline reorder-buffer array, while entries are flex-allocated per actual RX queue count; mismatches must remain bounded. Cacheline alignment and sparse workarounds should be preserved because RX reordering is hot-path and cross-queue cache sharing matters.

## Test Signals

Compile with sparse and normal builds, run aggregation KUnit, and validate struct layout assumptions under different cacheline sizes and RX queue counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/agg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ap.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ap.c

## Purpose

`ap.c` implements AP/IBSS support helpers for the MLD opmode. It builds firmware beacon templates, computes beacon rate flags, locates TIM/CSA/TWT offsets, handles early AP keys that arrive before broadcast/multicast stations exist, and starts/stops AP or IBSS firmware state.

## Important APIs, Types, and Functions

Public entry points are `iwl_mld_set_tim_idx()`, `iwl_mld_get_rate_flags()`, `iwl_mld_send_beacon_template_cmd()`, `iwl_mld_update_beacon_template()`, `iwl_mld_store_ap_early_key()`, `iwl_mld_free_ap_early_key()`, `iwl_mld_start_ap_ibss()`, and `iwl_mld_stop_ap_ibss()`. The main local helper is `iwl_mld_fill_beacon_template_cmd()`.

## Control Flow

Beacon update obtains a mac80211 template, fills link ID, channel-derived FILS and short-SSID data, byte count, beacon rate flags, TIM index for AP mode, BTWT/CSA/ECSA offsets, then sends `BEACON_TEMPLATE_CMD` with the command and beacon payload. AP/IBSS start sends AP TX power constraints for AP mode, updates the beacon template, modifies the link context, adds multicast and broadcast stations, flushes early keys to firmware, updates P2P device state and low-latency flags, and refreshes PHY chandef. Stop reverses active flags and removes broadcast/multicast stations.

## State and Persistence Behavior

State changes include `mld_vif->ap_ibss_active`, low-latency causes, P2P device firmware context, per-link `ap_early_keys[]`, multicast/broadcast station firmware state, and beacon template firmware state. Debugfs beacon injection can temporarily block template updates through `beacon_inject_active`.

## Dependencies and Integration Points

The file depends on mac80211 beacon APIs, cfg80211 channel helpers, firmware beacon command definitions, MLD link/vif/sta/key/power/phy helpers, CRC32 for short SSID, and AP multicast/broadcast station management.

## Risks and Edge Cases

Failure rollback in `iwl_mld_start_ap_ibss()` must remove only resources already added. Early key storage has fixed slots and returns `-ENOSPC` if full. TIM parsing assumes valid beacon element lengths from mac80211. Non-transmitting AP support is gated by a constant currently set false.

## Test Signals

Test AP and IBSS start/stop, beacon updates with/without configured beacon TX rate, 6 GHz FILS/PSC handling, CSA/ECSA/TWT offset reporting, early key storage/removal/send, P2P GO interactions, debugfs beacon injection interaction, and rollback after failures in link modify, multicast, broadcast, or key setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ap.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ap.h

## Purpose

`ap.h` declares the AP/IBSS helper API implemented in `ap.c`, exposing beacon-template, AP lifecycle, early-key, rate-flag, and TIM-index helpers to the rest of MLD.

## Important APIs, Types, and Functions

The prototypes cover `iwl_mld_update_beacon_template()`, `iwl_mld_start_ap_ibss()`, `iwl_mld_stop_ap_ibss()`, `iwl_mld_store_ap_early_key()`, `iwl_mld_free_ap_early_key()`, `iwl_mld_get_rate_flags()`, `iwl_mld_set_tim_idx()`, and `iwl_mld_send_beacon_template_cmd()`.

## Control Flow

mac80211 AP/IBSS callbacks call the lifecycle functions. Debugfs beacon injection reuses rate, TIM, and beacon-send helpers. Key setup code uses early-key helpers when AP group-key installation precedes firmware broadcast/multicast station setup.

## State and Persistence Behavior

The header itself has no storage, but its functions mutate firmware beacon/link/station state and per-link AP early-key arrays.

## Dependencies and Integration Points

It includes MLD core/interface definitions and firmware TX API structures. Consumers must already hold the required wiphy/driver locks described by the implementation.

## Risks and Edge Cases

Prototype drift with `ap.c` and missing includes are the main header risks. Because helpers accept raw mac80211 pointers, callers must supply valid `vif` and `bss_conf` objects for the intended link.

## Test Signals

Build all consumers with AP, IBSS, debugfs, and key-management paths enabled. Static analysis should verify callers handle error returns from start/update/store helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/coex.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/coex.c

## Purpose

`coex.c` handles Bluetooth coexistence initialization and BT activity notifications for MLD.

## Important APIs, Types, and Functions

`iwl_mld_send_bt_init_conf()` sends `BT_CONFIG` with network coexistence mode and MPLUT/high-band retention modules enabled. `iwl_mld_handle_bt_coex_notif()` parses `struct iwl_bt_coex_profile_notif`, treats an all-zero notification as BT-off, updates `mld->bt_is_active`, and invokes `iwl_mld_emlsr_check_bt()`.

## Control Flow

During firmware initialization, the driver sends BT coexistence configuration. Later notification dispatch calls the handler; it ignores no-op state repeats, logs ON/OFF transitions, updates cached activity, and asks MLO/EMLSR code to reevaluate BT-related constraints.

## State and Persistence Behavior

The only local persistent state mutation is `mld->bt_is_active`. Firmware coexistence mode persists after `BT_CONFIG` until firmware reset or reconfiguration.

## Dependencies and Integration Points

The file depends on firmware coexistence API structures, MLD command sending, and EMLSR logic in `mlo.h`.

## Risks and Edge Cases

Using a zeroed whole-structure comparison makes ABI padding and future fields significant. If firmware changes notification layout or adds reserved nonzero fields, BT activity detection may change. The handler does not length-check the packet itself, so dispatch code must guarantee the notification size.

## Test Signals

Validate `BT_CONFIG` is sent on bring-up, BT-on/off notifications toggle `mld->bt_is_active` exactly once per transition, and EMLSR reacts to BT activity. Fuzz notification lengths at the dispatcher if possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/coex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/coex.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/coex.h

## Purpose

`coex.h` declares MLD Bluetooth coexistence APIs.

## Important APIs, Types, and Functions

It exposes `iwl_mld_send_bt_init_conf()` and `iwl_mld_handle_bt_coex_notif()`.

## Control Flow

Firmware bring-up code calls the init function; notification dispatch calls the handler for BT coexistence profile notifications.

## State and Persistence Behavior

The header has no state. The implementation mutates `mld->bt_is_active` and sends persistent firmware coexistence configuration.

## Dependencies and Integration Points

It includes `mld.h` for `struct iwl_mld` and uses `struct iwl_rx_packet` from common firmware RX types through included headers.

## Risks and Edge Cases

Header risks are limited to prototype drift and ensuring consumers include it under the same feature conditions as `coex.c`.

## Test Signals

Build all users and verify notification dispatch links against the handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/coex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/constants.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/constants.h

## Purpose

`constants.h` centralizes tunable MLD policy constants for beacon-loss thresholds, power-save timers, scan/listen parameters, RSSI thresholds, EMLSR defaults, D3/debug options, FTM defaults, and extended capability sizes.

## Important APIs, Types, and Functions

It defines macros such as missed-beacon thresholds, power-save TX/RX data timeouts, snooze/heavy-traffic thresholds, passive scan timeouts, connection listen interval, EMLSR toggles and thresholds, FTM initiator algorithm/parameter defaults, and `IWL_MLD_STA_EXT_CAPA_SIZE`.

## Control Flow

There is no executable control flow. Other MLD components compile these values into power, scan, MLO, FTM, D3, and AP behavior.

## State and Persistence Behavior

The constants are compile-time policy, not runtime state. They indirectly shape firmware commands and driver decisions in many source files.

## Dependencies and Integration Points

The file is included by MLD modules that need shared defaults, including FTM initiator code. Values refer to firmware API constants such as `IWL_TOF_ALGO_TYPE_MAX_LIKE` through the broader include graph.

## Risks and Edge Cases

There is a duplicate definition of `IWL_MLD_PS_SNOOZE_INTERVAL`, currently identical but still a maintenance smell. Policy values are opaque and not runtime-configurable, so tuning requires rebuilds. Changing thresholds can alter roaming, scan, power, and EMLSR behavior across the driver.

## Test Signals

Build with warnings for macro redefinition, run power-save and EMLSR behavioral tests after threshold changes, and validate FTM requests still encode supported defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/constants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/d3.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/d3.c

## Purpose

`d3.c` implements MLD D3 suspend/resume and WoWLAN/net-detect support. It programs wake filters, security replay counters, GTK rekey material, packet patterns, ARP/NS/BTM protocol offloads, beacon filtering, and net-detect scans before suspend, then parses firmware resume notifications, reports wake reasons, reconciles key counters/rekeys, restores power/filter state, and decides whether to keep or drop the connection.

## Important APIs, Types, and Functions

Public APIs are `iwl_mld_no_wowlan_suspend()`, `iwl_mld_no_wowlan_resume()`, `iwl_mld_wowlan_suspend()`, `iwl_mld_wowlan_resume()`, `iwl_mld_set_rekey_data()`, and IPv6 `iwl_mld_ipv6_addr_change()`. Internal state types include `struct iwl_mld_wowlan_status`, `struct iwl_mld_resume_data`, `struct iwl_mld_netdetect_res`, multicast/MLO rekey containers, and key iterator data.

Major helpers convert firmware GTK/PTK/IGTK/BIGTK/MLO key status and sequence counters, validate/convert WoWLAN notification versions, parse wake-packet notifications, build cfg80211 wake reports, update mac80211 key RX sequences, add rekeyed multicast keys, process net-detect match info, wait for D3 notifications, collect suspend-side RSC/TSC state, send KEK/KCK material, configure wake filters, send pattern and protocol-offload commands, and block/unblock EMLSR around WoWLAN.

## Control Flow

No-WoWLAN suspend stops low-latency, powers the device for D3, sends `D3_CONFIG_CMD`, calls transport D3 suspend, cancels async notifications, and marks `in_d3`. No-WoWLAN resume clears `in_d3`, reads D3 debug data, waits for `D3_END_NOTIFICATION`, handles reset-required flags, restarts low latency, and restores device power.

WoWLAN suspend selects the BSS vif. If disconnected, it starts net-detect scheduled scan. If associated, it blocks EMLSR, validates one AP station/link, ensures an offload TX queue, sends `WOWLAN_CONFIGURATION`, security commands, patterns, protocol offload, enables beacon filtering, and updates MAC power. Resume waits for expected notification bits, optionally including wake packet and net-detect match info. It then restores regulatory/power/beacon state unless reset is required, stops net-detect if needed, reports net-detect or WoWLAN wakeup to cfg80211, updates TX queue write pointers and security state, unblocks EMLSR if the connection survives, or asks mac80211 to disconnect.

## State and Persistence Behavior

Persistent driver state includes per-vif rekey data, cached IPv6 target addresses and tentative bitmap, `mld->fw_status.in_d3/resuming/in_hw_restart`, `mld->netdetect`, scan status, EMLSR block state, beacon filter/MAC power state, key sequence counters, PTK PN mirrors for non-default RX queues, and transport TX queue pointers. Resume notification data is heap allocated and freed at the end of the flow.

## Dependencies and Integration Points

The file integrates MLD power, hcmd, interface, MCC, station, MLO, key, scan, beacon-filter, firmware D3/offload APIs, cfg80211 WoWLAN/net-detect reporting, mac80211 key iteration/rekey notification, IPv6 address tracking, transport D3 calls, and firmware debug capture.

## Risks and Edge Cases

Resume depends on receiving a complete notification set within `HZ/3`; missing or malformed notifications force restart/error handling. Notification version 5 is converted to the v6-like internal shape, so firmware ABI drift is sensitive. Security reconciliation must choose correct GTK/IGTK/BIGTK slots and PN endianness. Associated WoWLAN assumes at most one active link; MLO rekeys are added only for valid inactive links. Error paths set `in_hw_restart` and return `1` for firmware D3 errors, which callers must interpret differently from negative unrecoverable errors.

## Test Signals

Exercise no-WoWLAN and WoWLAN suspend/resume, reset-required D3 end flags, net-detect while disconnected, wake reasons with/without wake packets, magic/pattern/disconnect/rekey/rfkill/EAPOL/4-way wake reports, GTK/PTK/IGTK/BIGTK and MLO rekey updates, IPv6 NS offload skipping tentative addresses, ARP offload, pattern command construction, EMLSR block/unblock, and timeout/malformed notification paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/d3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/d3.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/d3.h

## Purpose

`d3.h` declares the MLD D3/WoWLAN public API and per-vif cached data used by suspend configuration.

## Important APIs, Types, and Functions

`struct iwl_mld_rekey_data` stores KEK/KCK lengths, material, replay counter, AKM, and validity. `struct iwl_mld_wowlan_data` stores IPv6 offload addresses/tentative bitmap under `CONFIG_IPV6` plus rekey data. Prototypes expose no-WoWLAN and WoWLAN suspend/resume, rekey data updates, and IPv6 address-change tracking.

## Control Flow

mac80211/cfg80211 callbacks populate rekey and IPv6 state before suspend. PM paths call the suspend/resume entry points depending on whether WoWLAN is configured.

## State and Persistence Behavior

The declared structs live in per-vif MLD state and persist across normal operation until used by D3 suspend. Rekey data remains valid until overwritten; IPv6 target address snapshots are refreshed from inet6 address notifications.

## Dependencies and Integration Points

The header depends on firmware D3 constants, cfg80211 rekey/WoWLAN types, mac80211 vif/hw types, and optional IPv6 structures.

## Risks and Edge Cases

Consumers must guard IPv6 calls with `CONFIG_IPV6`. Rekey buffer lengths must remain within the fixed arrays before `memcpy()` in `d3.c`.

## Test Signals

Build with and without IPv6 and PM sleep. Exercise cfg80211 rekey callbacks and confirm D3 suspend uses the cached material.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/d3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/debugfs.c

## Purpose

`debugfs.c` creates MLD debugfs controls and diagnostics for firmware restart/NMI, echo commands, HE sniffer configuration, TAS status, 6 GHz BIOS policy, packet injection, thermal CTDP, max sleep, PTP timestamping, per-vif power/beacon/low-latency/TWT/internal-MLO-scan controls, AP beacon IE injection, and per-link-station rate/TLC debug commands.

## Important APIs, Types, and Functions

Public registration functions are `iwl_mld_add_debugfs_files()`, `iwl_mld_add_vif_debugfs()`, `iwl_mld_add_link_debugfs()`, and `iwl_mld_add_link_sta_debugfs()`. Important handlers include `iwl_dbgfs_fw_nmi_write()`, `iwl_dbgfs_fw_restart_write()`, `iwl_dbgfs_send_echo_cmd_write()`, `iwl_dbgfs_he_sniffer_params_*()`, `iwl_dbgfs_tas_get_status_read()`, `iwl_dbgfs_wifi_6e_enable_read()`, `iwl_dbgfs_inject_packet_write()`, VIF power/beacon-filter/low-latency handlers, beacon IE injection/restore, TWT setup/operation, internal MLO scan, fixed rate, and TLC DHC.

## Control Flow

Registration adds top-level files under the device debugfs directory, symlinks into mac80211 debugfs, then adds per-vif/per-link/per-link-station directories as mac80211 objects appear. Most write handlers parse user input, reject commands when firmware is stopped or in D3, then send firmware commands or mutate driver debug state under `wiphy_locked_debugfs_*` wrappers. Packet injection hex-decodes an RX packet into a temporary page and calls the MLD RX path with BH disabled.

## State and Persistence Behavior

Debugfs writes can deliberately change runtime state: trigger firmware errors, set `do_not_dump_once`, change monitor AID/BSSID, clear firmware monitor buffers, alter beacon filter and low-latency flags, inject AP beacon IEs, configure TWT, start/stop internal scans, force rates, and update `debug_max_sleep`/`monitor.ptp_time`.

## Dependencies and Integration Points

The file uses MLD hcmd, iface, station, TLC, power, notification, AP, scan, thermal, DHC/RFI/TAS firmware APIs, DMI, hex decoding, debugfs, mac80211 debugfs object lifetimes, and the wrapper macros from `debugfs.h`.

## Risks and Edge Cases

Many handlers are intentionally dangerous and should remain debug-only: firmware NMI/restart, RX injection, beacon injection, TWT override, and fixed-rate commands can disrupt live traffic. Buffer-size macros cap input/output but parsing must stay synchronized with wrapper sizes. `iwl_mld_dbgfs_fw_cmd_disabled()` prevents commands while stopped or in D3, but state-only knobs can still affect later behavior. Beacon IE injection toggles `extra_beacon_tailroom` and must restore it even on errors.

## Test Signals

Build with debugfs, thermal, and PM variants. Validate each file appears in the right top-level/vif/link-sta directory, bad input returns `-EINVAL`, firmware-disabled paths return `-EIO`, TAS read handles invalid firmware responses, packet injection rejects malformed packets, beacon IE restore re-enables normal templates, and symlinks are valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/debugfs.h

## Purpose

`debugfs.h` provides macro templates that generate debugfs open/read/write wrappers for MLD, VIF, link, and link-station objects while taking the wiphy lock through mac80211 debugfs helpers.

## Important APIs, Types, and Functions

Macro families include `MLD_DEBUGFS_OPEN_WRAPPER`, `MLD_DEBUGFS_READ_WRAPPER`, `_MLD_DEBUGFS_READ_FILE_OPS`, `WIPHY_DEBUGFS_WRITE_FILE_OPS`, `WIPHY_DEBUGFS_READ_FILE_OPS_MLD`, `WIPHY_DEBUGFS_WRITE_FILE_OPS_MLD`, `WIPHY_DEBUGFS_READ_WRITE_FILE_OPS_MLD`, and `IEEE80211_WIPHY_DEBUGFS_READ_WRITE_FILE_OPS`. Inline helpers derive `struct iwl_mld *` from link-sta, bss-conf, or vif pointers.

## Control Flow

Generated open methods allocate a small per-file private buffer and store the target object. Read wrappers lazily fill the buffer once and use `simple_read_from_buffer()`. Write wrappers copy bounded user input through `wiphy_locked_debugfs_write()` and dispatch to type-specific `iwl_dbgfs_*_write()` handlers. MLD read/write variants hold buffer state in `dbgfs_*_data`.

## State and Persistence Behavior

The header manages only per-open debugfs private data. It does not own driver state, but generated handlers can mutate driver/firmware state.

## Dependencies and Integration Points

It depends on MLD interface/station helpers, mac80211 object layouts, debugfs file operations, wiphy-locked debugfs helpers, and the naming convention used by `debugfs.c`.

## Risks and Edge Cases

The macros generate many static symbols, so names must be unique per translation unit. Buffer sizes are fixed at declaration sites; undersized buffers truncate input or output expectations. Some wrappers reject `O_RDWR`, so file modes must match supported operations. The inline object-to-MLD conversions assume valid mac80211 backpointers.

## Test Signals

Compile `debugfs.c` with all generated wrappers, open/read/write files repeatedly to check private-data lifetime, verify lockdep sees wiphy locking, and test oversized input against declared buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ftm-initiator.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ftm-initiator.c

## Purpose

`ftm-initiator.c` implements cfg80211 peer measurement FTM initiator support for MLD. It converts PMSR requests into firmware TOF range commands, tracks one active request, translates firmware range responses into cfg80211 PMSR results, and completes or fails outstanding requests across firmware restart.

## Important APIs, Types, and Functions

Public functions are `iwl_mld_ftm_start()`, `iwl_mld_handle_ftm_resp_notif()`, and `iwl_mld_ftm_restart_cleanup()`. Local helpers fill common request fields, map channel definitions to firmware channel/format/BW/control position, set target flags, select associated AP station ID and PMF flag, fill per-target NDP/timing parameters, validate response request ID/count, find peers by BSSID, log results, and reset active state.

## Control Flow

Start rejects concurrent requests and oversized peer lists, fills the request cookie, timeout, randomized MAC template/mask, associated BSSID/TSF MAC ID if needed, and each AP target, then sends `TOF_RANGE_REQ_CMD`. On success it stores the request and wireless device. Firmware response notifications are validated against the active request, each AP entry is matched to a peer, status/failure reason/RTT/RSSI/TSF fields are converted into `cfg80211_pmsr_result`, reported to cfg80211, and response counters update burst indexes. The last report completes the cfg80211 request and clears state. Restart cleanup reports final failures for all peers and completes the request.

## State and Persistence Behavior

Persistent state lives in `mld->ftm_initiator`: active request pointer, requesting wireless device, and per-peer response counters. Request state is cleared on final batch or restart cleanup.

## Dependencies and Integration Points

The file depends on cfg80211 PMSR/FTM APIs, mac80211 VIF association state, MLD vif/station/PHY helpers, firmware location API, MLD constants for FTM defaults, and firmware capability checks for RTT confidence logging.

## Risks and Edge Cases

Only one active FTM request is supported. Unsupported channel widths fail the entire request. The request ID is truncated to `u8` for validation, so cookie collisions in low 8 bits are theoretically possible if firmware also truncates. Secured ranging and unprotected debugfs support are TODO. Host time currently uses boottime at notification processing rather than converted firmware timestamp.

## Test Signals

Test associated and unassociated requests, AP TSF reporting, 20/40/80/160 MHz targets, trigger and non-trigger based flags, PMF flag when associated with MFP, busy/no-response/timeout/success status conversion, multi-peer batching, final completion, concurrent request rejection, unknown BSSID handling, and restart cleanup failure reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ftm-initiator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ftm-initiator.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ftm-initiator.h

## Purpose

`ftm-initiator.h` declares the MLD FTM initiator state and entry points.

## Important APIs, Types, and Functions

`struct ftm_initiator_data` stores the active `cfg80211_pmsr_request`, requesting `wireless_dev`, and per-target response counters. Prototypes expose `iwl_mld_ftm_start()`, `iwl_mld_handle_ftm_resp_notif()`, and `iwl_mld_ftm_restart_cleanup()`.

## Control Flow

mac80211/cfg80211 operation code calls start for a PMSR request. Firmware notification dispatch calls the response handler. Restart/error handling calls cleanup to fail and complete any pending request.

## State and Persistence Behavior

The struct is embedded in MLD state and persists between request start and final completion or cleanup. Response counters survive across batches for periodic measurements.

## Dependencies and Integration Points

The header relies on cfg80211 PMSR and wireless device types plus firmware `IWL_TOF_MAX_APS` sizing through included MLD/location headers in users.

## Risks and Edge Cases

The active request pointer is non-owning; lifetime must be tied to cfg80211's request contract and cleared on all completion paths. `responses[]` must be sized consistently with firmware maximum AP entries.

## Test Signals

Build all FTM users, then exercise normal completion, partial batches, firmware restart cleanup, and rejection of a second request while `req` is non-NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ftm-initiator.h -->
