# subset-b-004866 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qlink.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qlink.h

### Purpose
`qlink.h` is the Quantenna FMAC host/firmware wire-protocol contract. It defines QLINK protocol version 18.1, common message headers, command IDs, command payloads, response payloads, asynchronous event payloads, and TLV encodings used by the driver to translate Linux cfg80211/mac80211 operations into firmware messages.

### Important APIs, Types, And Functions
The file exports packed little-endian structures rather than functions. Core types are `struct qlink_msg_header`, `struct qlink_cmd`, `struct qlink_resp`, `struct qlink_event`, and many command-specific structures such as firmware init/deinit, interface management, scan/connect/AP/channel/regulatory/key/power/WoWLAN/network-device messages. It also defines capability enums, channel/chandef representations, authentication/encryption data, station state/statistics, regulatory rules, HE iftype data, WoWLAN capability containers, and `struct qlink_tlv_hdr` with a fixed `__struct_group()` header and flexible payload.

### Control Flow
Runtime control flow is external: command builders fill these layouts, bus code sends `QLINK_MSG_TYPE_CMD`, firmware answers with matching `QLINK_MSG_TYPE_CMDRSP`, and event code consumes `QLINK_MSG_TYPE_EVENT`. Variable sections are generally TLV arrays or raw IE payloads following fixed headers. Version negotiation starts with `QLINK_CMD_FW_INIT`; later feature use depends on hardware capability bitmaps and response TLVs.

### State, Persistence, And Dependencies
There is no in-memory state in this header. Persistence is the on-wire ABI shared with firmware, including byte order, packing, reserved fields, and alignment. It depends on kernel IEEE 802.11 definitions for HT/VHT/HE capabilities and Ethernet address sizing.

### Integration Points
The command layer, event parser, qlink utility conversion code, regulatory handling, scan/connect/AP setup, station/key management, WoWLAN, OWE/SAE/external-auth paths, and hardware bridge notifications all use these definitions.

### Risks
The ABI is fragile: structure packing, flexible-array offsets, endianness, enum values, and reserved padding must stay synchronized with firmware. Several payloads rely on counts matching trailing TLVs or arrays. Invalid lengths can lead to parser drift if callers do not validate before casting. New protocol fields must be appended, not inserted.

### Test Signals
Useful signals include firmware init version negotiation, parsing band/MAC/HW info TLVs, scan/connect/AP command construction with variable IEs, key and ACL payload lengths, regulatory rule round trips, event length validation, and compatibility tests against older firmware revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qlink_util.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qlink_util.c

### Purpose
`qlink_util.c` converts between QLINK protocol values and Linux cfg80211/nl80211/mac80211 representations. It is the small translation layer that keeps command builders and parsers from open-coding enum, flag, channel, ACL, and regulatory conversions.

### Important APIs, Types, And Functions
Public helpers include `qlink_iface_type_to_nl_mask()`, `qlink_chan_width_mask_to_nl()`, `qlink_chandef_q2cfg()`, `qlink_chandef_cfg2q()`, `qlink_hidden_ssid_nl2q()`, `qtnf_utils_is_bit_set()`, `qlink_acl_data_cfg2q()`, `qlink_utils_band_cfg2q()`, `qlink_utils_dfs_state_cfg2q()`, `qlink_utils_chflags_cfg2q()`, and `qlink_utils_regrule_q2nl()`. Private helpers map individual channel widths and regulatory flags.

### Control Flow
Most functions are switch or bitmask translations. Channel conversion looks up `struct ieee80211_channel` by center frequency for firmware-to-cfg80211 and copies channel fields back for cfg80211-to-firmware. ACL conversion maps cfg80211 policy values then copies the MAC-address array. Regulatory parsing expands QLINK rule flags into nl80211 rule flags and copies frequency/power/CAC values after endian conversion.

### State, Persistence, And Dependencies
The file has no retained state. It depends on `qlink.h`, cfg80211/nl80211 enums, `ieee80211_get_channel()`, endian helpers, and caller-provided destination buffers. Persistence is only the transformed command/response content written elsewhere.

### Integration Points
Command construction for scans, AP setup, channel switches, regulatory notifications, and ACLs uses these helpers. Response/event parsers use them to present firmware channel definitions and regulatory rules to cfg80211.

