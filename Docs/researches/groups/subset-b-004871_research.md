# Research: subset-b-004871

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00mac.c

## Purpose
`rt2x00mac.c` is the generic mac80211 callback implementation shared by rt2x00 chip drivers. It translates mac80211 operations into rt2x00lib device, interface, crypto, queue, beacon, antenna, scan, rfkill, and statistics operations. Hardware-specific drivers, such as `rt61pci.c`, point their `struct ieee80211_ops` callbacks at these functions and override only the pieces that require direct register programming.

## Important APIs, Types, And Functions
The exported mac80211 callbacks include `rt2x00mac_tx`, `rt2x00mac_start`, `rt2x00mac_stop`, `rt2x00mac_reconfig_complete`, `rt2x00mac_add_interface`, `rt2x00mac_remove_interface`, `rt2x00mac_config`, `rt2x00mac_configure_filter`, `rt2x00mac_set_tim`, `rt2x00mac_set_key`, scan start/complete, `rt2x00mac_get_stats`, `rt2x00mac_bss_info_changed`, `rt2x00mac_conf_tx`, `rt2x00mac_rfkill_poll`, `rt2x00mac_flush`, antenna setters/getters, ring parameter reporting, and pending-TX reporting. Internal helper `rt2x00mac_tx_rts_cts()` synthesizes software RTS or CTS-to-self frames when hardware lacks an RTS threshold callback. Crypto setup is compiled under `CONFIG_RT2X00_LIB_CRYPTO` and uses `struct rt2x00lib_crypto`.

## Control Flow
Transmit starts by checking `DEVICE_STATE_PRESENT`, mapping the skb queue to a `struct data_queue`, optionally selecting ATIM, creating a software RTS/CTS frame when requested by the first rate, and calling `rt2x00queue_write_tx_frame()`. Queue-full handling is conservative: it rechecks under `queue->tx_lock`, pauses the mac80211 queue at threshold, and frees the skb on failure. Device start delegates to `rt2x00lib_start()`, but a second start during `ieee80211_restart_hw()` sets `DEVICE_STATE_RESET`, calls `pre_reset_hw`, and stops before restarting. Stop simply gates on presence and calls `rt2x00lib_stop()`.

Interface add reserves a beacon queue entry, increments AP or STA interface counters, initializes the per-interface beacon mutex, configures the MAC address through `rt2x00lib_config_intf()`, and forces a future filter refresh. Removal decrements counters, releases the beacon entry, and clears MAC/BSSID configuration to prevent false ACKs. Configuration stops RX, serializes with `conf_mutex`, calls `rt2x00lib_config()` and antenna configuration, then restarts RX. BSS changes update BSSID, beacon enable state, association counters and LEDs, and ERP/basic-rate/beacon interval/HT parameters. Beacon enabling starts the shared beacon queue only when the first interface begins beaconing, and stopping clears the per-vif beacon while keeping other vifs active.

## State And Persistence
State is primarily in `struct rt2x00_dev`: presence, started, reset, radio, scanning, and flushing bits; AP/STA/beaconing/associated interface counters; `packet_filter`; low-level statistics; default and active antenna state; and queue pointers. Per-interface state in `struct rt2x00_intf` stores the assigned beacon entry, beacon enable flag, delayed update flags, beacon skb mutex, and software sequence counter. No durable storage is written; hardware and firmware state is replayed through rt2x00lib callbacks after restart.

## Dependencies And Integration Points
This file integrates Linux mac80211, cfg80211 interface types, rt2x00lib operations, rt2x00 queue management, rt2x00 crypto helpers, LED handling, link tuner control, and driver-specific `ops->lib` callbacks. It assumes hardware drivers implement queue, filter, interface, key, ERP, antenna, rfkill, and device lifecycle hooks as advertised in `struct rt2x00lib_ops`.

## Risks
The largest risks are queue ownership and state races: mac80211 can call TX/configuration while removal or suspend is underway, so most paths gate on `DEVICE_STATE_PRESENT`. Software RTS/CTS consumes extra queue entries and can drop the data frame if room changes. Beacon queue entries are shared across interfaces and must be assigned and released exactly once. Association counters and beaconing counters can underflow if mac80211 callback ordering changes. Crypto handling intentionally rejects MFP, IBSS group keys, unsupported ciphers, TKIP on USB, and oversize keys; incorrect acceptance would produce hardware decryption failures. The antenna API maps user diversity requests into hardware or software diversity flags, so wrong defaults can confuse link tuning.

## Test Signals
Useful signals are successful interface add/remove for AP, station, adhoc, and mesh modes; TX under queue pressure with RTS/CTS and CTS protect flags; restart via `ieee80211_restart_hw()` clearing `DEVICE_STATE_RESET`; beacon enable/disable on multiple AP-like vifs; hardware crypto set/remove for pairwise keys and expected software fallback for unsupported keys; scan start/complete pausing and restarting the tuner; flush draining all TX queues; antenna set/get with diversity values; and correct ring parameter and pending-frame reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00mmio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00mmio.c

