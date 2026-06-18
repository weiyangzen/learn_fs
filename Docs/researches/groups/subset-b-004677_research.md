# subset-b-004677 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc_drv.c -->
# sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc_drv.c

Purpose: Implements the Linux `hv_netvsc` net_device front end for Microsoft Hyper-V synthetic Ethernet. It binds the VMBus network GUID, creates and registers the guest Ethernet device, exposes netdev and ethtool operations, builds RNDIS/NVSP transmit packets, receives packets from the lower Hyper-V channel code, manages link-change work, supports XDP, RSS/ring/channel tuning, and coordinates accelerated networking failover to a matching PCI VF.

Important APIs, types, and functions: Module parameters `ring_size` and `debug` configure VMBus ring sizing and netif message level. `netvsc_open()`/`netvsc_close()` wrap `rndis_filter_open()` and `rndis_filter_close()` plus VF open/close. `netvsc_xmit()` is the central TX path; it chooses VF versus synthetic path, linearizes overly scattered SKBs, constructs a `struct rndis_message`, adds PPI blocks for hash, VLAN, LSO, and checksum offload, maps page buffers, and calls `netvsc_send()`. RX enters through `netvsc_recv_callback()`, runs XDP via `netvsc_run_xdp()`, allocates an SKB from RSC data, applies checksum/hash/VLAN metadata, updates stats, and calls GRO. Reconfiguration helpers `netvsc_detach()` and `netvsc_attach()` are used by ethtool channel/ring changes, MTU changes, suspend, and resume. Ettool operations expose stats, RSS hash fields/key/indirection table, register dump of the transmit table, channel count, ring sections, features, and link settings. VF support is driven by `netvsc_netdev_event()`, `netvsc_register_vf()`, `netvsc_unregister_vf()`, `netvsc_vf_changed()`, and RX handler `netvsc_vf_handle_frame()`.

Control flow: Module init clamps `ring_size`, computes `netvsc_ring_bytes`, registers a netdevice notifier, then registers the VMBus driver. Probe allocates a multi-queue Ethernet device, initializes private context/work/completions/stats, calls `rndis_filter_device_add()` under RTNL, copies the host-provided MAC, schedules subchannel setup if needed, configures features/MTU/XDP capabilities, registers the netdev, tracks it in `netvsc_dev_list`, and opportunistically joins an already-present VF. Open enables RNDIS packet filters, carrier, queues, and VF. TX first diverts to an up VF when `data_path_is_vf` is set, otherwise emits a synthetic RNDIS packet on a selected channel. RX is called after RNDIS parsing has populated per-channel RSC fields. Link indications enqueue `struct netvsc_reconfig` entries and delayed work throttles carrier transitions and peer notifications. Remove and suspend cancel work, detach XDP/VF/RNDIS state, unregister the netdev, and free per-CPU stats.

State and persistence behavior: There is no durable storage. Persistent runtime state is per-netdev `struct net_device_context`: the VMBus device pointer, RCU `nvdev`, optional RCU `vf_netdev`, message level, RSS TX/RX indirection tables, speed/duplex, feature masks, delayed work, reconfiguration event list, VF completions, VF statistics, and saved device info across suspend. Per-channel TX/RX statistics and RSC state live in `struct netvsc_device`. Carrier, queue state, VF data-path state, and BPF/XDP program references are rebuilt on attach/probe and released on detach/remove.

Dependencies and integration points: This file integrates Linux netdev, ethtool, rtnetlink, notifier, NAPI/GRO, XDP/BPF, per-CPU statistics, PCI VF devices, VMBus `hv_driver`, and the lower Hyper-V/RNDIS helpers in `hyperv_net.h`, `rndis_filter.c`, and netvsc channel code. It relies on Hyper-V NVSP/RNDIS constants for PPI layout and on host messages for MAC, MTU, RSS, offloads, link state, and VF association.

Risks and edge cases: The highest-risk areas are race-prone lifetime boundaries: RTNL versus VMBus subchannel creation, RCU access to `nvdev`/`vf_netdev`, notifier replay during probe, namespace moves for VFs, and detach/attach rollback on MTU/channel/ring changes. TX page-buffer accounting must stay within `MAX_PAGE_BUFFER_COUNT` and correctly handle VLAN header popping, GSO checksum preparation, and unsupported partial checksums. Link-change work intentionally throttles events, so repeated RNDIS indications can be delayed. VF switching depends on host VF association completion and matching by PCI slot serial or MAC fallback. XDP and LRO are mutually constrained. Suspend/resume must restore saved channels, rings, RSS key, and XDP program without leaking references.