### Risks
Unknown widths return `(u8)-1` or invalid enum values and depend on callers catching invalid chandefs. `qlink_acl_data_cfg2q()` assumes the destination has enough trailing space for all entries. Flag conversions are intentionally partial; unsupported future flags will be silently dropped unless expanded.

### Test Signals
Tests should cover every enum mapping, invalid width handling, channel lookups that return `NULL`, ACL array sizing, bit-test bounds, regulatory flags including DFS/no-IR/HT/VHT restrictions, and endian-correct round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qlink_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qlink_util.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qlink_util.h

### Purpose
`qlink_util.h` declares QLINK conversion helpers and provides inline TLV append/iteration utilities for command skb construction and response parsing.

### Important APIs, Types, And Functions
Inline helpers are `qtnf_cmd_skb_put_buffer()`, `qtnf_cmd_skb_put_tlv_arr()`, and `qtnf_cmd_skb_put_tlv_u32()`. It declares the conversion functions implemented in `qlink_util.c`. Macros `qlink_for_each_tlv()` and `qlink_tlv_parsing_ok()` implement aligned TLV walking and final-position validation.

### Control Flow
The skb helpers append raw data or TLV headers plus values to an skb. TLV arrays round payload allocation up to `QLINK_ALIGN` while storing the original unpadded length in the header. The iteration macro advances by `sizeof(*tlv) + round_up(len, QLINK_ALIGN)` only while enough bytes remain for both header and declared value.

### State, Persistence, And Dependencies
There is no state. The header depends on skb APIs, cfg80211, QLINK wire definitions, endian helpers, and the caller maintaining sufficient skb tailroom. The persistent effect is serialized QLINK TLV payload in command skbs.

### Integration Points
Command builders use the skb append helpers for IE, bitmap, key, WoWLAN, and regulatory TLVs. Parsers use the TLV loop while processing firmware responses and events.

### Risks
The inline TLV append helper does not explicitly zero alignment padding, so consumers must respect `len` rather than padded bytes. Tailroom is assumed. `qlink_tlv_parsing_ok()` compares against rounded total length, so callers must pass the same logical length convention used by the firmware payload.

### Test Signals
Useful tests include TLV arrays with unaligned lengths, zero-length TLVs, malformed length overruns, exact-end parsing, skb tailroom assertions, and endian checks for u32 TLVs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qlink_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qtn_hw_ids.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qtn_hw_ids.h

### Purpose
`qtn_hw_ids.h` centralizes Quantenna PCI identifiers, chip ID masks, control-register offsets, and firmware image names for qtnfmac PCI hardware.

### Important APIs, Types, And Functions
It defines `PCIE_VENDOR_ID_QUANTENNA`, `PCIE_DEVICE_ID_QSR`, chip ID constants for Topaz and Pearl revisions, firmware file names for PCI Pearl/Topaz, and `qtnf_chip_id_get()`, which reads `QTN_REG_SYS_CTRL_CSR` and masks `QTN_CHIP_ID_MASK`.

### Control Flow
PCI probe code can match vendor/device IDs, map the device registers, call `qtnf_chip_id_get()` to classify the chipset, and choose firmware names and driver behavior based on the returned chip family.

### State, Persistence, And Dependencies
There is no local state. The only persistent contract is the register layout and firmware pathname expected by request-firmware paths. It depends on PCI ID definitions, MMIO `readl()`, and the caller passing a valid mapped register base.

### Integration Points
PCI bus code and utility stringification use the chip IDs. Firmware loading and board-specific setup depend on these constants to select the right image.

### Risks
Bad register mapping or unsupported chip IDs lead to unknown classification. Firmware names are ABI-like user-space paths under `/lib/firmware`, so renames break loading. New hardware revisions require updates to both ID constants and user-facing string conversion.

### Test Signals
Validate PCI ID matching, register reads on supported boards, firmware image selection for Topaz and Pearl variants, unknown-chip logging, and request-firmware failures for missing images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qtn_hw_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/shm_ipc.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/shm_ipc.c

### Purpose
`shm_ipc.c` implements a simple shared-memory IPC channel used by qtnfmac transports. It sends one packet through a 4 KiB MMIO/shared region, signals the peer via a caller-provided interrupt callback, and waits for an ACK flag; inbound packets are drained from workqueue context and delivered to a receive callback.