## Purpose
`rt2x00mmio.c` provides generic support for rt2x00 devices accessed through memory-mapped I/O, mainly PCI/PCIe chips. It implements busy-wait register polling, RX completion for descriptor rings, simple queue flush waiting, coherent descriptor DMA allocation, IRQ registration, and corresponding cleanup.

## Important APIs, Types, And Functions
Exported APIs are `rt2x00mmio_regbusy_read()`, `rt2x00mmio_rxdone()`, `rt2x00mmio_flush_queue()`, `rt2x00mmio_initialize()`, and `rt2x00mmio_uninitialize()`. Internal helpers allocate and free coherent descriptor memory for every `struct data_queue`. Per-entry MMIO private state is `struct queue_entry_priv_mmio` from `rt2x00mmio.h`, containing descriptor virtual and DMA addresses.

## Control Flow
`rt2x00mmio_regbusy_read()` reads a register until a supplied bit field clears, delaying between attempts, and returns a success boolean. `rt2x00mmio_rxdone()` processes up to 15 RX entries per invocation. It stops when the hardware-specific `get_entry_state()` says the current entry is still device-owned, wires the descriptor pointer into the skb descriptor, marks DMA start/done, and passes the entry to `rt2x00lib_rxdone()` with `GFP_ATOMIC`. Returning true means the tasklet should reschedule because the loop hit its per-pass budget.

Initialization iterates all queues, allocates one coherent descriptor block per queue sized `limit * desc_size`, and stores per-entry descriptor pointers. After descriptor memory is ready it requests the device IRQ using the hardware driver's `irq_handler`. Error unwind frees all descriptor allocations already made. Uninitialization frees the IRQ first, then releases coherent descriptor memory for every queue.

## State And Persistence
The file mutates queue entry private descriptor pointers and the device IRQ registration. Descriptor memory persists only while the device is initialized. RX completion updates queue indices indirectly through rt2x00lib once entries are processed. There is no durable state outside device memory and kernel allocations.

## Dependencies And Integration Points
It depends on `rt2x00mmio.h` register accessors, Linux DMA coherent allocation, IRQ APIs, queue metadata from `rt2x00queue.h`, and rt2x00lib RX/DMA callbacks. Hardware drivers such as `rt61pci.c` supply descriptor sizes, queue limits, `get_entry_state()`, `clear_entry()`, and the interrupt handler.

## Risks
The RX loop relies on the hardware driver's descriptor ownership bit being correct; a stale or inverted bit can either drop completions or spin through entries not ready for the host. Descriptor DMA allocation must match the queue layout and hardware ring base programming. The flush helper only waits up to ten 50 ms intervals and ignores `drop`, so hardware drivers that cannot drain queues in that window will report flush failures higher up. IRQ registration after DMA allocation means unwind ordering must stay correct.

## Test Signals
Test signals include successful coherent DMA allocation for all RX/TX/beacon queues, IRQ request/free pairing, RX tasklet processing batches without descriptor corruption, indirect register busy-read timeout logging for stuck BBP/RF/MCU registers, queue flush behavior under active TX/RX, and clean suspend/remove without leaked IRQs or DMA mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00mmio.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00mmio.h

## Purpose
`rt2x00mmio.h` declares the MMIO transport interface and provides inline register accessors for rt2x00 memory-mapped devices. It is the contract used by PCI-style hardware drivers to read and write CSR space, allocate per-entry descriptor state, and call shared MMIO queue/lifecycle helpers.

## Important APIs, Types, And Functions
Inline functions `rt2x00mmio_register_read()`, `rt2x00mmio_register_multiread()`, `rt2x00mmio_register_write()`, and `rt2x00mmio_register_multiwrite()` wrap `readl()`, `memcpy_fromio()`, `writel()`, and `__iowrite32_copy()` against `rt2x00dev->csr.base + offset`. The header declares `rt2x00mmio_regbusy_read()`, `rt2x00mmio_rxdone()`, `rt2x00mmio_flush_queue()`, `rt2x00mmio_initialize()`, and `rt2x00mmio_uninitialize()`. `struct queue_entry_priv_mmio` stores a descriptor pointer and DMA address for each queue entry.

## Control Flow
Hardware drivers include this header to perform direct CSR access and to provide shared transport callbacks in `struct rt2x00lib_ops`. Typical flow is PCI probe maps BAR0 into `rt2x00dev->csr.base`, queue allocation assigns `priv_size = sizeof(struct queue_entry_priv_mmio)`, MMIO initialization fills each private descriptor pointer, and hardware init programs ring base registers from `desc_dma`.

