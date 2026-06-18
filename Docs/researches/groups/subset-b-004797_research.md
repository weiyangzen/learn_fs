# subset-b-004797 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c

## Purpose
`pcie.c` is the Broadcom/Cypress `brcmfmac` PCIe bus backend. It registers the PCI driver, enumerates supported PCIe chip IDs, requests firmware/NVRAM/CLM/TXCAP blobs, downloads firmware into device RAM, discovers firmware shared RAM, builds MSGBUF common and flow rings, wires those rings into the core `brcmf_bus`/protocol layer, handles PCIe mailbox interrupts, and implements reset, suspend/resume, firmware console, coredump, and blob handoff behavior.

## Important APIs, types, and functions
- `struct brcmf_pciedev_info` is the main persistent bus state: PCI device, firmware names/blobs, MMIO mappings, chip metadata, shared RAM/ring metadata, IRQ state, mailbox wait queue, DMA index buffers, OTP parameters, WoWL flag, and debug console timer state.
- `struct brcmf_pcie_shared_info` mirrors firmware shared RAM fields: protocol version/flags, common rings, flow rings, ring counts, rx offsets, mailbox data addresses, firmware console address, scratch DMA buffers, and DMA ring-update buffers.
- `struct brcmf_pcie_ringbuf` wraps `struct brcmf_commonring` with DMA handle, device index locations, ring id, and backpointer. Its callbacks are registered with `brcmf_commonring_register_cb()`.
- `brcmf_pcie_probe()` allocates bus/private state, attaches the chipcore, selects PCIe register layout, loads module settings, reads OTP where needed, allocates common driver state, and starts async firmware loading through `brcmf_fw_get_firmwares()`.
- `brcmf_pcie_setup()` is the firmware callback. It attaches PCIe quirks, gets/adjusts RAM info, downloads firmware/NVRAM, initializes shared RAM, allocates rings/scratch buffers, requests IRQs, exposes rings to `bus->msgbuf`, calls `brcmf_attach()`, and starts firmware console polling.
- `brcmf_pcie_download_fw_nvram()` enters download state, writes firmware at `ci->rambase`, writes NVRAM and optional random seed near the top of RAM, releases the ARM core, waits for firmware to publish the shared RAM pointer, validates it, and initializes shared state.
- `brcmf_pcie_init_ringbuffers()` reads `brcmf_pcie_dhi_ringinfo`, decides whether indices live in TCM or host DMA memory, allocates common rings, creates flow-ring wrappers, and records firmware limits.
- `brcmf_pcie_quick_check_isr()` and `brcmf_pcie_isr_thread()` implement the threaded interrupt path: mask, acknowledge, handle mailbox data, trigger MSGBUF RX, read console, and re-enable interrupts when the bus is up.
- `brcmf_pcie_reset()`, `brcmf_pcie_remove()`, `brcmf_pcie_pm_enter_D3()`, and `brcmf_pcie_pm_leave_D3()` cover driver reset, teardown, D3 entry, and hot/cold resume.

## Control flow
The PCI driver registers through `brcmf_pcie_register()`. Probe allocates `brcmf_pciedev_info`, maps BAR resources through the chip attach path, chooses register offsets based on PCIe core revision, creates `brcmf_bus` with `BRCMF_PROTO_MSGBUF`, obtains module parameters, optionally parses OTP for Apple/WCC/BCA firmware board-type selection, and requests firmware. The firmware callback downloads the image, waits for the firmware shared-memory handshake, configures DMA rings and scratch buffers, enables mailbox IRQs, attaches the common driver, and leaves the bus in `BRCMFMAC_PCIE_STATE_UP`.

Runtime TX/RX data transport is delegated to MSGBUF through common-ring callbacks. Ring callbacks write/read host or TCM indices and ring the H2D mailbox. PCIe D2H doorbells wake the threaded ISR, which acknowledges the mailbox register, processes function-zero mailbox data such as D3 ACK/deep-sleep/FW halt, and calls `brcmf_proto_msgbuf_rx_trigger()` when D2H ring doorbells arrive.

Reset and resume deliberately tear down high-level state before reusing the firmware path. `brcmf_pcie_reset()` disables interrupts, drains console logs, detaches core driver state, releases IRQs/DMA rings/scratch buffers, watchdog-resets the device, and reloads firmware. Resume first attempts a hot D0 mailbox handshake; if the intmask indicates the device is not alive, it removes and reprobes the PCI function.