Test signals: Build with `CONFIG_HYPERV_NET`, XDP, netpoll, and SR-IOV capable paths. Runtime tests should cover probe/remove, module reload with a pre-existing VF, open/close and carrier transitions, synthetic TX/RX, VLAN TX/RX, GSO/TSO/TSO6, checksum fallback, high-fragment SKBs, XDP PASS/DROP/TX/REDIRECT/NDO_XMIT, ethtool channel/ring/RSS changes with rollback, MTU changes with VF rollback, VF register/unregister/up/down/change, namespace movement, suspend/resume, RNDIS network-change throttling, subchannel failures, and stats consistency across synthetic and VF paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc_trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc_trace.c

Purpose: Provides the single tracepoint-definition translation unit for the Hyper-V netvsc trace events. It includes `hyperv_net.h`, defines `CREATE_TRACE_POINTS`, and then includes `netvsc_trace.h` so the tracepoint declarations in the header emit storage and registration code exactly once.

Important APIs, types, and functions: There are no runtime functions in this file. Its key API is the Linux tracepoint pattern `#define CREATE_TRACE_POINTS` before including a trace header that ends with `<trace/define_trace.h>`. The resulting trace events are `rndis_send`, `rndis_recv`, `nvsp_send`, `nvsp_send_pkt`, and `nvsp_recv`, all declared in `netvsc_trace.h`.

Control flow: The build compiles this source into the netvsc module. At compile time, the trace macros expand into tracepoint descriptors and helper functions. At runtime, call sites in the RNDIS/NVSP code invoke the generated tracepoint hooks; if tracing is disabled, static keys keep overhead low.

State and persistence behavior: The file owns no driver state and no durable data. Tracepoint registration metadata lives in kernel/module text and data while the module is loaded. Captured trace records are transient ftrace/perf/ring-buffer data managed by the tracing subsystem.

Dependencies and integration points: It depends on `linux/netdevice.h`, `hyperv_net.h`, and the trace definitions in `netvsc_trace.h`. Integration is with Linux ftrace/perf and any netvsc code calling `trace_*()` helpers generated from the header.

Risks and edge cases: The file must remain the only translation unit defining `CREATE_TRACE_POINTS` for this trace header; duplicating it would create linker conflicts, while omitting it would leave tracepoint references unresolved. Include paths in the trace header must match the source tree location.

Test signals: Build the Hyper-V netvsc driver with tracing enabled, verify the module links, and confirm trace events appear under the `netvsc` trace system. Runtime smoke tests should enable `netvsc:rndis_send`, `netvsc:rndis_recv`, and `netvsc:nvsp_*` events while opening the interface and sending traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc_trace.h

Purpose: Declares ftrace trace events for Hyper-V netvsc RNDIS and NVSP control/data messages. It gives operators symbolic visibility into RNDIS request/response types, NVSP message types, packet queue IDs, and send-buffer section use without adding ad hoc logging to hot paths.

Important APIs, types, and functions: `TRACE_SYSTEM netvsc` names the trace namespace. `TRACE_DEFINE_ENUM()` exports RNDIS and NVSP constants so traces can print stable symbolic values. `show_rndis_type()` and `show_nvsp_type()` map message numeric types to readable labels. `DECLARE_EVENT_CLASS(rndis_msg_class)` defines common fields for RNDIS send/receive events: netdev name, queue, request ID, message type, and length. `DEFINE_EVENT()` instantiates `rndis_send` and `rndis_recv`. `TRACE_EVENT(nvsp_send)`, `TRACE_EVENT(nvsp_send_pkt)`, and `TRACE_EVENT(nvsp_recv)` record NVSP message types, subchannel IDs, channel type, and send-buffer section metadata.

Control flow: Driver call sites pass `struct net_device`, optional `struct vmbus_channel`, and RNDIS/NVSP message pointers to generated `trace_*` helpers. The trace fast-assign blocks snapshot the device name and selected header fields into the tracing ring buffer, and `TP_printk` formats them for userspace tracing tools.