## State And Persistence
The header does not own state by itself. Its accessors operate on the mapped CSR base owned by the PCI probe path. `queue_entry_priv_mmio` is persistent for the lifetime of queue entries and points into coherent DMA descriptor memory allocated by `rt2x00mmio.c`.

## Dependencies And Integration Points
It depends on Linux I/O helpers and rt2x00 core definitions. The accessors are used heavily by chip drivers such as `rt61pci.c` for register, BBP, RF, EEPROM, queue, interrupt, and power-state programming.

## Risks
The inline register functions perform no bounds checks on offsets or lengths. Multiwrite assumes the length is a multiple of four because it shifts by two for `__iowrite32_copy()`. Consumers must ensure `csr.base` is valid and device presence is checked at the call site where necessary. Descriptor DMA addresses must fit the hardware programming model.

## Test Signals
Signals are compile coverage for all MMIO users, successful CSR reads/writes during probe, ring-base programming matching `queue_entry_priv_mmio.desc_dma`, and no sparse/endian warnings around descriptor and register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00mmio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00pci.c

## Purpose
`rt2x00pci.c` is the generic PCI/PCIe bus glue for rt2x00 PCI drivers. It handles PCI enablement, BAR mapping, DMA mask setup, `ieee80211_hw` allocation, rt2x00 device initialization, and remove/suspend/resume forwarding to rt2x00lib.

## Important APIs, Types, And Functions
The exported APIs are `rt2x00pci_probe()`, `rt2x00pci_remove()`, and `rt2x00pci_pm_ops`. Private helpers `rt2x00pci_alloc_reg()` and `rt2x00pci_free_reg()` map BAR0 and allocate EEPROM/RF shadow arrays sized by `struct rt2x00_ops`.

## Control Flow
Probe enables the PCI function, requests regions, enables bus mastering and optionally MWI, requires a 32-bit DMA mask, allocates mac80211 hardware with private `struct rt2x00_dev`, sets driver data, initializes the rt2x00 device fields, detects PCI versus PCIe interface type, maps/register-allocates local storage, stores the PCI device id into `chip.rt` for early efuse users, and calls `rt2x00lib_probe_dev()`. Every failure label unwinds the resources acquired so far. Remove calls `rt2x00lib_remove_dev()`, frees mapped/shadow register storage, frees mac80211 hardware, clears MWI, disables the device, and releases regions. PM callbacks retrieve `rt2x00_dev` from driver data and call `rt2x00lib_suspend()` or `rt2x00lib_resume()`.

## State And Persistence
The file owns the bus-level lifetime of `rt2x00dev->csr.base`, `rt2x00dev->eeprom`, `rt2x00dev->rf`, `rt2x00dev->irq`, `rt2x00dev->dev`, `rt2x00dev->hw`, and `rt2x00dev->name`. EEPROM and RF arrays are kernel shadow storage, not persistent writes to device EEPROM unless other code explicitly writes through rt2x00 helpers.

## Dependencies And Integration Points
It integrates Linux PCI APIs, DMA mask configuration, mac80211 `ieee80211_alloc_hw()`, rt2x00 core probing, and chip-specific `struct rt2x00_ops`. Chip drivers such as `rt61pci.c` provide the PCI id table and invoke this generic probe from their bus-specific `probe` callback.

## Risks
The probe path assumes BAR0 is the CSR region and that devices support 32-bit DMA. Resource unwind ordering is important because rt2x00lib may register mac80211 state and start work before remove. `pci_release_regions()` is called after `pci_disable_device()` in remove, while probe unwind releases regions before disable; both are common but worth preserving intentionally. Early `chip.rt` initialization is needed by some chip-specific paths before full EEPROM parsing.

## Test Signals
Expected signals are clean probe/remove for all supported PCI IDs, valid BAR mapping, successful 32-bit DMA setup, mac80211 registration through rt2x00lib, suspend/resume callbacks on PCI power events, and no leaks or use-after-free reports when probe fails at each staged label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00pci.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00pci.h

## Purpose
`rt2x00pci.h` is the public header for the generic rt2x00 PCI bus library. It lets chip-specific PCI drivers call shared probe/remove code and attach shared PM operations.

## Important APIs, Types, And Functions
It declares `rt2x00pci_probe(struct pci_dev *pci_dev, const struct rt2x00_ops *ops)`, `rt2x00pci_remove(struct pci_dev *pci_dev)`, and `extern const struct dev_pm_ops rt2x00pci_pm_ops`. It includes Linux I/O and PCI headers.

## Control Flow
Chip drivers define a `struct pci_driver`, set `.probe` to a small wrapper that passes their `struct rt2x00_ops` into `rt2x00pci_probe()`, set `.remove = rt2x00pci_remove`, and wire `.driver.pm = &rt2x00pci_pm_ops`. All real PCI resource handling is implemented in `rt2x00pci.c`.