### Important APIs, Types, And Functions
Public functions are `qtnf_shm_ipc_init()`, `qtnf_shm_ipc_free()`, and `qtnf_shm_ipc_send()`. Internal handlers are `qtnf_shm_ipc_has_new_data()`, `qtnf_shm_handle_new_data()`, `qtnf_shm_ipc_irq_work()`, `qtnf_shm_ipc_irq_inbound_handler()`, and `qtnf_shm_ipc_irq_outbound_handler()`.

### Control Flow
Initialization validates shared-region layout at build time, stores callbacks, selects an inbound or outbound IRQ handler, initializes work and completion state, and clears counters. Inbound IRQ handling checks `NEW_DATA`, queues work, validates `data_len`, calls the RX callback, writes `ACK`, flushes the MMIO write, and interrupts the peer. Outbound send writes `data_len`, copies payload with `memcpy_toio()`, orders writes with barriers, sets `NEW_DATA`, interrupts the peer, waits up to two seconds for completion, then clears `waiting_for_ack`.

### State, Persistence, And Dependencies
State is in `struct qtnf_shm_ipc`: direction, shared-region pointer, counters, `waiting_for_ack`, callbacks, workqueue, and completion. Persistent peer-visible state is `flags`, `data_len`, and data bytes in the shared region. It depends on MMIO accessors, memory barriers, workqueues, completions, and transport-specific interrupt functions.

### Integration Points
Bus implementations use this as a low-level control/data path before higher QLINK command/event handling. RX callbacks usually wrap the shared data into skb/control packets.

### Risks
Only one outstanding TX is modeled; concurrent `qtnf_shm_ipc_send()` calls would race without external serialization. ACK completion can arrive after timeout, so `waiting_for_ack` ordering is important. Inbound data is passed as `__iomem` and must be copied safely by callbacks. Free completes waiters but does not flush queued work here.

### Test Signals
Exercise normal send/ACK, ACK timeout, inbound zero/oversized length rejection, repeated inbound drain while `NEW_DATA` remains set, teardown with a blocked sender, barrier-sensitive payload integrity, and interrupt callback ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/shm_ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/shm_ipc.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/shm_ipc.h

### Purpose
`shm_ipc.h` declares the qtnfmac shared-memory IPC object, callback contracts, direction enum, ACK timeout, and public send/init/free interface.

### Important APIs, Types, And Functions
Key types are `struct qtnf_shm_ipc_int`, `struct qtnf_shm_ipc_rx_callback`, `enum qtnf_shm_ipc_direction`, and `struct qtnf_shm_ipc`. The inline `qtnf_shm_ipc_irq_handler()` dispatches to the direction-specific handler installed by initialization.

### Control Flow
Callers allocate `struct qtnf_shm_ipc`, initialize it with a shared region, workqueue, interrupt callback, and RX callback, then call `qtnf_shm_ipc_irq_handler()` from hardware/bus IRQ handling. Outbound users call `qtnf_shm_ipc_send()` and inbound users receive data through the callback.

### State, Persistence, And Dependencies
The structure stores packet and timeout counters, a `waiting_for_ack` byte observed with `READ_ONCE`/`WRITE_ONCE` in the implementation, a work item, and completion. It depends on workqueue, completion, mutex/spinlock headers, and `shm_ipc_defs.h`.

### Integration Points
PCI or other bus transport code embeds this object for bidirectional host/firmware signaling, using separate inbound and outbound instances over shared MMIO regions.

### Risks
The header does not encode locking requirements for callers; external send serialization and teardown/workqueue flushing are part of integration discipline. Callback pointers are copied and assumed valid for the IPC lifetime.

### Test Signals
Compile-time coverage for both directions, IRQ dispatch before and after init, send serialization tests, callback lifetime teardown tests, and counter inspection under error paths are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/shm_ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/shm_ipc_defs.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/shm_ipc_defs.h

### Purpose
`shm_ipc_defs.h` defines the fixed shared-memory layout used by qtnfmac IPC peers.

### Important APIs, Types, And Functions
It sets `QTN_IPC_REG_HDR_SZ` to 32 bytes, `QTN_IPC_REG_SZ` to 4096 bytes, and `QTN_IPC_MAX_DATA_SZ` to the remaining payload capacity. It defines `QTNF_SHM_IPC_NEW_DATA` and `QTNF_SHM_IPC_ACK`, `struct qtnf_shm_ipc_region_header`, `union qtnf_shm_ipc_region_headroom`, and `struct qtnf_shm_ipc_region`.

### Control Flow
The implementation writes `data_len` and payload, then toggles `flags` between `NEW_DATA` and `ACK`. The 32-byte headroom ensures the payload begins at a fixed offset expected by both host and firmware.