## State and persistence behavior
Persistent state is in heap allocations owned by the PCI device lifetime: `brcmf_pciedev_info`, `brcmf_pciedev`, `brcmf_bus`, `bus->msgbuf`, DMA common rings, optional host index DMA buffer, scratch/ring-update DMA buffers, firmware blobs retained until common code requests them, module settings, and chip metadata. Firmware/NVRAM contents are not persisted by the driver beyond download; firmware names and optional CLM/TXCAP firmware pointers are kept for later handoff. Device state is represented by `BRCMFMAC_PCIE_STATE_DOWN/UP`, `irq_allocated`, `mbdata_completed`, `in_irq`, `wowl_enabled`, and debug console timer flags.

The file also maintains shared hardware state: BAR0 window selection, PCI config registers restored around reset, mailbox data fields in TCM, DMA ring index host addresses in the firmware ring-info block, and D3/D0/deep-sleep mailbox protocol bits.

## Dependencies and integration points
This backend depends on Linux PCI/MSI/firmware/DMA APIs, Broadcom chipcore helpers (`chip.c`, `soc.h`, `chipcommon.h`), `firmware.h`, `commonring.h`, `msgbuf.h`, `bus.h`, `core.h`, `common.h`, module parameter handling, and debug/trace helpers. It integrates upward through `struct brcmf_bus_ops` (`preinit`, `stop`, `wowl_config`, `get_ramsize`, `get_memdump`, `get_blob`, `reset`, `debugfs_create`) and through `bus->msgbuf` common/flow ring pointers consumed by the MSGBUF protocol layer.

## Risks and edge cases
- Shared RAM version and address validation are critical; unsupported versions or bad pointers abort setup.
- Ring initialization depends on firmware-provided counts and offsets. The code rejects `max_flowrings > 512`, but many other ring-info fields are trusted after endian conversion.
- Host index DMA mode switches pointer accessors from TCM to host memory; lifetime and cache coherency rely on coherent allocation and correct firmware address publication.
- `brcmf_pcie_send_mb_data()` waits up to about one second for an existing mailbox transaction to clear; stuck firmware can block reset/suspend paths.
- `brcmf_pcie_release_irq()` frees IRQ then polls `in_irq`, so races around threaded IRQ completion are explicitly handled but still timing-sensitive.
- Firmware download places NVRAM and optional random seed at top-of-RAM; bad RAM sizing or seed placement can corrupt firmware-owned memory.
- OTP parsing rejects malformed Apple board parameters and can fail probe for WCC/BCA paths.
- Resume has two distinct paths. Hot resume depends on firmware still responding; cold resume removes and reprobes, increasing teardown/reentry risk.

## Test signals
Useful validation signals include successful PCI probe, firmware request names/board-type selection, `PCIe protocol version` log, shared RAM address log, ring count logs, IRQ request success, `brcmf_attach()` success, MSGBUF traffic, D3 ACK wait completion, hot resume logs, firmware coredump/memdump availability, debugfs `console_interval`, and negative tests for missing firmware, invalid shared RAM version/address, unsupported OTP data, IRQ request failure, ring allocation failure, and resume fallback reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.h

## Purpose
`pcie.h` is the minimal internal PCIe bus header for `brcmfmac`. It exposes the public wrapper object that connects generic bus state to the private PCIe implementation.

## Important APIs, types, and functions
- `struct brcmf_pciedev` contains `struct brcmf_bus *bus` and `struct brcmf_pciedev_info *devinfo`.
- `struct brcmf_pciedev_info` is intentionally forward-declared by use only; its definition remains private in `pcie.c`.

## Control flow
The header has no executable control flow. `pcie.c` allocates `struct brcmf_pciedev`, fills its `bus` and `devinfo` fields during probe, stores it under `bus->bus_priv.pcie`, and later retrieve it from bus operations, reset, remove, and PM paths.

## State and persistence behavior
The struct is a persistent ownership bridge for the PCI device lifetime. It does not own resources by itself; it points to the generic `brcmf_bus` allocation and the PCIe-specific `devinfo` allocation. Teardown in `pcie.c` frees the wrapper and the pointed-to state.

## Dependencies and integration points
The type depends on declarations of `struct brcmf_bus` and `struct brcmf_pciedev_info` from surrounding driver headers/source. It is consumed by the bus-private union in `bus.h` and by PCIe bus operations in `pcie.c`.

## Risks and edge cases
Because the wrapper only contains raw pointers, correctness depends on probe/remove ordering and clearing `dev_set_drvdata()` after free. There is no local lifetime protection or reference counting in this header.

## Test signals
Compile coverage is the main signal. Runtime signals come from PCIe probe/remove/reset paths successfully dereferencing `bus->bus_priv.pcie` without NULL or use-after-free faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pno.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pno.c