State and persistence behavior: The header does not own device state. Trace records persist only as long as the tracing backend retains them. The generated event format is a user-visible diagnostic ABI, so field names and meanings should be treated conservatively.

Dependencies and integration points: It depends on Linux tracepoint infrastructure and on `hyperv_net.h` types such as `struct rndis_message`, `struct nvsp_message`, `struct nvsp_1_message_send_rndis_packet`, and `struct vmbus_channel`. `TRACE_INCLUDE_PATH ../../drivers/net/hyperv` directs `<trace/define_trace.h>` to this header when compiled from the generated trace file context.

Risks and edge cases: The RNDIS event class reads `msg->msg.init_req.req_id` for all RNDIS messages, relying on request ID placement being common across request/response shapes; packet or indication messages may print a field that is meaningful only for control messages. Trace fast-assign code must not dereference invalid message buffers, so call sites must validate or only trace trusted in-kernel constructed messages. Symbol tables need updates when new NVSP/RNDIS message types are added.

Test signals: Build-test with `CREATE_TRACE_POINTS` in `netvsc_trace.c`; enable each trace event through tracefs; exercise RNDIS init/query/set, NVSP init/subchannel/RSS, and packet send paths; verify event format files expose the expected fields and symbolic names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/rndis_filter.c -->
# sources/distributed-fs/ceph-client/drivers/net/hyperv/rndis_filter.c

Purpose: Implements the RNDIS protocol layer for Hyper-V netvsc. It allocates and tracks RNDIS control requests, sends them through the lower netvsc/NVSP channel, receives and validates RNDIS packet/control/indication messages, negotiates MAC/MTU/link/offload/RSS capabilities, manages packet filters for open/close and multicast updates, and sets up multi-channel RSS subchannels.

Important APIs, types, and functions: `struct rndis_request` packages a list node, completion, response/request messages, extension buffers, and an inline `hv_netvsc_packet`. `get_rndis_device()`, `get_rndis_request()`, and `put_rndis_request()` manage RNDIS state and in-flight request list. `rndis_filter_send_request()` emits control messages via `netvsc_send()` and traces them. RX entry `rndis_filter_receive()` dispatches RNDIS packet data, control completions, and indications. `rndis_get_ppi()` parses validated per-packet-info blocks. `rndis_filter_receive_data()` handles VLAN/checksum/hash PPI, RSC suballocation fragments, and calls `netvsc_recv_callback()`. Control helpers include `rndis_filter_query_device()`, `rndis_filter_set_device_mac()`, `rndis_filter_set_offload_params()`, `rndis_filter_set_rss_param()`, `rndis_filter_set_packet_filter()`, `rndis_filter_init_device()`, `rndis_filter_halt_device()`, `rndis_filter_open()`/`close()`, `rndis_set_subchannel()`, and `rndis_filter_device_add()`/`remove()`.

Control flow: Device add first calls lower `netvsc_device_add()`, links a newly allocated `rndis_device` as `net_device->extension`, sends RNDIS initialize, queries host MTU and permanent MAC, optionally applies friendly name, queries offload capabilities, sets desired offload parameters, queries link status/speed, then negotiates RSS and prepares subchannels for NVSP v5+. Opening sets the directed/broadcast/multicast packet filter and transitions to `RNDIS_DEV_DATAINITIALIZED`; closing cancels multicast work and clears the filter. Receive first copies and validates the RNDIS header into the channel receive buffer; packet messages are bounds-checked, PPI data is copied and parsed, RSC fragments are accumulated in per-channel state, and completed packets flow to the netdev RX callback. Control completions are matched by request ID under `request_lock`, copied into the waiting request, DMA-unmapped, and completed.

State and persistence behavior: Runtime state lives in `struct rndis_device`: RNDIS state enum, request ID counter, request list/lock, multicast work, current filter, link state, hardware MAC, RSS key, and `ndev` pointer. Per-channel RSC state stores fragments, packet length, VLAN/checksum/hash metadata, and fragment count only until a coalesced packet is delivered or dropped. RSS indirection state is stored in `struct net_device_context` and host state is updated via RNDIS OIDs. No state persists across driver unload; probe rebuilds it from host queries.