## State And Persistence
The header owns no runtime state. It defines the compile-time interface by which chip modules share the PCI bus implementation.

## Dependencies And Integration Points
The declarations depend on `struct rt2x00_ops` from the rt2x00 core and Linux PCI/PM types. `rt61pci.c` is a direct consumer.

## Risks
Because this is only a declaration header, risks are ABI-style within the kernel tree: signature changes must be applied to all chip drivers. Missing inclusion of the matching rt2x00 core header before this header would leave `struct rt2x00_ops` undefined.

## Test Signals
Test signals are successful compilation of PCI rt2x00 drivers, module load binding through their PCI tables, remove calling the shared cleanup path, and suspend/resume symbols resolving when PM is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00queue.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00queue.c

## Purpose
`rt2x00queue.c` is the shared queue, skb, descriptor, and queue-state engine for rt2x00 devices. It allocates queue entries, prepares RX buffers, maps and unmaps DMA, builds generic TX descriptors from mac80211 metadata, handles beacon skb updates, maintains circular queue indices, starts/stops/pauses/wakes queues, and provides allocation/initialization/free helpers used by both MMIO and USB transports.

## Important APIs, Types, And Functions
Key APIs include `rt2x00queue_alloc_rxskb()`, `rt2x00queue_map_txskb()`, `rt2x00queue_unmap_skb()`, `rt2x00queue_free_skb()`, frame alignment and L2 padding helpers, `rt2x00queue_write_tx_frame()`, `rt2x00queue_clear_beacon()`, `rt2x00queue_update_beacon()`, `rt2x00queue_for_each_entry()`, `rt2x00queue_get_entry()`, `rt2x00queue_index_inc()`, queue pause/unpause/start/stop/flush helpers, `rt2x00queue_init_queues()`, `rt2x00queue_initialize()`, `rt2x00queue_uninitialize()`, `rt2x00queue_allocate()`, and `rt2x00queue_free()`. Internal descriptor builders split work into sequence generation, legacy PLCP, HT fields, crypto, and common TX flags.

## Control Flow
RX allocation computes data plus descriptor plus wireless-info size, reserves alignment and crypto head/tail room, maps DMA when `REQUIRE_DMA` is set, and stores DMA state in `struct skb_frame_desc`. TX write first builds a `struct txentry_desc` while mac80211 control data is still intact, then reclaims driver data in the skb control block, strips or copies IV/EIV as required, aligns or pads the frame, and enters `queue->tx_lock`. It refuses full queues, claims the current `Q_INDEX` entry by setting `ENTRY_OWNER_DEVICE_DATA`, writes transport-specific data, tracks BAR frames for later block-ack handling, marks data pending, advances `Q_INDEX`, lets the chip driver write the hardware descriptor, and kicks the hardware unless burst/threshold logic says to wait.

Descriptor construction interprets mac80211 flags for ACK, RTS/CTS, fragmentation, more frames, timestamp insertion, retry limits, rate mode, MCS/HT width/short GI/STBC/AMPDU, software sequence assignment, PLCP lengths, and crypto. Beacon update obtains a fresh beacon from mac80211, builds a TX descriptor, and calls the hardware driver's `write_beacon()`. Queue iteration snapshots index ranges under `index_lock`, then walks the circular span without holding the lock for callbacks. Start/stop serialize with `status_lock` and call driver `start_queue`/`stop_queue`, while mac80211 queue stop/wake is applied for AC queues.

## State And Persistence
State lives in `struct data_queue` and `struct queue_entry`: flags, `length`, `count`, `index[Q_INDEX_MAX]`, watchdog counters, WMM parameters, frame/descriptor sizes, per-entry skb pointers, private transport data, and last-action timestamps. Queue arrays are allocated as one contiguous block for RX, TX queues, beacon, and optional ATIM. RX skbs persist while queues are initialized; TX skbs belong to entries until completion or cleanup. No state survives driver removal.

## Dependencies And Integration Points
The queue layer is deeply integrated with mac80211 skb metadata, rt2x00lib DMA/TX/RX completion routines, crypto helpers, BAR tracking, debugfs frame dumps, Linux DMA APIs, and chip transport hooks such as `write_tx_data`, `write_tx_desc`, `kick_queue`, `start_queue`, `stop_queue`, `flush_queue`, `clear_entry`, `write_beacon`, and `clear_beacon`. MMIO and USB transports differ below this layer but share the queue model.