## Purpose
`pno.c` implements preferred network offload and cfg80211 scheduled-scan support for `brcmfmac`. It tracks active scheduled scan requests, translates cfg80211 match sets, channels, scan plans, and random-MAC options into firmware PFN/GSCAN iovars, starts/stops firmware PNO, and maps firmware bucket results back to cfg80211 request IDs.

## Important APIs, types, and functions
- `struct brcmf_pno_info` stores up to `BRCMF_PNO_MAX_BUCKETS` live `cfg80211_sched_scan_request *` pointers and protects them with `req_lock`.
- `brcmf_pno_start_sched_scan()` stores a request and reprograms firmware PNO. On failure it removes the new request and restores any older active requests.
- `brcmf_pno_stop_sched_scan()` removes a request, clears firmware PNO state, and reprograms remaining requests if any.
- `brcmf_pno_prep_fwconfig()` computes a base scan period using `gcd()` of the first scan-plan interval for each request, fills a shared channel list, creates one firmware GSCAN bucket per request, and returns the bucket count.
- `brcmf_pno_config_sched_scans()` is the main firmware programming sequence: clean existing PFN state, set PFN parameters, configure channels, configure GSCAN buckets, set random MAC if requested, add SSID/BSSID match entries, and enable PFN.
- `brcmf_pno_add_ssid()` and `brcmf_pno_add_bssid()` issue `pfn_add` and `pfn_add_bssid` iovars.
- `brcmf_pno_set_random()` constructs `brcmf_pno_macaddr_le` from cfg80211 random address/mask and local-random bits.
- `brcmf_pno_find_reqid_by_bucket()` and `brcmf_pno_get_bucket_map()` map firmware bucket indexes and netinfo matches to request IDs/maps.
- `brcmf_pno_wiphy_params()` publishes scheduled-scan capabilities to cfg80211.

## Control flow
Attach allocates `brcmf_pno_info` under `cfg->pno`. Starting a scheduled scan appends the cfg80211 request to the in-memory request array under lock, then rebuilds all firmware PNO state from the full request set. Rebuild first disables and clears PFN, configures base PFN scanning, sets channel and bucket information, optionally programs random MAC, pushes SSID/BSSID match entries, then enables `pfn`.

Stopping a scan removes the request by `reqid`, disables/clears PFN, and, if other requests remain, performs the same full reconfiguration. Firmware result handling elsewhere can call the bucket helpers to convert firmware bucket indexes or netinfo entries into cfg80211 request IDs/bucket bitmaps.

## State and persistence behavior
PNO state is memory-resident and tied to the cfg80211 driver configuration lifetime. The module stores raw pointers to cfg80211 scheduled scan requests, not copies; it assumes cfg80211 keeps those requests valid until stopped. Firmware state is persistent inside the dongle until explicitly cleared by `pfn=0` and `pfnclear` or overwritten by a new configuration. No on-disk persistence exists.

## Dependencies and integration points
The file depends on cfg80211 scheduled-scan structs, Broadcom firmware iovar helpers (`brcmf_fil_iovar_*`), firmware layout structs from `fwil_types.h`, driver config from `cfg80211.h`, `core.h`, and scan/debug helpers. It integrates with wiphy capability setup, cfg80211 scheduled-scan start/stop callbacks, and firmware event/result decoding through bucket-map helpers declared in `pno.h`.

## Risks and edge cases
- `brcmf_pno_store_request()` checks capacity with `WARN()` before taking the mutex, so concurrent callers rely on higher-level serialization plus the mutexed write section.
- The request array stores external pointers; stale request lifetime would corrupt later matching or stop handling.
- Only `scan_plans[0].interval` is used for each request, so multi-plan cfg80211 semantics are collapsed.
- Channel aggregation can exceed `BRCMF_NUMCHANNELS`; that returns `-ENOSPC` and rolls back the current start.
- `brcmf_pno_set_random()` uses the first request with `NL80211_SCAN_FLAG_RANDOM_ADDR`; multiple active requests with different randomization needs are not independently represented.
- Full firmware reprogramming on every add/remove means transient failures can clear active PNO; start failure attempts restoration for previous requests, stop failure does not restore the removed one.
- Hidden SSID active-scan detection is based on SSID equality between match sets and request SSID list.

## Test signals
Signals include wiphy scheduled-scan limits, successful `pfn_set`, `pfn_cfg`, `pfn_gscan_cfg`, `pfn_macaddr`, `pfn_add`, `pfn_add_bssid`, and `pfn=1` iovars; rollback after an injected iovar failure; bucket-to-request ID mapping for multiple simultaneous requests; random MAC bit correctness; channel overflow behavior; and `WARN_ON(pi->n_reqs)` staying quiet during detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pno.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pno.h