Dependencies and integration points: This file integrates with `hyperv_net.h` structures, `netvsc_send()`, `netvsc_recv_callback()`, lower `netvsc_device_add/remove()`, VMBus packet APIs, Linux netdev features, Unicode conversion for host configuration names, RNDIS OIDs, NDIS offload/RSS structures, and trace events from `netvsc_trace.h`.

Risks and edge cases: Buffer and offset validation is critical because RNDIS data comes from the host; malformed `msg_len`, PPI offsets, info lengths, RSC fragment markers, and response sizes can otherwise corrupt channel buffers or request storage. Control requests wait without explicit timeout, so host non-response can hang callers on paths that expect synchronous completion. `rndis_filter_set_packet_filter()` updates `dev->filter` after any successful send path rather than checking completion status in detail. Halt sets `destroy` and waits for all channel send completions, so queue drain accounting must be correct. RSS/subchannel setup must tolerate host allocating fewer channels than requested and must not expose queue counts before NAPI/channel state is ready.

Test signals: Exercise RNDIS init/query/set/halt, open/close packet filters, multicast/promiscuous/allmulti updates, MAC address changes, friendly-name query, link status/speed updates, offload negotiation across NVSP versions 1-5, RSS key and indirection changes, subchannel allocation failures and reduced counts, malformed RNDIS/PPI/RSC packet injection, RSC first/middle/last fragment sequences, receive checksum/hash/VLAN metadata, and teardown while control requests or sends are outstanding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/rndis_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/Kconfig

Purpose: Defines the kernel configuration menu for IEEE 802.15.4 low-rate wireless personal area network drivers. It groups fake, SPI, USB, and simulator transceiver drivers under `IEEE802154_DRIVERS` and encodes their bus and stack dependencies.

Important APIs, types, and symbols: `menuconfig IEEE802154_DRIVERS` depends on `NETDEVICES && IEEE802154` and defaults to `y` while adding no code by itself. Driver symbols include `IEEE802154_FAKELB`, `IEEE802154_AT86RF230`, `IEEE802154_MRF24J40`, `IEEE802154_CC2520`, `IEEE802154_ATUSB`, `IEEE802154_ADF7242`, `IEEE802154_CA8210`, `IEEE802154_CA8210_DEBUGFS`, `IEEE802154_MCR20A`, and `IEEE802154_HWSIM`. Several SPI drivers select or depend on `REGMAP_SPI`; USB and debugfs options depend on `USB` and `DEBUG_FS`.

Control flow: Kconfig evaluation determines which object files the companion Makefile includes. Enabling the parent menu makes child choices visible; selecting a child as built-in or module controls whether the related driver is linked into the kernel image or built as a loadable module.

State and persistence behavior: The only persistent state is kernel build configuration in `.config` and generated autoconf headers. Runtime driver state is not present here.

Dependencies and integration points: The symbols integrate with the network device subsystem, `IEEE802154`, `MAC802154`, SPI, USB, common clock support, debugfs, regmap, and the Makefile in the same directory. Help text documents module names expected by users and packaging.

Risks and edge cases: Incorrect dependencies can create build failures or expose drivers without required bus/mac802154 support. `IEEE802154_DRIVERS` defaults to `y`, so new child defaults should be conservative. Debugfs must remain gated by both the CA8210 driver and `DEBUG_FS`.

Test signals: Run Kconfig builds for allnoconfig/menuconfig visibility, each driver as `m`, combinations without SPI/USB/MAC802154, and randconfig coverage to catch missing selects or unmet dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/Makefile

Purpose: Maps IEEE 802.15.4 Kconfig symbols to the object files compiled for each driver in this directory.

Important APIs, types, and symbols: Standard kernel build variables `obj-$(CONFIG_...) += ...` include `fakelb.o`, `at86rf230.o`, `mrf24j40.o`, `cc2520.o`, `atusb.o`, `adf7242.o`, `ca8210.o`, `mcr20a.o`, and `mac802154_hwsim.o` based on configuration.

Control flow: During kbuild, each enabled symbol contributes the corresponding object as built-in or module according to the symbol value. Module names follow object basenames unless additional composite object rules are added elsewhere.

State and persistence behavior: This file has no runtime state. Its output is build artifacts and modules determined by `.config`.