### State, Persistence, And Dependencies
This header has no runtime state, but it defines the persistent shared-memory ABI. It depends only on Linux integer types and `BIT()`.

### Integration Points
`shm_ipc.c` validates this layout with `BUILD_BUG_ON()`. Bus code maps this structure over PCI/device shared memory, and firmware must use the same offsets and flag values.

### Risks
Changing sizes, packing, or flag meanings breaks host/firmware communication. `data_len` is 16-bit, which is sufficient for the 4064-byte payload but still requires validation before consuming inbound data.

### Test Signals
Build-time offset/size checks, firmware ABI tests, max payload transfer, invalid length injection, and flag transition tracing validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/shm_ipc_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/switchdev.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/switchdev.h

### Purpose
`switchdev.h` provides a tiny compatibility hook for marking received skbs as hardware-forwarded when qtnfmac is built with switchdev support.

### Important APIs, Types, And Functions
The only helper is `qtnfmac_switch_mark_skb_flooded(struct sk_buff *skb)`. With `CONFIG_NET_SWITCHDEV`, it sets `skb->offload_fwd_mark = 1`; otherwise it compiles to a no-op.

### Control Flow
Callers can unconditionally invoke the helper on frames flooded by hardware switch/bridge logic. The compile-time configuration decides whether the skb mark is actually set.

### State, Persistence, And Dependencies
There is no state. The helper mutates only the skb metadata for the current packet. It depends on `linux/skbuff.h` and, conditionally, kernel switchdev semantics.

### Integration Points
The helper integrates qtnfmac hardware bridge capabilities with the Linux bridge/switchdev path to avoid duplicate forwarding decisions.

### Risks
Incorrect marking could suppress needed software forwarding or cause duplicated traffic if omitted. Builds without switchdev intentionally lose the metadata signal.