## Purpose
`pno.h` declares the scheduled-scan/PNO interface used by the cfg80211 and firmware-event portions of `brcmfmac`.

## Important APIs, types, and functions
- Constants: `BRCMF_PNO_SCAN_COMPLETE`, `BRCMF_PNO_MAX_PFN_COUNT`, and scheduled-scan min/max period limits.
- Forward declaration: `struct brcmf_pno_info`.
- Public functions: `brcmf_pno_start_sched_scan()`, `brcmf_pno_stop_sched_scan()`, `brcmf_pno_wiphy_params()`, `brcmf_pno_attach()`, `brcmf_pno_detach()`, `brcmf_pno_find_reqid_by_bucket()`, and `brcmf_pno_get_bucket_map()`.

## Control flow
The header has no implementation flow. It defines the call surface: cfg80211 setup attaches PNO state and publishes wiphy limits; scheduled-scan callbacks start/stop firmware PNO; firmware result processing can resolve request IDs and bucket maps from PNO state.

## State and persistence behavior
The header exposes `struct brcmf_pno_info` opaquely, forcing users to manage it through attach/detach and helper functions. Runtime state lives in `pno.c` and under `cfg->pno`; there is no persisted data.

## Dependencies and integration points
The declarations depend on driver types such as `struct brcmf_if`, `struct brcmf_cfg80211_info`, `struct brcmf_pno_net_info_le`, cfg80211 scheduled-scan request types, and `struct wiphy`. It integrates cfg80211-facing code with firmware result handling.

## Risks and edge cases
The opaque type keeps internals private, but callers must obey lifetime expectations: attach before start/stop/result mapping, stop all active requests before detach, and pass netinfo structures with firmware-compatible SSID/BSSID fields.

## Test signals
Compile coverage across cfg80211 and event code is the primary test signal. Runtime tests should verify attach/start/stop/detach ordering and bucket-map helpers under multiple scheduled scan requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/proto.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/proto.c

## Purpose
`proto.c` is the protocol dispatcher for `brcmfmac`. It allocates the generic `struct brcmf_proto`, selects the concrete firmware protocol implementation based on the bus-advertised `proto_type`, verifies that required callbacks were installed, and detaches the selected implementation during teardown.

## Important APIs, types, and functions
- `brcmf_proto_attach(struct brcmf_pub *drvr)` allocates `drvr->proto`, dispatches to `brcmf_proto_bcdc_attach()` for `BRCMF_PROTO_BCDC` or `brcmf_proto_msgbuf_attach()` for `BRCMF_PROTO_MSGBUF`, validates mandatory handlers, and returns `0` or `-ENOMEM`.
- `brcmf_proto_detach(struct brcmf_pub *drvr)` calls the matching BCDC/MSGBUF detach routine and frees `drvr->proto`.
- Required handlers checked here include `tx_queue_data`, `hdrpull`, `query_dcmd`, `set_dcmd`, `configure_addr_mode`, `delete_peer`, `add_tdls_peer`, and `debugfs_create`.

## Control flow
Attach is called after bus setup but before normal network operation. The bus backend sets `drvr->bus_if->proto_type`; `proto.c` uses that value to attach protocol-specific state and function pointers. If protocol type is unsupported or any required callback remains unset, it logs an error, frees the generic proto object, clears `drvr->proto`, and fails. Detach mirrors the type dispatch and releases protocol-specific then generic state.

## State and persistence behavior
The only state owned here is the heap-allocated `struct brcmf_proto` stored in `drvr->proto`. Concrete protocol modules may place private data in `proto->pd`. This state persists for the `brcmf_pub` lifetime and is not persisted externally.

## Dependencies and integration points
The file depends on `core.h`, `bus.h`, `proto.h`, `bcdc.h`, and `msgbuf.h`. It integrates SDIO/USB-style BCDC buses and PCIe MSGBUF buses with the common core through a single vtable consumed by inline wrappers in `proto.h`.

## Risks and edge cases
- All attach failures return `-ENOMEM`, even unsupported protocol type or missing handler cases, which can obscure root cause.
- The required-callback check covers only mandatory fields. Optional callbacks must be NULL-safe at call sites.
- Because protocol choice comes from bus state, a bus backend that sets the wrong `proto_type` can attach the wrong implementation or fail late.

## Test signals
Test by probing both BCDC and MSGBUF bus types, validating required callbacks are populated, forcing unsupported `proto_type`, injecting attach failures in concrete protocols, and ensuring detach frees `drvr->proto` without leaking or double-detaching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/proto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/proto.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/proto.h