Dependencies and integration points: It must stay synchronized with `Kconfig` symbols and source filenames in `drivers/net/ieee802154`. It integrates with the Linux kernel recursive make system.

Risks and edge cases: A mismatch between Kconfig symbol, source filename, or Makefile object entry silently prevents an enabled driver from building or causes build errors. Composite drivers would require additional `foo-y` rules not present here.

Test signals: Build each `CONFIG_IEEE802154_*` option as module and built-in, and run `make M=drivers/net/ieee802154` or equivalent subtree builds to verify object mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/adf7242.c -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/adf7242.c

Purpose: Implements the SPI mac802154 driver for Analog Devices ADF7242/ADF7241 IEEE 802.15.4 transceivers. It uploads required addon firmware, programs radio-controller and packet/filter registers, exposes mac802154 operations, handles IRQ-driven RX/TX completion, and provides debugfs status.

Important APIs, types, and functions: `struct adf7242_local` holds the SPI device, `ieee802154_hw`, TX completion, SPI mutex, prebuilt status SPI message, debugfs root, RX recalibration delayed work/workqueue, flags, TX status, promiscuous state, RSSI, CSMA/retry parameters, and cacheline-aligned SPI buffers. Low-level helpers `adf7242_status()`, `adf7242_wait_status()`, `adf7242_read_reg()`, `adf7242_write_reg()`, `adf7242_read_fbuf()`, `adf7242_write_fbuf()`, and `adf7242_cmd()` serialize SPI access and radio-controller commands. Firmware helpers upload/verify `adf7242_firmware.bin`. mac802154 ops include synchronous transmit, start/stop, channel, address filter, promiscuous mode, CSMA params, frame retries, TX power, CCA ED level, and ED readout. `adf7242_isr()` handles RX packet and CSMA/TX IRQs.

Control flow: Probe requires an IRQ, allocates `ieee802154_hw`, initializes supported 2.4 GHz channels and PHY capability tables, creates an ordered workqueue, resets the chip, requests firmware, uploads PRAM pages, configures frame filtering, auto ACK, packet addon mode, PA/RXFE, and IRQ masks, requests a threaded IRQ, disables it until start, registers the hw, and creates debugfs. Start moves to PHY ready, clears interrupts, enables the IRQ, sets `FLAG_START`, and enters RX. TX disables IRQs, marks `FLAG_XMIT`, cancels RX calibration, writes the frame buffer, commands CSMA-CA transmit, waits up to `HZ/10` for IRQ completion, checks `tx_stat`, clears transmit state, and returns to RX. RX IRQ reads frame length and buffer, extracts LQI/RSSI trailer bytes, trims CRC/RSSI/LQI, and delivers through `ieee802154_rx_irqsafe()`.

State and persistence behavior: Runtime radio state is held in ADF7242 registers/PRAM and `adf7242_local` fields. `FLAG_START` and `FLAG_XMIT` gate interrupt behavior and periodic recalibration. `promiscuous`, CSMA params, frame retry count, RSSI, and TX completion status are kept in RAM and re-applied after soft reset. Firmware is requested from the kernel firmware loader at probe and not persisted by the driver.

Dependencies and integration points: The driver depends on SPI, threaded IRQs, firmware loader, workqueues, debugfs, `ieee802154_hw`, mac802154/cfg802154 APIs, and device-tree/SPI IDs `adi,adf7242` and `adi,adf7241`. It integrates with userspace through nl802154/mac802154 operations and debugfs `status`.

Risks and edge cases: Probe fails without firmware, an IRQ, or successful radio-controller status polling. SPI buffers are shared and protected by `bmux`; new call paths must not bypass locking. `adf7242_upload_firmware()` page loop and DEBUG-only verification are sensitive to firmware length boundaries. ISR behavior differs for TX versus RX and must re-enable RX after invalid interrupts. Soft reset disables IRQs when started and must restore filter, CSMA, promiscuous, packet config, and RX state. The driver reports CSMA status as success unless `ADF7242_REPORT_CSMA_CA_STAT` is enabled, limiting error visibility.

Test signals: Build as module and built-in, probe with and without firmware, validate IRQ trigger defaults, start/stop repeatedly, transmit success/timeout/no-IRQ paths, receive valid and corrupt PSDU lengths, channel 11-26 programming, TX power range, CCA ED level, CSMA/retry validation, promiscuous/address filter/PAN coordinator changes, soft reset recovery after status timeout, debugfs status reads, and remove while delayed work or IRQ activity is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/adf7242.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/at86rf230.c -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/at86rf230.c