## Risks
Queue index corruption is the highest-impact risk. `Q_INDEX`, `Q_INDEX_DMA_DONE`, and `Q_INDEX_DONE` must be advanced by the correct producer/consumer path, and `queue->length` must remain consistent with ownership bits. TX setup mutates skb layout for crypto, headroom, DMA alignment, and L2 padding; mistakes break descriptors or payload parsing. Sequence generation has known comments about beacon sequence behavior and devices that cannot toggle hardware sequencing per frame. BAR tracking allocates in atomic context and intentionally degrades to failed BAR status if allocation fails. Flush may warn if hardware completion does not drain entries, and pause/wake races must remain serialized with txdone.

## Test Signals
Strong test signals include TX under all AC queues, full-queue threshold pause/wake, DMA map/unmap accounting, RX skb recycling, encrypted TX/RX with IV stripping/copying, fragmented frames, RTS/CTS and CTS-to-self, AMPDU/BAR behavior, beacon update/clear, queue start/stop during radio transitions, flush with and without drop, watchdog timeout detection through `last_action`, KASAN/KMSAN for skb headroom mutations, and lockdep coverage for `tx_lock`, `index_lock`, and `status_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00queue.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00queue.h

## Purpose
`rt2x00queue.h` defines the common queue data model and descriptor summary structures used by rt2x00 core, transports, and chip drivers. It gives all rt2x00 devices a shared vocabulary for queue IDs, skb driver metadata, RX/TX completion descriptors, TX descriptor intent, queue entries, queue indices, queue state flags, and queue iteration helpers.

## Important APIs, Types, And Functions
Important constants are `DATA_FRAME_SIZE`, `MGMT_FRAME_SIZE`, and `AGGREGATION_SIZE`. `enum data_queue_qid` maps mac80211 AC queues, management, RX, beacon, and ATIM queues. `struct skb_frame_desc` overlays mac80211 driver data and stores descriptor pointers, DMA address, IVs, TX rate reporting fields, and station pointer. `struct rxdone_entry_desc`, `struct txdone_entry_desc`, and `struct txentry_desc` are transport-neutral summaries consumed by rt2x00lib and chip drivers. `struct queue_entry` models one ring entry and `struct data_queue` models a whole queue. Inline helpers report empty/full/available/threshold status, descriptor word access, and DMA timeouts. Loop macros walk all queues or all TX queues.

## Control Flow
The header supports the queue lifecycle implemented in `rt2x00queue.c`: allocate `struct data_queue` objects, initialize each via chip `queue_init`, allocate entries with per-entry private transport data, map RX/TX skbs, and advance circular indices as hardware and software exchange ownership. `rt2x00queue_for_each_entry()` and the queue macros provide the traversal contract used by USB kicking/flushing and MMIO/chip completion paths.

## State And Persistence
Queue state is in memory only. `struct data_queue` tracks queue identity, flags, locks, count/limit/threshold/length, three circular indices, watchdog state, WMM parameters, frame and descriptor sizing, transport-specific USB endpoint metadata, and private-data size. `struct queue_entry` tracks per-slot flags, last action time, owning queue, skb, index, and transport private data. `struct skb_frame_desc` persists inside an skb while it is owned by rt2x00.

## Dependencies And Integration Points
This header integrates mac80211 metadata, Linux skb and DMA concepts, rate/cipher enums from `rt2x00reg.h`, queue users in `rt2x00queue.c`, transports in `rt2x00mmio.c` and `rt2x00usb.c`, and chip descriptor encoders such as `rt61pci_write_tx_desc()`. The descriptor read/write helpers centralize little-endian conversion for hardware descriptors.

## Risks
The skb descriptor has a build-time size assertion against `IEEE80211_TX_INFO_DRIVER_DATA_SIZE`; adding fields can break all builds. Queue index meanings must remain consistent across transports. Some macros do not bounds-check beyond their documented end pointers, so callers must choose the right range. Descriptor helpers assume little-endian descriptor words. `rt2x00queue_dma_timeout()` uses a fixed 100 ms timeout and only checks `ENTRY_OWNER_DEVICE_DATA`.

## Test Signals
Signals include compile-time size checks passing, queue allocation for drivers with and without ATIM, descriptor endian correctness in TX/RX status, queue threshold behavior, circular iteration over wraparound ranges, and successful use of the same queue structures by MMIO and USB transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00reg.h

## Purpose
`rt2x00reg.h` defines generic rt2x00 register-field infrastructure and cross-driver enum values for crypto status, antenna selection, LED modes, TSF synchronization, device power states, IFS/TXOP values, cipher IDs, rate modulation, and firmware validation errors. It is the low-level bitfield toolkit used by chip-specific register definitions and driver code.

## Important APIs, Types, And Functions
Core types are `struct rt2x00_field8`, `struct rt2x00_field16`, and `struct rt2x00_field32`, each storing a bit offset and mask. `FIELD8()`, `FIELD16()`, and `FIELD32()` validate constant masks at build time and compute offsets with compile-time first-set-bit macros. `rt2x00_set_field8/16/32()` and `rt2x00_get_field8/16/32()` write and extract values from register words with type checking. Enums define values used in descriptor and register programming, including `RX_CRYPTO_*`, `ANTENNA_*`, `LED_MODE_*`, `STATE_*`, `IFS_*`, `TXOP_*`, `CIPHER_*`, `RATE_MODE_*`, and `FW_*`.

## Control Flow
Chip register headers create field constants with `FIELD32(mask)` and driver code passes those constants to the set/get macros. This lets code modify named fields without manually shifting in every driver function. Busy-wait helpers in MMIO/USB also accept `struct rt2x00_field32` values to test hardware busy bits.

## State And Persistence
The header defines no runtime state beyond small field descriptors embedded in generated expressions. It standardizes values stored in hardware registers, firmware state, and descriptor summaries.

## Dependencies And Integration Points
It depends on kernel compile-time checks and `typecheck`. Nearly every rt2x00 source file that programs registers or descriptors depends on these enums and macros. `rt61pci.c` uses them extensively for CSR, BBP, RF, EEPROM, security, interrupt, and descriptor fields.

## Risks
The build-time field validation requires masks to be constant, non-zero, contiguous, and fit the target width. Incorrect masks fail compilation, which is useful but can surprise maintainers. `SET_FIELD` does not range-check the value before shifting, so oversized values are silently masked. The file also defines `is_power_of_two`, which can conflict conceptually with kernel helpers if included carelessly, although it is a macro local to this header usage.

## Test Signals
Test signals are successful compilation of all register definitions, sparse/typecheck coverage for wrong field widths, correct register programming in hardware traces, and no regressions in crypto, antenna, power-state, rate, or firmware error enum interpretation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00usb.c

## Purpose
`rt2x00usb.c` is the generic USB transport implementation for rt2x00 USB devices. It provides vendor control requests for register access, cached buffered register transfers, asynchronous register reads, bulk URB queue submission, RX/TX completion work, USB queue flushing and watchdog recovery, endpoint discovery, URB allocation, probe/disconnect, and PM forwarding.

## Important APIs, Types, And Functions
Exported APIs include `rt2x00usb_vendor_request()`, `rt2x00usb_vendor_req_buff_lock()`, `rt2x00usb_vendor_request_buff()`, `rt2x00usb_regbusy_read()`, `rt2x00usb_register_read_async()`, `rt2x00usb_kick_queue()`, `rt2x00usb_flush_queue()`, `rt2x00usb_watchdog()`, `rt2x00usb_disable_radio()`, `rt2x00usb_clear_entry()`, `rt2x00usb_initialize()`, `rt2x00usb_uninitialize()`, `rt2x00usb_probe()`, `rt2x00usb_disconnect()`, and PM suspend/resume when enabled. Private callbacks handle TX URB completion, RX URB completion, TX status work, RX done work, endpoint assignment, URB allocation, and register shadow allocation.

## Control Flow
Control transfers route through `rt2x00usb_vendor_request()`, which retries until timeout, treats repeated protocol/timeouts or device removal as disappearance, and clears `DEVICE_STATE_PRESENT` on fatal USB errors. Buffered register requests serialize with `csr_mutex` and chunk transfers through a kmalloc-backed `CSR_CACHE_SIZE` buffer. Async register reads allocate a control URB and callback context, anchor the URB, and optionally resubmit based on the callback return value.

TX queue kicking walks entries from `Q_INDEX_DONE` to `Q_INDEX`, clears `ENTRY_DATA_PENDING`, pads the skb to the driver-reported USB length, fills a bulk OUT URB, and submits it. TX URB completion marks IO failure on status, calls DMA done, lets chip code observe TX DMA done, and queues txdone work when no hardware TX status FIFO is required or status is available. RX kicking walks free entries, marks device ownership, calls DMA start, fills a bulk IN URB, and submits it. RX completion validates length/status, calls DMA done, and queues RX work, which passes completed entries to `rt2x00lib_rxdone()`.

Initialization finds bulk IN/OUT endpoints, assigns missing TX queues to the last discovered TX endpoint, allocates one URB per entry and optional beacon guardian URBs, and leaves queue entry setup to shared queue code. Uninitialization kills anchored async URBs, cancels timer/work, and frees all per-entry URBs. Probe resets the USB device, allocates mac80211 hardware, sets `RT2X00_CHIP_INTF_USB`, initializes work items and a USB anchor, allocates CSR/eeprom/RF storage, and calls `rt2x00lib_probe_dev()`.

## State And Persistence
USB transport state includes `rt2x00dev->csr.cache`, `eeprom`, `rf`, `anchor`, `num_proto_errs`, rxdone/txdone work items, txstatus timer, per-queue endpoint/maxpacket fields, and per-entry URBs in `struct queue_entry_priv_usb` or beacon guardian private data. State is in kernel memory and USB device state only; it is released on disconnect or uninitialize.

## Dependencies And Integration Points
The file depends on Linux USB core APIs, rt2x00 shared queue structures, rt2x00lib DMA/TX/RX completion, chip-specific `get_tx_data_len`, optional `tx_dma_done`, workqueues, hrtimers, and mac80211 hardware allocation. USB chip drivers include `rt2x00usb.h` and call `rt2x00usb_probe()` from their interface driver.

## Risks
USB buffer rules are strict: direct vendor-request buffers must be kmalloc-backed, so buffered access must be used for stack or arbitrary buffers. Fatal USB error detection clears device presence, which affects all later callbacks. URB completion and queue state must agree on ownership bits or completions can be ignored. `rt2x00usb_work_txdone()` reports unknown status unless chip-specific TX status is available. Flush loops depend on completion work draining queues within ten 50 ms sleeps. Async register reads free only the context, relying on URB lifetime rules after `usb_free_urb()` and anchoring.

## Test Signals
Signals include successful control register read/write and EEPROM reads, endpoint discovery on devices with shared or per-queue endpoints, TX bulk submission and completion under queue pressure, RX URB recycling, repeated USB protocol error handling, watchdog reset of timed-out TX DMA, flush with URB kill on drop, disconnect while URBs are in flight, suspend/resume forwarding, and no leaks from anchored async reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00usb.h

## Purpose
`rt2x00usb.h` declares the generic rt2x00 USB transport API, USB vendor request constants, register access wrappers, per-entry USB private structures, queue operations, lifecycle hooks, and USB driver entry points.

## Important APIs, Types, And Functions
Important constants include `REGISTER_TIMEOUT`, `REGISTER_TIMEOUT_FIRMWARE`, `EEPROM_TIMEOUT`, `CSR_CACHE_SIZE`, and vendor request type macros. `enum rt2x00usb_vendor_request` defines device-mode, single/multi register, EEPROM, LED, and RX control commands. `enum rt2x00usb_mode_offset` defines firmware/reset/sleep/wakeup/autoload mode offsets. Inline register helpers wrap buffered vendor requests for single and multi 32-bit reads/writes, including locked variants for callers already holding `csr_mutex`. Declared operations cover busy reads, async reads, radio disable, queue kicking/flushing/watchdog, entry clearing, initialization, uninitialization, probe/disconnect, and PM.

## Control Flow
USB chip drivers use this header to expose transport callbacks in their rt2x00lib ops. Register operations flow through vendor requests; large buffers are split through the CSR cache in `rt2x00usb.c`. Queue entries carry URBs, and beacon entries may use a larger private struct with a guardian URB when the chip requires a beacon guard byte. PM macros resolve suspend/resume to NULL when `CONFIG_PM` is disabled.

## State And Persistence
The header defines per-entry state only: `struct queue_entry_priv_usb` stores the main URB, while `struct queue_entry_priv_usb_bcn` extends it with guardian data and a guardian URB. Endpoint numbers and packet sizes are stored in `struct data_queue`, not in this header. No durable state is defined.

## Dependencies And Integration Points
It depends on Linux USB types and rt2x00 core structures. It is paired with `rt2x00usb.c` and used by USB chip drivers such as rt2500usb, rt73usb, and rt2800usb-style modules.

## Risks
The locked register helpers require `csr_mutex` to be held by convention enforced in the C file with `BUG_ON`. Buffer length must not exceed `CSR_CACHE_SIZE` for the locked cached path. The beacon private struct intentionally begins with the same layout as the generic USB private struct; changing field order would break casts in queue code. PM declarations differ by config, so users must use the provided macros.

## Test Signals
Signals include compilation of USB chip drivers, correct vendor request constants in bus traces, register access under locked and unlocked paths, beacon guardian URB allocation when required, PM builds with and without `CONFIG_PM`, and endpoint queue operations resolving through the declared API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt61pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt61pci.c

## Purpose
`rt61pci.c` is the chip-specific PCI/PCMCIA driver for Ralink RT2561, RT2561s, and RT2661 devices. It binds the generic rt2x00 PCI, MMIO, queue, mac80211, firmware, EEPROM, RF, LED, link tuning, interrupt, and descriptor frameworks to this hardware family by supplying register programming and operation tables.

## Important APIs, Types, And Functions
The module exposes a PCI driver through `module_pci_driver(rt61pci_driver)`. Its main operation tables are `rt61pci_mac80211_ops`, `rt61pci_rt2x00_ops`, and `rt61pci_ops`. Important helper groups include indirect BBP/RF/MCU access (`rt61pci_bbp_read/write`, `rt61pci_rf_write`, `rt61pci_mcu_request`), EEPROM access and validation, LED callbacks, crypto key programming, filter/interface/ERP/antenna/channel/power/retry/PS configuration, link statistics and tuning, queue start/kick/stop, firmware name/check/load, ring/register/BBP initialization, device state transitions, descriptor writers, RX descriptor decoding, TX status handling, interrupt/tasklet handlers, hardware probing, WMM configuration, TSF reading, queue sizing, and PCI id registration.

## Control Flow
Probe enters through the module PCI wrapper and generic `rt2x00pci_probe()`, which eventually calls `rt61pci_probe_hw()`. Hardware probe disables power saving, reads EEPROM through a 93cx6 bit-banged interface, validates and normalizes missing EEPROM words, initializes chip/RF/capability/default antenna/frequency/LNA/LED state, enables rfkill GPIO direction, builds supported band/rate/channel/power specifications, and sets capabilities such as firmware requirement, DMA, optional hardware crypto, control filters, and link tuning.

Firmware loading selects one of three firmware filenames from the PCI device id, requires an 8192-byte image with an ITU-T CRC over the data plus two zero bytes, resets MCU/mailboxes, writes the image to firmware memory, waits for MCU ready, and resets MAC/BBP with host-ready set. Radio-on state initializes DMA rings, base registers, BBP defaults and EEPROM BBP overrides, then enables RX DMA. Runtime mac80211 callbacks mostly use `rt2x00mac.c`; chip-specific `conf_tx` first updates shared queue WMM values then writes TXOP/AIFSN/CWMIN/CWMAX registers.

TX uses generic queue descriptor intent from `rt2x00queue.c` and encodes RT61 TXD words in `rt61pci_write_tx_desc()`. Word 0 is written last to avoid hardware consuming a partially updated descriptor. Beacon writing disables beacon generation, writes a TXINFO descriptor and padded beacon body into the selected hardware beacon memory, programs TBTT adjustment, restores beacon generation, and frees the temporary beacon skb. RX completion decodes CRC, cipher status, IV/ICV, RSSI, signal type, size, and BSS ownership from RXD words. Interrupts acknowledge source registers, schedule RX/TX/beacon/autowake tasklets, mask scheduled interrupt bits, and let each tasklet re-enable its interrupt after processing.

## State And Persistence
State spans EEPROM shadow data, RF shadow registers, `rt2x00dev` chip/capability flags, LED MCU register image, LNA gain, frequency offset, TX power, current band, interface counters from the common layer, queue descriptors and DMA ring base registers, hardware key valid bits in `SEC_CSR2/3`, beacon memory, firmware MCU state, interrupt masks, and link quality tuner fields. EEPROM normalization writes only the kernel shadow via `rt2x00_eeprom_write()` during validation; hardware persistence depends on the lower EEPROM helper behavior elsewhere.

## Dependencies And Integration Points
This driver depends on Linux PCI, mac80211, eeprom_93cx6, CRC ITU-T, rt2x00 core/lib/mac/queue/mmio/pci helpers, `rt61pci.h` register definitions, firmware blobs `rt2561.bin`, `rt2561s.bin`, and `rt2661.bin`, optional debugfs and LED support, and MMIO DMA descriptor rings. It is a direct consumer of `rt2x00mac.c`, `rt2x00mmio.c`, `rt2x00pci.c`, `rt2x00queue.c`, and `rt2x00reg.h`.

## Risks
Hardware sequencing is fragile. BBP/RF/MCU indirect access depends on busy bits and `csr_mutex`; failures produce `0xff` reads or skipped writes. Firmware length/CRC/ready checks can fail before the device is usable. EEPROM defaults prevent invalid values but may hide bad calibration. Pairwise key allocation scans two valid-bit registers and relies on `hw_key_idx`; shared keys are deliberately unsupported because hardware decryption is unreliable. Descriptor programming must write owner/valid bits last. TX status FIFO processing can miss entries and reports skipped entries as unknown. Interrupt masking must be paired with tasklet re-enable or RX/TX stalls. Antenna/RF programming has chip-specific FIXME behavior for RF2529 diversity. Power-save/autowake touches MAC, PCI usec, soft reset, and MCU commands in exact order.

## Test Signals
Test RT2561, RT2561s, and RT2661 PCI IDs through probe, firmware load, radio on/off, suspend/resume, rfkill, 2.4 GHz and 5 GHz channels where supported, EEPROM fallback paths, hardware crypto pairwise keys, software fallback for shared keys, WMM queue configuration, beacon generation for up to four AP interfaces, TX status and retry reporting, RX decrypt/error/RSSI reporting, link tuner VGC changes, interrupt storms and re-enable behavior, autowake from power save, and remove with tasklets/IRQ/DMA rings quiesced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt61pci.c -->