## Purpose
`proto.h` defines the internal protocol vtable and inline wrappers used by the rest of `brcmfmac` to issue data, control, address-mode, TDLS, reorder, interface lifecycle, initialization, and debugfs operations without knowing whether the active bus uses BCDC or MSGBUF.

## Important APIs, types, and functions
- `enum proto_addr_mode` selects indirect or direct firmware address mode.
- `struct brcmf_skb_reorder_data` reserves skb control-buffer space for RX reorder tracking.
- `struct brcmf_proto` is the protocol vtable. It includes handlers for header pull, firmware dcmd query/set, queued/direct TX, address mode, peer deletion/addition, RX reorder, interface add/delete/reset, init completion, debugfs, and private data.
- Inline wrappers include `brcmf_proto_hdrpull()`, `brcmf_proto_query_dcmd()`, `brcmf_proto_set_dcmd()`, `brcmf_proto_tx_queue_data()`, `brcmf_proto_txdata()`, `brcmf_proto_configure_addr_mode()`, `brcmf_proto_delete_peer()`, `brcmf_proto_add_tdls_peer()`, `brcmf_proto_rxreorder()`, interface lifecycle helpers, `brcmf_proto_init_done()`, and `brcmf_proto_debugfs_create()`.

## Control flow
After `brcmf_proto_attach()` installs a concrete vtable, higher-level code calls these inline wrappers. Most wrappers directly dispatch through `drvr->proto`; optional interface lifecycle and init-done hooks check for NULL and no-op when absent. `brcmf_proto_hdrpull()` normalizes a NULL `ifp` output argument to a local temporary pointer so implementations always receive a non-NULL `struct brcmf_if **`.

## State and persistence behavior
`struct brcmf_proto` persists under `drvr->proto`; private implementation state hangs off `pd`. `brcmf_skb_reorder_data` overlays `skb->cb`, so its state is packet-local and lifetime-bound to the skb. No state is persisted outside memory.

## Dependencies and integration points
The header depends on common driver types (`brcmf_pub`, `brcmf_if`), Linux `sk_buff`, Ethernet address length, and protocol implementations that populate the vtable. It is a central integration point between core networking/cfg80211 code and BCDC/MSGBUF transport protocols.

## Risks and edge cases
- Required wrappers assume `drvr->proto` and relevant callbacks are non-NULL; safety relies on `proto.c` validation before use.
- `brcmf_proto_is_reorder_skb()` interprets `skb->cb` as `brcmf_skb_reorder_data`; other skb control-buffer users must not conflict.
- Optional hooks are no-op when missing, so behavior differences between BCDC and MSGBUF can be silent.
- There is a minor style issue in `brcmf_proto_query_dcmd()` spacing (`len,fwerr`) but no behavior impact.

## Test signals
Compile and runtime coverage should exercise all wrappers through both protocol implementations, NULL optional hooks, RX reorder skb markers, dcmd query/set paths, interface add/delete/reset, and debugfs creation. Fault injection should verify no wrapper is called before successful protocol attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c

## Purpose
`sdio.c` is the main SDIO bus backend for `brcmfmac`. It initializes SDIO chips, downloads firmware/NVRAM/CLM, implements SDPCM framing over function 2, manages interrupts and deferred processing, handles control/data TX/RX, glomming, flow control, clock and sleep state, watchdog polling, debug forensics, reset/remove, and integration with the BCDC protocol.

## Important APIs, types, and functions
- `struct brcmf_sdio` is the central runtime state: SDIO device pointer, chip/core metadata, interrupt masks/status atomics, TX queue and flow control, SDPCM sequence/window state, RX header/control buffers, glom queues, clock/sleep state, control-frame wait queues, watchdog timer/thread, ordered workqueue, counters, SR state, and alignment/glomming configuration.
- `struct brcmf_sdio_count` holds debug counters for interrupts, polling, register failures, TX/RX errors, flow control, glomming, frame transfers, control frames, and readahead.
- SDPCM helpers `brcmf_sdio_hdparse()`, `brcmf_sdio_hdpack()`, `brcmf_sdio_update_hwhdr()`, and `brcmf_sdio_getdatoffset()` parse and construct the hardware/software packet headers.
- RX path: `brcmf_sdio_dpc()` -> `brcmf_sdio_readframes()` -> `brcmf_sdio_read_control()`, `brcmf_sdio_rxglom()`, `brcmf_rx_event()`, or `brcmf_rx_frame()`.
- TX path: `brcmf_sdio_bus_txdata()` enqueues priority packets; `brcmf_sdio_sendfromq()` dequeues under firmware window/flow-control limits; `brcmf_sdio_txpkt()` prepares headers/alignment and calls `brcmf_sdiod_send_pkt()`; `brcmf_sdio_bus_txctl()` sends synchronous control frames via the DPC.
- Clock/power helpers include `brcmf_sdio_kso_control()`, `brcmf_sdio_htclk()`, `brcmf_sdio_clkctl()`, `brcmf_sdio_bus_sleep()`, `brcmf_sdio_sr_init()`, `brcmf_sdio_sleep()`, and watchdog timer helpers.
- Probe/setup functions include `brcmf_sdio_probe()`, `brcmf_sdio_probe_attach()`, `brcmf_sdio_prepare_fw_request()`, `brcmf_sdio_firmware_callback()`, `brcmf_sdio_bus_preinit()`, and `brcmf_sdio_remove()`.
- Bus integration is through `brcmf_sdio_bus_ops`, which supplies stop, preinit, tx/rx control, tx data, tx queue lookup, WoWL, RAM size/memdump, blob retrieval, debugfs, reset, and remove hooks.