Purpose: Implements the SPI mac802154 driver for Atmel/Microchip AT86RF231, AT86RF233, and AT86RF212 transceivers. It detects chip variants, configures radio timings and PHY capabilities, manages sleep/reset GPIOs, uses regmap for register access, and drives asynchronous TX/RX through a SPI state-machine around the transceiver states.

Important APIs, types, and functions: `struct at86rf2xx_chip_data` holds timing constants, RSSI base, and variant-specific channel/TX power callbacks. `struct at86rf230_state_change` is the reusable async SPI state-machine context with hrtimer, SPI message/transfer, buffers, completion callback, state tracking, TRAC result, and ownership flag. `struct at86rf230_local` stores SPI, `ieee802154_hw`, chip data, regmap, sleep GPIO, state completion, calibration deadline, TX state, TX SKB, and async TX context. Register helpers use `__at86rf230_read/write()` and subreg wrappers that wake/sleep the chip as needed. `at86rf230_async_state_change()` and related callbacks implement timed transceiver state transitions. mac802154 ops provide async transmit, ED stub, start/stop, channel, address filter, TX power, LBT, CCA mode/ED threshold, CSMA params, frame retries, and promiscuous mode.

Control flow: Probe parses optional `xtal-trim`, obtains reset and sleep GPIOs, hardware-resets the chip, allocates hw, initializes regmap and state contexts, detects manufacturer/part/version, initializes completion and chip registers, clears IRQ status, requests the IRQ, disables IRQ until start, sleeps the chip, and registers mac802154. Start wakes the chip, enables IRQ, and synchronously enters `STATE_RX_AACK_ON`. TX stores the SKB, optionally recalibrates by transitioning through `STATE_TRX_OFF`, moves to TX states, writes the frame buffer, triggers transmit via SLP_TR pulse or `STATE_BUSY_TX`, and later IRQ completion reads TRAC status and reports success or mapped mac802154 errors before returning to RX_AACK_ON. RX IRQ reads IRQ status, then frame buffer, validates PSDU length, extracts LQI, and delivers the SKB.

State and persistence behavior: Driver state is volatile and split between chip registers, regmap cache, GPIO sleep state, async state contexts, calibration timeout, and current TX SKB. Stop forces TRX_OFF, disables IRQ, refreshes random CSMA seed registers, and sleeps the transceiver. No durable state exists; probe redetects and reinitializes the device.

Dependencies and integration points: Depends on SPI, regmap SPI, GPIO descriptors, hrtimers, IRQs, device properties, random bytes, and mac802154/cfg802154. Device IDs and OF compatibles cover `atmel,at86rf230`, `atmel,at86rf231`, `atmel,at86rf233`, and `atmel,at86rf212`, but part 2 AT86RF230 is detected and reported unsupported.

Risks and edge cases: Asynchronous state transitions are timing-sensitive; wrong chip timing constants can break TX/RX. IRQ status is marked precious in regmap because reading clears it. BUSY_RX_AACK races are explicitly handled with retries and forced transitions; altering this may reintroduce stuck TX. Sleep-aware register access toggles GPIO around regmap calls and can affect cache assumptions. TX error recovery must not leak dynamically allocated IRQ contexts or lose the TX SKB. `at86rf230_ed()` returns a fixed dummy value, so energy-detect behavior is incomplete. Probe detection and reset GPIO polarity/timing must match board wiring.

Test signals: Build with `REGMAP_SPI`; probe each supported part and reject unsupported/non-Atmel IDs; test optional reset/sleep GPIOs and `xtal-trim`; start/stop sleep transitions; TX success, no-ACK, channel-access-failure, and async SPI error recovery; RX valid/corrupt frames; IRQ polarity variants; channel/page changes for 2.4 GHz and AT86RF212 sub-GHz modes; CCA mode/threshold, LBT, TX power tables, CSMA/retry programming, address filters, promiscuous mode, calibration after five minutes, and remove after IRQ masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/at86rf230.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/at86rf230.h -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/at86rf230.h