### Test Signals
Bridge offload tests should verify the mark on flooded frames with switchdev enabled and no behavioral regression when compiled without `CONFIG_NET_SWITCHDEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/switchdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/trans.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/trans.c

### Purpose
`trans.c` implements qtnfmac's QLINK control transport coordination above the bus. It serializes synchronous command/response exchange, validates received control packet headers, delivers command responses to waiters, and queues asynchronous events for worker processing.

### Important APIs, Types, And Functions
Public functions are `qtnf_trans_send_cmd_with_resp()`, `qtnf_trans_init()`, `qtnf_trans_free()`, and exported `qtnf_trans_handle_rx_ctl_packet()`. Internal helpers are `qtnf_trans_signal_cmdresp()`, `qtnf_trans_event_enqueue()`, and `qtnf_trans_free_events()`.

### Control Flow
For a synchronous command, the current-command node sequence number is incremented under `resp_lock`, the sequence is written into the QLINK command header, waiting state is set, and the skb is sent through `qtnf_bus_control_tx()`. The sender waits up to five seconds for completion, then collects `resp_skb` and clears waiting state. RX handling first validates minimum header length and exact message length, then dispatches command responses to the current waiter or queues events to `event_queue` and schedules `event_work`.

### State, Persistence, And Dependencies
State lives in `bus->trans`: one `qtnf_cmd_ctl_node` with sequence, response skb, completion, lock, and waiting flag, plus an skb event queue with a max length. The file depends on qtnf bus control TX, QLINK headers, skb queues, workqueues, spinlocks, and completion APIs.

### Integration Points
The command layer uses this for request/response control operations. Bus RX paths pass all control packets into `qtnf_trans_handle_rx_ctl_packet()`. Event work later parses queued `struct qlink_event` messages.

### Risks
Only one synchronous command can be outstanding; callers must serialize command submission. Late or mismatched responses are dropped. Event queue overflow drops events. The response-size check for CMDRSP compares against `sizeof(struct qlink_cmd)` instead of `sizeof(struct qlink_resp)`, which is layout-equivalent here but semantically brittle.

### Test Signals
Test command success, timeout, interruptible wait, response sequence mismatch, unexpected response, malformed length, too-short event/response packets, event queue overflow, and teardown queue draining.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/trans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/trans.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/trans.h

### Purpose
`trans.h` declares qtnfmac QLINK transport state and public transport functions used by command, event, and bus layers.

### Important APIs, Types, And Functions
It defines command flags and buffer sizing constants, forward-declares `struct qtnf_bus`, and defines `struct qtnf_cmd_ctl_node` plus `struct qtnf_qlink_transport`. It declares `qtnf_trans_init()`, `qtnf_trans_free()`, `qtnf_trans_send_next_cmd()`, `qtnf_trans_handle_rx_ctl_packet()`, and `qtnf_trans_send_cmd_with_resp()`.

### Control Flow
The structures support one current command protected by `resp_lock` and a separate async event queue. Callers initialize transport state during bus bring-up, send commands through the synchronous API, and feed received control skbs into the RX handler.

### State, Persistence, And Dependencies
Transport state is memory-resident and per-bus. Persistent effects are not stored here; packets are passed to bus and event layers. Dependencies include kernel skbuff, module/kernel headers, mutex/spinlock facilities, and QLINK definitions.

### Integration Points
This header is included by qtnfmac command, event, and bus implementations. It is the contract between hardware-specific bus delivery and generic QLINK command/event handling.

### Risks
The declaration of `qtnf_trans_send_next_cmd()` has no implementation in this file subset, so users must rely on other compilation units or avoid it. Single-command state makes external serialization mandatory. Buffer-size constants need to match command builders and bus limits.

### Test Signals
Compile/link coverage for all declared functions, command serialization tests, event queue limit tests, and bus init/free ordering exercise this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/trans.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/util.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/util.c

### Purpose
`util.c` implements small qtnfmac utility routines for per-interface station list management and chip ID stringification.

### Important APIs, Types, And Functions
Station helpers are `qtnf_sta_list_init()`, `qtnf_sta_list_lookup()`, `qtnf_sta_list_lookup_index()`, `qtnf_sta_list_add()`, `qtnf_sta_list_del()`, and `qtnf_sta_list_free()`. `qtnf_chipid_to_string()` maps Topaz/Pearl chip IDs to readable names and is exported.

### Control Flow
The station list is initialized with an empty list head and zero atomic size. Lookup scans by MAC or by ordinal index. Add avoids duplicates, allocates a node, copies the MAC, appends to the list, increments size, and bumps `vif->generation`. Delete removes and frees a node while decrementing size and bumping generation. Free drains all nodes and reinitializes the list.

### State, Persistence, And Dependencies
State lives in `struct qtnf_sta_list` and `struct qtnf_vif` from `core.h`. There is no disk persistence. Dependencies include kernel list APIs, atomic counters, Ethernet address comparison/copy, allocator helpers, and hardware ID constants.

### Integration Points
AP/station event handling and station dump paths use the list to track associated peers. `generation` supports userspace-visible station list consistency across dumps. Chip stringification is used by PCI/probe logging or diagnostics.

### Risks
No locking is performed in these helpers; callers must hold the appropriate interface or event lock. The index lookup is linear and assumes the list is stable while traversed. Allocation failure returns `NULL` without changing state.

### Test Signals
Add/delete duplicate MACs, generation increments, free on nonempty list, index lookup bounds, null MAC handling, concurrent caller locking audits, and chip ID formatting tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/util.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/util.h

### Purpose
`util.h` declares qtnfmac station-list helpers and chip ID string conversion, plus inline size/empty accessors.

### Important APIs, Types, And Functions
It declares all station list operations implemented in `util.c` and `qtnf_chipid_to_string()`. Inline helpers are `qtnf_sta_list_size()` and `qtnf_sta_list_empty()`.

### Control Flow
Callers initialize a list, add/delete/lookup nodes through the declared functions, and query size or emptiness with lightweight inline reads. The header itself contains no complex flow.

### State, Persistence, And Dependencies
The header has no state but exposes operations on state defined by `core.h`. It depends on `linux/kernel.h` and qtnfmac core structures.

### Integration Points
Interface, event, station-info, and debug paths include this header to share station-list behavior without exposing implementation details in every file.

### Risks
The inline accessors do not lock; they are only as safe as caller synchronization. Including `core.h` makes this utility header coupled to central driver internals.

### Test Signals
Build coverage across all users, lockdep/KCSAN around list readers, and station lifecycle tests validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/Kconfig

### Purpose
`ralink/Kconfig` adds the top-level wireless vendor menu entry for Ralink devices and includes the rt2x00 family configuration.

### Important APIs, Types, And Functions
It defines `config WLAN_VENDOR_RALINK` as a bool defaulting to `y`, wraps subordinate options in `if WLAN_VENDOR_RALINK`, and sources `drivers/net/wireless/ralink/rt2x00/Kconfig`.

### Control Flow
During kernel configuration, disabling the vendor option hides all Ralink driver prompts. Enabling it makes the rt2x00 menu and driver options available.

### State, Persistence, And Dependencies
Configuration state is persisted in the kernel `.config`. This file depends on Kconfig menu processing and the sourced rt2x00 file.

### Integration Points
It is reached from the wireless drivers Kconfig tree and gates all Ralink build options under `drivers/net/wireless/ralink/`.

### Risks
The vendor option does not directly build code; confusion can arise if users expect it to enable a driver by itself. A wrong source path would hide all rt2x00 options.

### Test Signals
Run `make menuconfig` or `scripts/kconfig/conf` with the vendor option both enabled and disabled, and verify rt2x00 symbols appear only in the enabled case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/Makefile

### Purpose
`ralink/Makefile` connects the Ralink vendor directory to the kernel build by descending into `rt2x00/` when `CONFIG_RT2X00` is enabled.

### Important APIs, Types, And Functions
The only build rule is `obj-$(CONFIG_RT2X00) += rt2x00/`.

### Control Flow
Kbuild evaluates the config symbol and includes or skips the rt2x00 subdirectory accordingly.

### State, Persistence, And Dependencies
There is no runtime state. It depends on Kbuild and the `CONFIG_RT2X00` symbol defined in rt2x00 Kconfig.

### Integration Points
This is the build bridge between the generic wireless driver Makefile and all Ralink rt2x00 library/driver objects.

### Risks
If `CONFIG_RT2X00` is unset, no Ralink rt2x00 objects build even if lower symbols are somehow selected. The file intentionally has no per-driver granularity.

### Test Signals
Check `make drivers/net/wireless/ralink/` with `CONFIG_RT2X00=y/m/n` and inspect included object directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/Kconfig

### Purpose
`rt2x00/Kconfig` defines the Ralink rt2x00 driver family configuration, including PCI, USB, SoC drivers, shared libraries, firmware/crypto/debugfs/LED helpers, and chipset-family feature toggles.

### Important APIs, Types, And Functions
The main symbol is `RT2X00`, depending on `MAC80211 && HAS_DMA`. Driver symbols include `RT2400PCI`, `RT2500PCI`, `RT61PCI`, `RT2800PCI`, `RT2500USB`, `RT73USB`, `RT2800USB`, and `RT2800SOC`. Shared symbols include `RT2X00_LIB`, `RT2X00_LIB_MMIO`, `RT2X00_LIB_PCI`, `RT2X00_LIB_USB`, `RT2800_LIB`, `RT2800_LIB_MMIO`, `RT2X00_LIB_FIRMWARE`, `RT2X00_LIB_CRYPTO`, `RT2X00_LIB_LEDS`, `RT2X00_LIB_DEBUGFS`, and `RT2X00_DEBUG`.

### Control Flow
Selecting a concrete driver pulls in the required shared library and bus support with Kconfig `select`. More advanced RT2800 PCI/USB families expose nested bools for optional chipset support. Debugfs depends on mac80211 debugfs. LED support defaults on when the LED class is available and library/module linkage is compatible.

### State, Persistence, And Dependencies
Kernel `.config` stores all choices. Dependencies wire the family to mac80211, PCI/USB/OF/SOC availability, DMA capability, EEPROM 93cx6, firmware loader, and CRC libraries.

### Integration Points
These symbols drive the rt2x00 Makefile object selection and control conditional compilation in driver sources. Distribution kernel configs use this file to build individual Ralink modules.

### Risks
`select` bypasses dependency prompts, so shared-library symbols must remain dependency-safe. Experimental chipset toggles defaulting to `y` can expose less-tested hardware paths. Hidden helper symbols must match Makefile object names.

### Test Signals
Use `allmodconfig`, `randconfig`, PCI-only, USB-only, and no-LED/no-debugfs configs. Verify expected module names, selected helper libraries, and no unmet dependency warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/Makefile

### Purpose
`rt2x00/Makefile` maps rt2x00 Kconfig symbols to shared library objects and concrete Ralink driver modules.

### Important APIs, Types, And Functions
It builds `rt2x00lib-y` from core library objects and conditionally adds debugfs, crypto, firmware, and LED helpers. It maps symbols to objects such as `rt2x00lib.o`, `rt2x00mmio.o`, `rt2x00pci.o`, `rt2x00usb.o`, `rt2800lib.o`, `rt2800mmio.o`, `rt2400pci.o`, `rt2500pci.o`, `rt61pci.o`, `rt2800pci.o`, USB drivers, and `rt2800soc.o`.

### Control Flow
Kbuild combines the `rt2x00lib-y` components into the library object when `CONFIG_RT2X00_LIB` is enabled, and builds bus helpers or device drivers according to their config symbols.

### State, Persistence, And Dependencies
There is no runtime state. Build state follows `.config` and Kbuild's object graph. It depends on object files existing with names matching symbol intent.

### Integration Points
This file is the final build selection layer for the entire rt2x00 family, connecting Kconfig choices to modules used by PCI/USB/SoC probe paths.

### Risks
Missing object entries or symbol mismatches create link or missing-driver failures. Conditional helper objects must stay aligned with code guarded by corresponding `CONFIG_RT2X00_LIB_*` symbols.

### Test Signals
Module builds for each individual driver, combined allmodconfig builds, and link checks with debugfs/crypto/firmware/LED toggles validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2400pci.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2400pci.c

### Purpose
`rt2400pci.c` is the rt2x00 PCI/MMIO driver for Ralink RT2460/RT2400 PCI and PCMCIA wireless devices. It implements chip-specific register access, EEPROM probing, RF/BBP setup, queue and descriptor handling, interrupt tasklets, link tuning, mac80211 callbacks, and PCI module registration.

### Important APIs, Types, And Functions
Important routines include BBP/RF indirect access (`rt2400pci_bbp_read/write()`, `rt2400pci_rf_write()`), EEPROM bit-bang callbacks, LED/rfkill helpers, config handlers (`config_filter`, `config_intf`, `config_erp`, `config_ant`, `config_channel`, `config_ps`), queue handlers, register/BBP initialization, power-state switching, TX descriptor/beacon writing, RX status filling, TX done processing, interrupt/tasklet handlers, EEPROM validation/init, hardware mode probing, and `rt2400pci_probe()`.

### Control Flow
PCI probe delegates to `rt2x00pci_probe()` with `rt2400pci_ops`. Probe reads EEPROM, identifies RF2420/RF2421, sets antenna/rfkill/link-tuning capabilities, builds 2.4 GHz CCK-only channel specs, and marks DMA/ATIM/software-sequence requirements. Radio enable initializes DMA ring registers, core registers, and BBP defaults plus EEPROM overrides. Runtime mac80211 config calls write MAC/BSSID/beacon timing/channel/antenna/power/retry/PS state. Interrupts clear CSR7, schedule tasklets, mask active sources, and tasklets process TX/RX/beacon work before reenabling interrupts.

### State, Persistence, And Dependencies
Persistent device data comes from EEPROM and RF calibration tables. Runtime state lives in `struct rt2x00_dev`, DMA descriptors, skb frame descriptors, tasklets, queue entries, locks, and hardware registers. Dependencies include rt2x00 core/mmio/pci libraries, mac80211, eeprom_93cx6, PCI, LEDs, debugfs, and kernel DMA mapping.

### Integration Points
The file registers `ieee80211_ops`, `rt2x00lib_ops`, `rt2x00_ops`, and a PCI driver for vendor/device `1814:0101`. It uses shared rt2x00 queue, TX/RX, link, debugfs, and mac80211 glue.

### Risks
Hardware ownership bits and descriptor word0 ordering are race-sensitive. Indirect BBP/RF access can time out. IRQ masking/tasklet reenabling must avoid lost interrupts and teardown races. Several ARCSR writes use `ARCSR2_LENGTH` while programming ARCSR3-5 fields, which matches shared bit positions but is brittle. Single global CW handling rejects nonzero queue config.

### Test Signals
Probe/remove, EEPROM width detection, RF2420/RF2421 channel switch, DMA ring ownership, TX success/retry/failure statuses, RX timestamp wrap logic, rfkill GPIO, beacon enable/disable, suspend/resume power states, interrupt storms, and monitor/filter changes are high-value tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2400pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2400pci.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2400pci.h

### Purpose
`rt2400pci.h` defines the RT2460/RT2400 PCI hardware register map, EEPROM layout, RF/BBP constants, DMA descriptor bitfields, queue sizing constants, and TX power conversion macros used by `rt2400pci.c`.

### Important APIs, Types, And Functions
The header defines RF chip IDs (`RF2420`, `RF2421`), register base/size constants, CSR/TXCSR/RXCSR/ARCSR/PWR/BBP/RF/LED/GPIO fields, EEPROM offsets and field masks, TX/RX descriptor sizes and word field masks, and `TXPOWER_FROM_DEV()`/`TXPOWER_TO_DEV()` conversion macros.

### Control Flow
No executable flow exists, but all driver register manipulation uses these `FIELD32`, `FIELD16`, and `FIELD8` definitions through rt2x00 field helpers. Descriptor fields define when software or NIC owns entries, how packet lengths and PLCP values are set, and how RX status is decoded.

### State, Persistence, And Dependencies
The file models hardware and EEPROM persistent state. It depends on rt2x00 field macros being available before inclusion. EEPROM fields persist MAC address, antenna defaults, RF type, LED mode, tuning, radio button, BBP overrides, and TX power.

### Integration Points
`rt2400pci.c` uses these constants for every register, EEPROM, RF, BBP, descriptor, and power conversion operation. Debugfs also exposes register/eeprom/bbp/rf ranges from these values.

### Risks
Incorrect masks corrupt hardware programming. TX power conversion is reversed relative to other rt2x00 drivers, so misuse can increase or decrease power incorrectly. Descriptor field definitions must match DMA hardware exactly to avoid NIC/software ownership races.

### Test Signals
Register field encode/decode tests, descriptor dump validation against hardware docs, EEPROM parsing fixtures, TX power boundary tests, and debugfs range sanity checks are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2400pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2500pci.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2500pci.c

### Purpose
`rt2500pci.c` is the rt2x00 PCI/MMIO driver for Ralink RT2560/RT2500 PCI and PCMCIA wireless devices. It is structurally similar to rt2400pci but supports OFDM, more RF front ends, optional 5 GHz channels through RF5222, richer descriptor fields, and RT2560-specific tuning.

### Important APIs, Types, And Functions
Important routines include BBP/RF indirect access, EEPROM bit-bang callbacks, rfkill/LED helpers, configuration handlers, RF channel programming with TX power, dynamic link tuning, queue and descriptor operations, register/BBP initialization, power-state switching, interrupt/tasklet handling, EEPROM validation with default repair, RF table selection, hardware-mode probing, and PCI/module registration.

### Control Flow
Probe delegates to `rt2x00pci_probe()` with `rt2500pci_ops`. EEPROM is read and missing antenna/NIC/calibration words are synthesized. RF type is validated among RF2522/2523/2524/2525/2525E/5222, capabilities are set, RSSI offset is read, and channel tables are selected. Radio enable programs queues, MAC/PCI/BBP/autoresponder registers, then BBP defaults and EEPROM overrides. Channel changes program RF registers with RF-specific tuning sequences, channel-14 filter, optional RF4, and TX power. Interrupts clear CSR7, schedule tasklets, mask sources, and tasklets drain TX/RX/beacon work.

### State, Persistence, And Dependencies
Runtime state is in rt2x00 core structures, DMA descriptors, skb metadata, locks, tasklets, and hardware registers. Persistent device configuration is EEPROM plus static RF channel tables. Dependencies are rt2x00 core/mmio/pci, mac80211, eeprom_93cx6, PCI, LEDs, debugfs, and DMA APIs.

### Integration Points
The file registers `ieee80211_ops`, `rt2x00lib_ops`, `rt2x00_ops`, and a PCI driver for `1814:0201`. It uses shared rt2x00 mac80211 callbacks for most operations and supplies chip-specific callbacks for hardware handling.

### Risks
The driver has many RF-specific branches and revision-specific link tuning, so regressions can be hardware-specific. Descriptor word0 ownership ordering is race-sensitive. EEPROM default repair may hide bad hardware data. Probe reads RSSI offset but `rt2500pci_probe_hw()` later sets `rssi_offset = DEFAULT_RSSI_OFFSET`, which may override calibration and is worth checking against intended behavior. The RF5222 channel table has unusual channel ordering around 52/66/60/64 that should match hardware expectations.

### Test Signals
Probe/remove across RF variants, EEPROM fallback fixtures, 2.4/5 GHz channel switching, TX power changes without channel changes, OFDM/CCK RX signal interpretation, dynamic CCA/R17 tuning, rfkill delayed behavior, DMA descriptor ownership, interrupt masking, beacon reload, and suspend/resume are key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2500pci.c -->