## Control flow
`brcmf_sdio_probe()` allocates `struct brcmf_sdio`, creates an ordered high-priority workqueue, attaches chip/core state, sets alignments and drive strength, prepares queues/buffers/wait queues/watchdog, disables function 2 to clear stale device state, initializes clock state, then requests firmware. The firmware callback downloads firmware and NVRAM, starts the ARM core, enables the watchdog, forces clocks, enables function 2, programs host interrupt mask and chip-specific watermarks, optionally enables SaveRestore/KSO behavior, registers interrupts, marks the SDIO device data-ready, then calls `brcmf_alloc()` and `brcmf_attach()`.

Runtime interrupts call `brcmf_sdio_isr()`, which records pending interrupt state and queues `brcmf_sdio_dataworker()`. The worker loops while `dpc_triggered` is set, calling `brcmf_sdio_dpc()`. DPC wakes the bus, reads and acknowledges interrupt status, handles mailbox data such as firmware ready, flow-control, NAK completion, and firmware halt, processes RX frame indications, transmits pending control frames, drains data TX queue within firmware credit windows, and reschedules itself if more work remains.

RX reads parse SDPCM headers, validate checksum/length/channel/offset/sequence/window fields, update firmware TX window and flow-control bits, and dispatch control frames to the dcmd response waiter or data/event frames upward. Glom descriptor frames allocate a packet chain, read the superframe, validate each subframe, then deliver each subpacket. RX failures may abort function 2, terminate frames, and optionally NAK to request event/control retransmission.

TX data pushes SDPCM header room, maps skb priority to a precedence queue, applies high/low water flow blocking to the protocol layer, and triggers DPC. DPC dequeues packets not blocked by firmware flow-control bits, supports optional TX glomming with scatter-gather alignment and tail padding, sends via SDIO CMD53, updates sequence numbers, postprocesses skbs back to their original layout, and completes them to BCDC.

## State and persistence behavior
All runtime state is volatile and tied to the SDIO device lifetime. Firmware/NVRAM are loaded into dongle RAM during setup; CLM firmware is retained in `sdiodev->clm_fw` until the common layer asks for it via `get_blob`. TX/RX sequence numbers, flow-control masks, firmware credit window, glom descriptors, control response buffers, counters, and clock/sleep state persist across runtime operations but are reset on bus stop/remove. The watchdog timer and thread periodically poll interrupts, firmware console output in debug builds, idle clock transitions, and freezer state.

The driver also mutates device-side persistent-for-session state: CCCR card control, function 1 misc registers, SB address windows, PMU drive strength, F2 watermarks, host interrupt masks, mailbox data, firmware RAM, NVRAM placement, and SaveRestore/KSO registers.

## Dependencies and integration points
The file depends on Linux MMC/SDIO APIs, firmware loading, kthreads, workqueues, timers, debugfs, Broadcom chipcore and firmware helpers, `brcmf_sdiod_*` low-level SDIO accessors from other files, `bcdc.h`, `bus.h`, `core.h`, `common.h`, `tracepoint.h`, and protocol/common attach functions. It integrates upward as a `brcmf_bus_ops` provider for BCDC and downward through SDIO function 0/1/2 register and buffer transfers.