Purpose: Defines the AT86RF2xx transceiver register map, subregister masks, SPI command bits, IRQ bits, radio states, and TRAC transmit-result codes shared by the SPI AT86RF230-family driver and the USB ATUSB driver.

Important APIs, types, and constants: `RG_*` constants name registers from transceiver status/control through PHY RSSI/ED/channel, IRQ mask/status, voltage/battery/oscillator, address/PAN filters, and CSMA settings. `SR_*` triples encode `(register, mask, shift)` for subregister helpers. `CMD_REG`, `CMD_WRITE`, and `CMD_FB` encode SPI register/frame-buffer commands. IRQ constants describe PLL, RX, TX, CCA/ED, address match, under-run, and battery-low interrupts. State constants such as `STATE_TRX_OFF`, `STATE_RX_AACK_ON`, `STATE_TX_ARET_ON`, `STATE_BUSY_RX_AACK`, and `STATE_TRANSITION_IN_PROGRESS` mirror hardware state values. `TRAC_MASK()` and `TRAC_*` values decode TX completion status.

Control flow: Implementation files pass `SR_*` triples to subregister read/write helpers and compare hardware status against `STATE_*` and `TRAC_*` values during state changes, TX completion, RX mode entry, CCA, and error recovery. Frame-buffer command bits are used for asynchronous SPI buffer reads/writes.

State and persistence behavior: The header has no runtime state; it documents volatile hardware state. Values written through these constants persist only in transceiver registers while powered or until reset/sleep behavior changes them.

Dependencies and integration points: Used by `at86rf230.c` and `atusb.c`; depends on `BIT()` availability from kernel headers included by users. The constants must match the AT86RF230/231/233/212 datasheets and firmware command expectations for ATUSB.

Risks and edge cases: Incorrect masks/shifts silently corrupt adjacent hardware fields. Some constants are variant-specific, such as `SR_TX_PWR_23X` versus `SR_TX_PWR_212` and sub-GHz modulation bits. IRQ status reads can have side effects in the implementation. Shared use by USB firmware-facing code means changes must remain synchronized with device protocols.

Test signals: Compile both AT86RF230 SPI and ATUSB drivers, exercise all subregister helper paths, validate register writes with hardware or SPI/USB traces, and test TX TRAC decoding, IRQ mask/status, channel/TX power, address filters, CCA, and state transitions on each chip variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/at86rf230.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/atusb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/atusb.c

Purpose: Implements the USB mac802154 driver for the ATUSB 802.15.4 dongle and related firmware/hardware variants, including RZUSB and HULUSB. It communicates with device firmware using vendor control requests and bulk RX URBs, configures the attached AT86RF2xx transceiver, and exposes asynchronous TX/RX and PHY controls to mac802154.

Important APIs, types, and functions: `struct atusb` holds `ieee802154_hw`, USB device, variant data, shutdown/error state, delayed work, idle/RX URB anchors, TX control request/URB/SKB, ACK sequence, and firmware version/hardware type. `struct atusb_chip_data` provides variant channel/TX power callbacks. Control helpers `atusb_write_subreg()` and `atusb_read_subreg()` access transceiver registers through firmware requests. RX uses `atusb_alloc_urbs()`, `atusb_submit_rx_urb()`, `atusb_work_urbs()`, `atusb_in()`, and `atusb_in_good()`. TX uses `atusb_xmit()` and firmware completion packets handled by `atusb_tx_done()`. mac802154 ops cover async transmit, ED stub, start/stop RX mode, address filters, TX power, LBT, CCA mode/ED threshold, CSMA params, frame retries, promiscuous mode, and channel setting. Probe helpers read firmware ID/build, detect transceiver, and fetch EEPROM EUI-64.

Control flow: USB probe allocates hw/private state, anchors RX URBs, allocates a TX URB, resets the RF chip, detects/configures the transceiver and firmware variant, sets an extended address, enables frame retry capability for firmware >= 0.3, registers mac802154, forces TRX_OFF, and enables all transceiver IRQs via firmware. Start schedules RX URB submission work and sends `ATUSB_RX_MODE` on. Bulk IN completions either report TX completion packets of length 1 or 2, or parse received frames with PHR length and LQI then deliver SKBs. TX sends `ATUSB_TX` as a control URB with an incrementing ACK sequence and waits for firmware to report completion via the RX path. Disconnect sets shutdown, cancels work, kills anchored URBs and TX URB, unregisters hw, and frees state.