## Risks and edge cases
- SDPCM header parsing is a major trust boundary. Length checksum, data offset, channel, next-frame length, and sequence checks protect against desynchronization, but bad firmware/device data still drives abort/NAK behavior.
- Control TX/RX is wait-queue based with timeouts; missed wakeups, stale `rxctl`, or DPC halt can surface as dcmd timeouts.
- Glomming is allocation- and alignment-heavy. Descriptor length errors, SG entry misalignment, or partial read failures require careful cleanup of queued skbs.
- Clock/KSO/SR transitions are timing-sensitive and chip-specific, including special CY43012 behavior when clearing KSO.
- The DPC uses atomics plus an ordered workqueue; correctness depends on careful setting/clearing of `dpc_triggered`, `intstatus`, `ipend`, and `fcstate`.
- `brcmf_sdio_bus_txdata()` pushes header room before enqueue and must pull it back on enqueue failure; later TX postprocessing must restore skb shape after padding/glomming.
- Firmware callback failure releases both SDIO function drivers, so partial setup paths must avoid leaked IRQs, workqueues, firmware, buffers, or clocks.
- Probe has many chip-specific watermarks and drive-strength settings; regressions may be device-ID specific.

## Test signals
Useful signals include successful SDIO probe, firmware/NVRAM download and optional verify, F2 enable, interrupt registration, `Dongle ready` mailbox, `brcmf_attach()` success, stable TX/RX under flow control, dcmd round trips, glommed and non-glommed RX, watchdog idle sleep/wake, WoWL/sleep behavior, memdump and CLM blob handoff, debugfs counters/forensics, firmware halt handling, injected CMD52/CMD53 failures, malformed SDPCM headers, control timeout, and remove/reset under active traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.h

## Purpose
`sdio.h` declares the SDIO bus/device interface, Broadcom SDIO register constants, function accessors, low-level transfer routines, device state enum, and probe/remove/interrupt/sleep hooks shared between `sdio.c` and lower-level SDIO support code.

## Important APIs, types, and functions
- Register constants cover SDIO CCCR vendor registers, function 1 misc registers, SB/OCP address windowing, function interrupt bits, KSO/SleepCSR, watermark/MES busy controls, and watchdog poll interval.
- `enum brcmf_sdiod_state` distinguishes `BRCMF_SDIOD_DOWN`, `BRCMF_SDIOD_DATA`, and `BRCMF_SDIOD_NOMEDIUM`.
- `struct brcmf_sdio_dev` is the shared SDIO device object: function 1/2 handles, saved backplane window, chipcommon core, `struct brcmf_sdio *bus`, Linux device, `brcmf_bus`, module settings, IRQ flags/lock, SG capabilities/table, request-size limits, firmware/NVRAM/CLM names, WoWL and power-management flags, state/freezer, and retained CLM firmware.
- `struct sdpcmd_regs` maps SDIO core register layout for offset calculations used by `SD_REG()` in `sdio.c`.
- Accessor macros wrap function 0 and function 1 byte reads/writes.
- Declared low-level operations include `brcmf_sdiod_readl/writel()`, packet/buffer send/receive, receive chain, RAM read/write, abort, SG allocation, state/freezer helpers, `brcmf_sdiod_probe/remove()`, `brcmf_sdio_probe/remove()`, `brcmf_sdio_isr()`, watchdog timer, WoWL config, sleep, and DPC trigger.

## Control flow
The header defines the boundary between the high-level SDPCM bus logic in `sdio.c` and lower-level SDIO device operations. Platform/SDIO probe code constructs `brcmf_sdio_dev`, calls `brcmf_sdiod_probe()` and `brcmf_sdio_probe()`, routes interrupts into `brcmf_sdio_isr()`, and later calls remove. `sdio.c` calls low-level buffer/RAM/register helpers declared here to perform CMD52/CMD53 traffic.

## State and persistence behavior
`struct brcmf_sdio_dev` persists for the SDIO function device lifetime and carries both low-level transport state and pointers to high-level bus state. Register constants describe device-side state modified for the current session. Firmware name buffers and retained `clm_fw` persist until removal or blob handoff.

## Dependencies and integration points
The header depends on Linux skb and firmware types plus `firmware.h`. It integrates SDIO function-driver code, chipcore access, firmware setup, interrupt registration, freezer support, and the high-level bus backend.

## Risks and edge cases
- `struct sdpcmd_regs` must match hardware layout; bad offsets affect interrupt masks, mailboxes, and frame control.
- Macros directly call SDIO core functions and assume the correct host claim context is held by callers where required.
- `brcmf_sdio_dev` contains many ownership-sensitive raw pointers and flags; remove paths must coordinate IRQ, freezer, firmware, SG table, and bus state lifetimes.
- Register masks/constants are chip-generation sensitive, especially KSO, CMD14, and address-window behavior.

## Test signals
Compile coverage across `sdio.c` and low-level SDIO files is necessary. Runtime signals include correct register access, interrupt registration/unregistration, state transitions, SG allocation fallback, RAM read/write firmware download, abort behavior, freezer transitions, sleep/wake, and clean remove with function 1/2 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/tracepoint.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/tracepoint.c