State and persistence behavior: Runtime state includes firmware version/hardware type, current TX SKB and ACK sequence, URBs anchored as idle or active RX, delayed allocation work, and error latch `err`. Permanent EUI-64 may be read from device EEPROM via firmware; if unavailable or invalid, a random extended address is generated for the runtime hw instance. No driver-side durable state is written.

Dependencies and integration points: Depends on USB core, vendor request protocol in `atusb.h`, AT86RF register constants in `at86rf230.h`, mac802154/cfg802154, SKBs, and kernel delayed work/USB anchors. It binds USB vendor/product `0x20b7:0x1540` with vendor-specific interface class.

Risks and edge cases: RX and TX completion share the bulk IN stream, so sequence mismatches can report hardware TX errors. URB allocation failures are retried via delayed work; shutdown must prevent resubmission. Some USB control-message return values are latched through `atusb->err`, while many configuration writes proceed sequentially before checking the latch. Firmware version gates EUI-64 and frame-retry support, and unknown hardware types fail probe. `atusb_stop()` kills idle URBs but active RX URBs are killed during disconnect; start/stop races depend on anchors and shutdown. ED is a fixed dummy value. HULUSB sub-GHz channel/page handling updates supported ED levels dynamically and must match AT86RF212 semantics.

Test signals: Probe supported firmware hardware types and reject unknown types; test old firmware without EUI64 read and newer firmware with valid/invalid EEPROM addresses; RX valid frames, corrupt lengths, zero-length URBs, and URB errors; TX success, no-ACK, channel-access-failure, sequence mismatch, and control URB submission failure; start/stop/disconnect under traffic; channel/TX power/CCA/LBT/CSMA/retry/promiscuous/address-filter operations; and URB allocation failure retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/atusb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/atusb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/atusb.h

Purpose: Defines the vendor/product IDs and USB vendor request protocol shared by the Linux ATUSB driver and ATUSB firmware. It is intended to remain identical between kernel and firmware source trees.

Important APIs, types, and constants: `ATUSB_VENDOR_ID` and `ATUSB_PRODUCT_ID` identify Qi Hardware ATUSB devices. `ATUSB_BUILD_SIZE` bounds firmware build-string reads. `enum atusb_requests` assigns request IDs for system status (`ATUSB_ID`, `ATUSB_BUILD`, `ATUSB_RESET`), debug/test/RF control (`ATUSB_RF_RESET`, `ATUSB_POLL_INT`, `ATUSB_TIMER`, GPIO, SLP_TR), transceiver register/buffer/SRAM access, raw SPI helpers, HardMAC RX/TX (`ATUSB_RX_MODE`, `ATUSB_TX`), and EEPROM EUI-64 read/write. Hardware type enum values distinguish ATUSB board revisions, RZUSB, and HULUSB. `ATUSB_REQ_FROM_DEV` and `ATUSB_REQ_TO_DEV` encode USB vendor control request direction.

Control flow: `atusb.c` sends these requests through USB control messages during probe, register access, RF reset, RX mode changes, TX submission, firmware information reads, and EUI-64 retrieval. Firmware interprets `wValue`, `wIndex`, and data lengths according to the comment table in this header.

State and persistence behavior: The header has no runtime state. Some requests affect persistent device EEPROM (`ATUSB_EUI64_WRITE`) or retrieve persistent EUI-64 data (`ATUSB_EUI64_READ`), but the Linux driver only reads EUI-64 in this source set.

Dependencies and integration points: It depends on USB request flag macros supplied by Linux USB headers in users. Its main integration point is the firmware ABI; request numbers and data layouts must remain synchronized with ATUSB firmware.

Risks and edge cases: Changing enum values, directions, lengths, or hardware type numbers breaks compatibility with existing firmware. Comments document expected transfer shapes and are part of the practical ABI. Firmware capabilities vary by version, so drivers must continue gating newer requests such as EUI-64 reads.

Test signals: Compile the ATUSB driver, verify USB device matching, run probe against firmware versions before and after EUI-64 support, confirm request numbers with usbmon traces, and test RF reset, register read/write, RX mode, TX, build string, and EUI-64 read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/atusb.h -->