## Purpose
`tracepoint.c` instantiates `brcmfmac` tracepoints and provides the shared `__brcmf_err()` logging helper that emits both normal kernel error logs and the `brcmf_err` trace event.

## Important APIs, types, and functions
- `CREATE_TRACE_POINTS` before including `tracepoint.h` causes tracepoint definitions to be emitted in this translation unit.
- `__brcmf_err(struct brcmf_bus *bus, const char *func, const char *fmt, ...)` formats a varargs error using `struct va_format`, logs to `dev_err()` when bus/device context is available or `pr_err()` otherwise, then calls `trace_brcmf_err()`.
- The implementation is excluded under `__CHECKER__`, matching sparse/static-analysis constraints.

## Control flow
Callers use higher-level `brcmf_err` wrappers from bus/source files. Those wrappers pass bus context, function name, and format string to `__brcmf_err()`. This function starts the varargs list, binds it to `va_format`, emits the kernel log, emits the tracepoint, and then ends the varargs list.

## State and persistence behavior
No long-lived mutable state is owned here. The only state is temporary varargs formatting data during a log call and statically registered tracepoint metadata generated by the trace infrastructure.

## Dependencies and integration points
The file depends on Linux device/module logging, `bus.h`, `tracepoint.h`, and `debug.h`. It integrates normal error logging with ftrace/perf-style trace consumers so errors can be observed even when normal logs are rate-limited elsewhere.

## Risks and edge cases
- The same `va_format` is consumed by both `dev_err()`/`pr_err()` and the tracepoint before `va_end()`. The tracepoint stores formatted string data during the call, so ordering matters.
- If `bus` is NULL, logs lose device-specific context and use global `pr_err()`.
- Tracepoint generation is sensitive to `CREATE_TRACE_POINTS` being defined in exactly one compilation unit.

## Test signals
Compile with and without `CONFIG_BRCM_TRACING`, run error paths with bus and NULL bus contexts, verify kernel log output, and verify `brcmf_err` trace events appear when tracing is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/tracepoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/tracepoint.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/tracepoint.h

## Purpose
`tracepoint.h` defines the `brcmfmac` trace events used for errors, debug messages, hexdumps, BCDC headers, and SDPCM headers. It also supplies no-op inline stubs when tracing is disabled so callers can use trace functions unconditionally.

## Important APIs, types, and functions
- Fallback macro overrides for `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, and `DEFINE_EVENT` create inline no-op `trace_*` functions when `CONFIG_BRCM_TRACING` is not enabled.
- `TRACE_SYSTEM brcmfmac` names the trace subsystem.
- `TRACE_EVENT(brcmf_err)` records function name and formatted error message from `struct va_format`.
- `TRACE_EVENT(brcmf_dbg)` records debug level, function name, and formatted message.
- `TRACE_EVENT(brcmf_hexdump)` records a data address, length, and dynamic byte array.
- `TRACE_EVENT(brcmf_bcdchdr)` extracts BCDC flags, priority, flags2, signal length, and dynamic signal bytes.
- `TRACE_EVENT(brcmf_sdpcm_hdr)` records SDPCM direction, length, sequence number, and a 12- or 20-byte header snapshot.
- When tracing is enabled, `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>` integrate with the kernel trace generation system.

## Control flow
At compile time, tracing-enabled builds generate tracepoint code from these macros, with `tracepoint.c` acting as the definition site. Tracing-disabled builds replace trace calls with inline no-ops. Runtime trace calls copy relevant fields or dynamic arrays into trace buffers and format compact `TP_printk()` summaries for consumers.

## State and persistence behavior
The header defines static trace metadata and per-event trace records. It does not own driver runtime state. Event payloads copy data from caller-provided pointers at trace time.

## Dependencies and integration points
The file depends on Linux tracepoint infrastructure and `struct va_format`. It is used by debug/error helpers, BCDC protocol code, and SDIO SDPCM framing code. The SDPCM direction fallback macros keep this header independent enough to compile even if direction constants are not already defined.

## Risks and edge cases
- Trace events that copy dynamic data trust caller-provided lengths and pointer validity at trace-call time.
- `brcmf_bcdchdr` derives dynamic array length from byte 3 of the header; malformed or too-short input would be a caller bug.
- `brcmf_sdpcm_hdr` copies 20 bytes for glom headers and 12 bytes otherwise; callers must provide at least that much header data.
- Disabled-tracing macro overrides must stay compatible with call signatures, or no-op builds will break.

## Test signals
Build with tracing disabled to validate no-op stubs, build with `CONFIG_BRCM_TRACING` to validate trace generation, and exercise error/debug/hexdump/BCDC/SDPCM call sites while inspecting trace buffers for expected fields and lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/tracepoint.h -->
