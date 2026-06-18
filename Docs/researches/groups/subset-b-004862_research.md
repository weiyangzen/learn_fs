# Research: subset-b-004862

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/regs.h

## Purpose
Defines the MT7996/MT7992/MT7990 register-address vocabulary used by the mt7996 driver. It is a pure hardware contract header: no executable control flow, but a large set of macros that translate driver concepts such as per-band MAC blocks, WFDMA rings, RRO queues, MIB counters, interrupt masks, remap windows, LED controls, firmware state, PCIe MAC, and PHY/RF diagnostic blocks into MMIO addresses and bitfields.

## Important APIs, Types, And Functions
The important types are `struct __map`, `struct __base`, and `struct mt7996_reg_desc`, which let runtime chip-specific tables describe base addresses, remap windows, and offset revisions. `enum base_rev` names per-band base blocks such as AGG, ARB, TMAC, RMAC, DMA, WTBLOFF, ETBF, LPON, MIB, and RATE. `enum offs_rev` names revision-dependent offsets for MIB counters, HIF remap registers, WTBL control registers, and chip-specific address ends. Macros such as `MT_WF_TMAC()`, `MT_WF_MIB()`, `MT_RXQ_RING_BASE()`, and `MT_INT_RX_DONE_ALL` are integration points for reset, DMA, interrupt, statistics, debug, and RRO code.

## Control Flow
There is no runtime control flow. Consumers populate `dev->reg` from a chip descriptor, then these macros fold band id, queue id, offset-revision id, and WFDMA mask state into concrete addresses. DMA setup reads queue ids through `MT_Q_ID()` and chooses WFDMA0/WFDMA1 through `MT_Q_BASE()`. Interrupt handlers combine queue-specific masks through `MT_INT_RX()` and `MT_INT_TX_MCU()`. Statistics paths use the MIB macros, with comments marking counters that should not be read directly because firmware may own their clear-on-read semantics.

## State And Persistence
The header describes persistent hardware state rather than owning memory itself. State lives in chip registers: RRO address tables and ACK windows, PLE page counts, MDP header translation, TMAC timing, WTBL updates, RMAC filters, WFDMA global configuration, interrupt source/mask CSRs, MCU command/status bits, firmware assertion state, LED blink controls, low-power ownership, ADIE identity, and PHYRX diagnostic counters. Revision indirection is persistent per device through `dev->reg.base` and `dev->reg.offs_rev`.

## Dependencies And Integration Points
Depends on mt76/mt7996 device structures exposing `dev->reg`, queue id arrays, queue interrupt masks, WFDMA masks, and band count definitions. It integrates with the mt7996 DMA, MMIO, MCU recovery, SER, debugfs, statistics, LED, PCIe, WED/RRO, and PHY code. The macros rely heavily on Linux `BIT`, `GENMASK`, and `FIELD_PREP/FIELD_GET` conventions.

## Risks
The main risk is silent address drift across chip revisions. A wrong base, remap offset, queue id, or interrupt mask can corrupt unrelated registers, lose interrupts, or break recovery. MIB clear-on-read comments matter: reading firmware-owned counters can destroy statistics. RRO and WFDMA macros are tightly coupled to queue enumeration; changing queue ordering without updating this header can route DMA to the wrong ring.

## Test Signals
Useful signals are successful probe on all supported mt7996-family chips, WFDMA ring setup, interrupt delivery per RX/TX/MCU queue, firmware recovery state transitions, RRO queue operation, accurate MIB accumulation, LED control, low-power ownership changes, PCIe1 dual-HIF operation, and debug register reads that match expected hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/npu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/npu.c

## Purpose
Implements Airoha NPU/PPE offload support for mt76 MMIO devices. It provides NPU RX queue provisioning, NAPI polling, IRQ handling, TX descriptor filling for NPU-backed queues, queue register handoff, traffic-control offload callbacks, firmware address notification, IRQ masking, and lifecycle attach/detach of the external `airoha-npu` and `airoha-eth` devices.

## Important APIs, Types, And Functions
Key exported entry points are `mt76_npu_init()`, `mt76_npu_deinit()`, `mt76_npu_rx_queue_init()`, `mt76_npu_dma_add_buf()`, `mt76_npu_txdesc_cleanup()`, `mt76_npu_queue_setup()`, `mt76_npu_check_ppe()`, `mt76_npu_net_setup_tc()`, `mt76_npu_send_txrx_addr()`, and `mt76_npu_disable_irqs()`. Internal helpers manage RX page-pool descriptors (`mt76_npu_fill_rx_queue()`), descriptor cleanup, SKB assembly (`mt76_npu_dequeue()`), NAPI polling, IRQ acknowledgment/disable, and TC flower block binding through PPE callbacks.

## Control Flow
Initialization obtains NPU and PPE devices, requesting modules if needed, initializes reserved NPU memory, switches `dev->dma_dev` to the NPU device, stores physical address/type metadata, enables hardware RRO mode, expands RX token space, and publishes NPU/PPE pointers under RCU. RX queue init allocates NPU descriptor rings through the existing queue ops, requests the NPU IRQ, adds NAPI, fills RX buffers, and enables NAPI. IRQ handling acknowledges and disables the NPU queue IRQ, then schedules NAPI. NAPI drains completed descriptors into SKBs, passes them to `drv->rx_skb()`, refills descriptors, and notifies driver RX completion.

## State And Persistence
State is held in `dev->mmio.npu`, `dev->mmio.ppe_dev`, `dev->mmio.phy_addr`, `dev->mmio.npu_type`, `dev->hwrro_mode`, `dev->rx_token_size`, NPU RX queue flags/descriptors, queue `wed_regs`, NAPI slots, page-pool buffers, and RCU-protected PPE/NPU references. RX descriptor ownership persists between NPU hardware, page pool, and mt76 queue head/tail indexes.

## Dependencies And Integration Points
Depends on Airoha NPU/PPE APIs, Linux NAPI, TC flower offload, flow block callbacks, page-pool DMA metadata, mt76 DMA queue ops, WED/NPU queue flags, mt76 driver RX callbacks, and RCU/mutex lifetime rules. It also assumes HW-RRO is available because the NPU offload path requires hardware packet reordering.

## Risks
Descriptor ownership is sensitive: failed NAPI SKB construction, missing DONE bits, or bad multi-frame counts can leak page-pool buffers or stall the queue. `mt76_npu_dma_add_buf()` notes that non-linear SKBs are not yet handled. RCU pointer replacement must pair with queue cleanup so IRQ/NAPI paths do not use freed NPU/PPE devices. TC block lifetime uses a static callback list and must bind/unbind cleanly across netdev teardown.

## Test Signals
Probe with and without loadable `airoha-npu`/`airoha-eth`, RX queue init for both NPU queues, IRQ-to-NAPI delivery, RX refill after budget exhaustion, PPE hash/reason handling, TC flower bind/unbind, offloaded TX descriptor cleanup, device reset/deinit while IRQs are quiet, and page-pool/dma debug checks for leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/npu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/pci.c

## Purpose
Provides small shared PCIe ASPM helpers for mt76 PCI drivers. The file lets chip drivers detect whether ASPM is active and force-disable L0s/L1 link power states when hardware or firmware requires more stable PCIe latency.

## Important APIs, Types, And Functions
`mt76_pci_disable_aspm()` reads the device and parent link-control ASPM fields, logs the active ASPM modes, calls `pci_disable_link_state()` when PCIEASPM core support is available, and falls back to clearing device and parent `PCI_EXP_LNKCTL` ASPM bits. `mt76_pci_aspm_supported()` returns whether either endpoint or upstream link currently advertises active ASPM bits.

## Control Flow
Both helpers read the device link-control register and, when present, the parent bridge link-control register. Disable exits early if neither side has ASPM enabled. Otherwise it tries the kernel PCIe ASPM API first; only if that fails or is unavailable does it directly clear ASPM bits in the downstream component then upstream component.

## State And Persistence
The only persistent state affected is PCIe link-control configuration in the endpoint and parent bridge. No mt76-private state is stored.

## Dependencies And Integration Points
Depends on Linux PCIe capability helpers, `pci_disable_link_state()`, `CONFIG_PCIEASPM`, and callers in PCI mt76 chip drivers that decide when ASPM must be disabled or probed.

## Risks
Directly clearing parent/device ASPM bits can affect power behavior beyond the mt76 function. Parent and child settings must remain consistent. The helper only considers current L0s/L1 bits, not policy state or platform firmware expectations.

## Test Signals
Driver probe on PCIe devices with ASPM enabled/disabled, logs showing disabled L0s/L1, stable DMA and firmware command behavior after disabling, and no PCIe AER/link errors or suspend/resume regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/scan.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/scan.c

## Purpose
Implements shared software-driven hardware-scan orchestration for mt76 PHYs. It serializes one scan request, switches channels, sends probe requests, waits for passive-channel beacons when required, restores the main channel, and reports completion to mac80211.

## Important APIs, Types, And Functions
Exported callbacks are `mt76_hw_scan()`, `mt76_cancel_hw_scan()`, `mt76_abort_scan()`, and `mt76_scan_rx_beacon()`. The central worker is `mt76_scan_work()`. `mt76_scan_complete()` restores channel/offchannel state and calls `ieee80211_scan_completed()`. `mt76_scan_send_probe()` builds probe requests with scan IEs, optional BSSID targeting, no-CCK flag handling, and mt76 TX queueing through the scan vif link WCID.

## Control Flow
`mt76_hw_scan()` selects the correct PHY for multi-radio hardware, rejects concurrent scan/ROC/reset, takes a vif phy link, records the scan request, and schedules work immediately. Each worker run clears beacon-wait state, advances through requested channels, toggles offchannel notification, sets the channel, optionally waits for a beacon on no-IR/radar channels, sends probes for active channels, and reschedules itself for dwell time. Completion or abort restores the main channel and drops the held vif link.

## State And Persistence
Scan state lives in `dev->scan`: request pointer, vif, phy, channel index, current channel, beacon wait/received flags, and `mlink`. The PHY `MT76_SCANNING` bit, `phy->offchannel`, and main channel definition are coordinated with this state. It is transient and explicitly zeroed at completion.

## Dependencies And Integration Points
Integrates with mac80211 scan callbacks, cfg80211 scan request data, mt76 channel-setting helpers, offchannel notifications, vif-link reference helpers, the shared TX path, `scan_lock`, delayed work, and MCU reset state.

## Risks
Race risks center on aborts, beacon wakeups, and reset. The code must avoid completing scans during MCU reset, must restore the main channel after offchannel dwell, and must not use a released vif link. Probe generation assumes `ieee80211_tx_prepare_skb()` succeeds under RCU; failures drop the SKB without more recovery.

## Test Signals
Active and passive scan across 2/5/6 GHz channels, abort while offchannel, scan during association with stations present, multi-radio band selection, no-CCK probe behavior, BSSID-directed scans, reset during scan, and confirmation that queues and channel state return to normal afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/sdio.c

## Purpose
Provides the shared SDIO bus implementation for mt76 devices. It handles SDIO register access before and after MCU startup, hardware ownership/interrupt initialization, queue allocation, TX/RX queue ops, TX status workers, RX delivery workers, and SDIO worker lifecycle.

## Important APIs, Types, And Functions
Exported register/bus APIs include `mt76s_rr()`, `mt76s_wr()`, `mt76s_rmw()`, `mt76s_read_copy()`, `mt76s_write_copy()`, `mt76s_wr_rp()`, `mt76s_rd_rp()`, `mt76s_read_pcr()`, and `mt76s_hw_init()`. Queue/lifecycle APIs include `mt76s_alloc_rx_queue()`, `mt76s_alloc_tx()`, `mt76s_init()`, and `mt76s_deinit()`. Queue ops are `mt76s_tx_queue_skb()`, `mt76s_tx_queue_skb_raw()`, and `mt76s_tx_kick()`.

## Control Flow
Before MCU startup, register reads/writes use mailbox handshakes through H2D/D2H registers and WHISR polling. After MCU startup they delegate to `mcu_ops`. `mt76s_hw_init()` enables the SDIO function, claims driver ownership, sets block size, enables interrupts, configures WHIER/WHCR per SDIO generation, and claims the SDIO IRQ. Runtime TX queueing prepares SKBs, appends entries, and schedules the SDIO TX/RX worker. Status workers retire completed queue entries, fetch driver TX status data, wake waiters, and reschedule the generic TX worker when data queues drain.

## State And Persistence
State lives in `dev->sdio`: `func`, `hw_ver`, `xmit_buf`, `xmit_buf_sz`, scheduler quotas, SDIO worker threads, and status/stat workers. Queue state lives in `dev->q_rx`, `dev->phy.q_tx[]`, and `dev->q_mcu[MT_MCUQ_WM]`. Hardware state includes SDIO ownership, interrupt enable bits, block size, mailbox contents, and WHCR aggregation mode.

## Dependencies And Integration Points
Depends on Linux MMC/SDIO APIs, mt76 worker helpers, mt76 queue ops, MCU register access methods, driver `tx_prepare_skb()` and `tx_status_data()` callbacks, SDIO register definitions in `sdio.h`, and `mt76s_txrx_worker()`/IRQ handling in `sdio_txrx.c`.

## Risks
Mailbox register access has timeout and mismatch failure modes. Queue entry publication relies on memory barriers before bus access. Raw MCU SKBs are freed differently from data SKBs. Deinit must stop all workers, flush pending TX status, release SDIO IRQ under host claim, and free queued RX SKBs; ordering mistakes can cause use-after-free or stalled SDIO IRQs.

## Test Signals
SDIO probe on CONNAC and CONNAC2 devices, driver ownership acquisition, interrupt delivery, register access both before and after MCU startup, TX/RX queue activity, suspend/reset paths with `MT76_MCU_RESET`, clean deinit, and no stuck `tx_wait` or `MT76_READING_STATS` bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/sdio.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/sdio.h

## Purpose
Defines shared SDIO register offsets, bitfields, generation identifiers, and interrupt metadata used by mt76 SDIO bus code. It is the hardware description companion to `sdio.c` and `sdio_txrx.c`.

## Important APIs, Types, And Functions
The header defines ownership and interrupt registers such as `MCR_WHLPCR`, `MCR_WHISR`, `MCR_WHIER`, mailbox registers, RX packet-length registers, TX queue quota registers, read/write data ports, and CONNAC2-only reset/extended queue registers. `enum mt76_connac_sdio_ver` distinguishes CONNAC and CONNAC2 behavior. `struct mt76s_intr` is the parsed interrupt payload consumed by TX/RX scheduling.

## Control Flow
There is no executable control flow. Consumers use the constants to claim host ownership, enable/disable interrupts, clear WHISR bits, parse RX lengths, update scheduler quotas from WTQCR fields, and choose SDIO-generation-specific aggregation fields.

## State And Persistence
The header describes persistent SDIO function state: host/firmware ownership, interrupt masks/status, mailbox values, queue counters, data ports, RX aggregation mode, reset bits, and per-queue quota counters. `struct mt76s_intr` transiently represents an interrupt snapshot.

## Dependencies And Integration Points
Depends on Linux `BIT`, `GENMASK`, and bitfield conventions. It is included by mt76 SDIO register, IRQ, and TX/RX code, and by chip-specific SDIO drivers that supply `parse_irq()` callbacks.

## Risks
Wrong field selection between CONNAC and CONNAC2 can break ownership, RX aggregation, or queue accounting. The duplicated bit meaning around `WHLPCR_FW_OWN_REQ_SET` and `WHLPCR_IS_DRIVER_OWN` requires careful use by callers.

## Test Signals
Correct parsed ISR bits, RX0/RX1 packet lengths, TX quota refill values, ownership transitions, and reset/interrupt behavior on both CONNAC and CONNAC2 SDIO hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/sdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/sdio_txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/sdio_txrx.c

## Purpose
Implements the active SDIO TX/RX datapath worker and IRQ entry point. It drains mt76 TX queues into SDIO write bursts, reads RX packets described by parsed interrupt metadata, accounts PSE/PLE/MCU quotas, and coordinates suspend/reset waits.

## Important APIs, Types, And Functions
Exported functions are `mt76s_txrx_worker()`, `mt76s_sdio_irq()`, and `mt76s_txqs_empty()`. Internal helpers include `mt76s_refill_sched_quota()`, `mt76s_rx_run_queue()`, `mt76s_rx_handler()`, `mt76s_tx_pick_quota()`, `mt76s_tx_update_quota()`, `__mt76s_xmit_queue()`, and `mt76s_tx_run_queue()`.

## Control Flow
The SDIO IRQ disables interrupts and schedules `txrx_worker`. The worker disables interrupts, repeatedly runs data TX queues, the MCU TX queue, and RX handling until no frames or quota updates remain, then re-enables interrupts. RX handling calls the chip-specific `parse_irq()`, reads RX0/RX1 blocks from `MCR_WRDR(qid)`, splits packets by RX descriptor length, builds SKBs, publishes them to RX queues, and schedules `net_worker`. TX handling batches entries into `sdio->xmit_buf`, respecting firmware-running state, block-size padding, transmit quotas, and MCU reset state.

## State And Persistence
Persistent runtime state includes SDIO scheduler quotas (`pse_mcu_quota`, `pse_data_quota`, `ple_data_quota`, page size, deficit), queue head/first/tail indexes, per-entry `done` flags, shared transmit buffer contents, and `bus_hung`. RX pages are transiently allocated per read and SKBs hold page references for fragments.

## Dependencies And Integration Points
Depends on `sdio.h` registers, chip-specific IRQ parsing, Linux SDIO block I/O, mt76 queue and worker infrastructure, driver `rx_check()` and `rx_skb()` callbacks, tracepoints, MCU/reset state bits, and `mt76_skb_adjust_pad()` for raw TX padding.

## Risks
Quota accounting can stall TX if interrupts do not refill counts or if PSE/PLE sizes are miscomputed. RX aggregation parsing trusts descriptor lengths after validation; malformed data can drop frames or set `bus_hung`. Worker interrupt masking must always be paired with re-enable. Queue pointer barriers are required so bus access sees complete entries.

## Test Signals
Sustained bidirectional traffic, MCU command TX before and after firmware start, RX0/RX1 delivery, quota exhaustion/recovery, suspend and MCU reset waits, injected SDIO read/write errors setting `bus_hung`, and no lost interrupts after worker exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/sdio_txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/testmode.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/testmode.c

## Purpose
Implements shared nl80211 testmode handling for mt76 PHY manufacturing/calibration tests. It parses test attributes, tracks per-PHY test parameters, allocates synthetic TX frames, starts/stops finite test transmissions, reports TX/RX stats, and delegates hardware-specific state/parameter programming to chip `test_ops`.

## Important APIs, Types, And Functions
Exports `mt76_tm_policy`, `mt76_testmode_alloc_skb()`, `mt76_testmode_tx_pending()`, `mt76_testmode_set_state()`, `mt76_testmode_cmd()`, and `mt76_testmode_dump()`. Important helpers validate rate/length parameters, compute max MPDU length by PHY mode, build fragmented SKBs for large MPDUs, track which netlink parameters were present, initialize defaults, and dump common TX/RX counters.

## Control Flow
`mt76_testmode_cmd()` parses attributes, handles reset, initializes defaults, updates fields, validates bounds, calls driver `set_params()`, records present parameters, and optionally changes state. State changes first stop active TX, then initialize TX if entering `TX_FRAMES`, call driver `set_state()`, start TX scheduling, or clear RX stats. `mt76_testmode_tx_pending()` is called from the generic TX worker to clone the prepared SKB into hardware queues until count, queue, or queued-limit constraints stop it.

## State And Persistence
Per-PHY state lives in `phy->test`: current state, TX count/length/rate/antenna/power/frequency parameters, MAC addresses, `param_set` bitmap, `tx_skb`, pending/queued/done counters, RX stats, and optional MTD metadata. It is reset by `MT76_TM_ATTR_RESET` and transiently interacts with `dev->tx_wait`.

## Dependencies And Integration Points
Depends on nl80211 testmode netlink, mac80211 TX status, mt76 TX queue ops, mt76 test hooks, random payload generation, monitor-mode requirement for active test states, and optional `CONFIG_NL80211_TESTMODE` handling in the TX completion path.

## Risks
Parameter validation must match PHY capabilities; wrong NSS/rate/length acceptance can build invalid frames. TX stop disables the generic TX worker and waits for done counters, so completion accounting must be exact. Large MPDU fragmentation manually adjusts SKB length/data_len and is sensitive to allocation failure. Some HE-related modes are passed to driver code rather than fully validated here.

## Test Signals
Netlink set/dump round trips, reset to defaults, TX_FRAMES with finite counts and queued limits, RX_FRAMES stats accumulation, invalid parameter rejection, test mode blocked when device is not running or not in monitor mode, and no SKB leaks after stop or allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/testmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/testmode.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/testmode.h

## Purpose
Defines the mt76 nl80211 testmode ABI shared by mt76 drivers and user space. It enumerates command attributes, statistics attributes, RX detail attributes, test states, and TX PHY modes.

## Important APIs, Types, And Functions
Important enums are `mt76_testmode_attr`, `mt76_testmode_stats_attr`, `mt76_testmode_rx_attr`, `mt76_testmode_state`, and `mt76_testmode_tx_mode`. `MT76_TM_TIMEOUT` controls common wait timing, and `mt76_tm_policy[]` is declared for the parser in `testmode.c`.

## Control Flow
No executable flow. The enum order defines netlink attribute numbers and therefore is ABI-sensitive. Parser and dumper code use these ids to validate attributes, fill `phy->test`, and emit stats.

## State And Persistence
The header defines externally visible state names such as OFF, IDLE, TX_FRAMES, RX_FRAMES, TX_CONT, and ON. It also defines persistent parameter ids for MTD source, TX count/length/rate/power/timing, frequency offset, driver-specific nested data, and MAC addresses.

## Dependencies And Integration Points
Depends on netlink headers and is included by mt76 core and chip-specific testmode implementations. User-space tools must match the enum values.

## Risks
Reordering existing enum entries would break the ABI. Documentation comments contain a minor duplicated `TX_QUEUED` wording issue for `TX_DONE`, so readers should trust the enum names. New attributes must be appended before the `NUM_*` sentinel.

## Test Signals
ABI compatibility with existing testmode tools, successful parsing of all listed attributes, nested TX power/MAC address handling, and correct dump formatting for common stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/testmode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/trace.c

## Purpose
Instantiates the generic mt76 tracepoints declared in `trace.h` and exports selected tracepoint symbols for use by mt76 modules.

## Important APIs, Types, And Functions
The file defines `CREATE_TRACE_POINTS`, includes `trace.h`, and exports `mac_txdone` and `dev_irq` tracepoint symbols with GPL visibility. It excludes sparse/checker builds through `#ifndef __CHECKER__`.

## Control Flow
No runtime control flow beyond tracepoint registration produced by the trace subsystem at compile/load time.

## State And Persistence
Tracepoint metadata is registered with the kernel tracing subsystem. No mt76 device state is stored here.

## Dependencies And Integration Points
Depends on Linux tracepoint infrastructure, `trace.h`, module support, and consumers in mt76 code that call `trace_mac_txdone()`, `trace_dev_irq()`, `trace_reg_rr()`, or `trace_reg_wr()`.

## Risks
Only one C file may define `CREATE_TRACE_POINTS` for this trace header. Include path settings in the build must let `trace/define_trace.h` locate `trace.h`.

## Test Signals
Successful module build/load, visible mt76 trace events under ftrace/perf, and no duplicate tracepoint definition link errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/trace.h

## Purpose
Declares generic mt76 tracepoints for register reads/writes, IRQ status, and TX completion identifiers. These are low-overhead instrumentation hooks used across mt76 bus and chip code.

## Important APIs, Types, And Functions
Defines event classes `dev_reg_evt` and `dev_txid_evt`, concrete events `reg_rr`, `reg_wr`, `dev_irq`, and `mac_txdone`, and shared formatting macros for wiphy name, register/value pairs, and WCID/packet id pairs.

## Control Flow
No driver control flow. The trace macros generate tracepoint call sites and record assignments when a tracepoint is enabled. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` direct `define_trace.h` to this header.

## State And Persistence
Trace records persist only in the kernel tracing buffers. Each record carries the wiphy name plus event-specific register, value, mask, WCID, or packet id fields.

## Dependencies And Integration Points
Depends on Linux tracepoint infrastructure and `mt76.h` for `struct mt76_dev`. It is used by generic mt76 code and bus/datapath code to diagnose register access, interrupts, and TX status.

## Risks
Trace event field layout is user-visible to tracing tools. Renaming events or changing field meanings can break diagnostics. The fixed 32-byte wiphy name buffer truncates longer names by design.

## Test Signals
Events appear under `/sys/kernel/tracing/events/mt76`, can be enabled individually, and show correct wiphy/register/IRQ/TX id data during traffic and interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/tx.c

## Purpose
Implements the shared mt76 transmit scheduler, TX status tracking, power-save frame release, pending/offchannel queues, AQL backpressure fallback, hardware queue blocking, token management, and common queue-completion helpers.

## Important APIs, Types, And Functions
Major exports include `mt76_tx()`, `mt76_wake_tx_queue()`, `mt76_txq_schedule_all()`, `mt76_tx_worker_run()`, `mt76_release_buffered_frames()`, `__mt76_tx_complete_skb()`, TX status helpers (`mt76_tx_status_*`), `mt76_stop_tx_queues()`, `mt76_queue_tx_complete()`, token APIs (`mt76_token_consume()`, `mt76_token_release()`, RX token variants), `mt76_ac_to_hwq()`, `mt76_skb_adjust_pad()`, and `__mt76_set_tx_blocked()`.

## Control Flow
mac80211 or chip code queues SKBs through `mt76_tx()` or iTXQ wakeups. The worker drains pending WCID queues first, then schedules mac80211 TXQs per AC. Burst scheduling dequeues frames, gets rates when needed, checks PS/reset/offchannel/AQL limits, calls bus-specific `queue_ops->tx_queue_skb()`, and kicks hardware. Completion either reports immediate status or waits for both DMA_DONE and TXS_DONE via IDR packet ids. Status timeout/flush paths mark missing TXS as failed or ACKed depending on driver flags.

## State And Persistence
State spans per-WCID pending/offchannel queues, `tx_list`, `non_aql_packets`, packet-id IDRs, `wcid_list`, queue head/tail/queued counts, queue blocked/stopped flags, per-PHY TX lists, `mgmt_tx_pending`, token IDRs, token counts, WED token counts, and TX callback flags embedded in SKBs.

## Dependencies And Integration Points
Integrates with mac80211 TXQs, sta/vif status APIs, mt76 queue ops for USB/SDIO/MMIO, WED offload token ranges, testmode, RCU WCID lookup, driver `tx_complete_skb()`, and the mt76 worker framework.

## Risks
The highest risks are lifetime and accounting bugs: SKBs must be reported once, IDR packet ids removed, non-AQL counters balanced, queue locks respected, and token blocking lifted when enough tokens return. Offchannel and management queue decisions affect association and ROC correctness. WED packet-id shortcuts and unreliable TXS fallback can hide real firmware status failures.

## Test Signals
High-throughput TX, per-AC scheduling fairness, PS release EOSP behavior, aggregation BAR generation, offchannel management TX, testmode TX completion, TX status timeout/flush, WED active/inactive operation, token exhaustion/unblock, reset while queues are non-empty, and lockdep/KASAN coverage around status callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/usb.c

## Purpose
Provides the shared mt76 USB bus implementation: vendor control requests, register access, bulk RX/TX URB management, optional scatter-gather RX/TX, queue allocation, TX status workers, stop/resume/deinit helpers, and USB bus ops registration.

## Important APIs, Types, And Functions
Exports vendor/register helpers (`__mt76u_vendor_request()`, `mt76u_vendor_request()`, `___mt76u_rr()`, `___mt76u_wr()`, `mt76u_read_copy()`, `mt76u_single_wr()`), queue APIs (`mt76u_alloc_queues()`, `mt76u_alloc_mcu_queue()`, `mt76u_stop_rx()`, `mt76u_resume_rx()`, `mt76u_stop_tx()`, `mt76u_queues_deinit()`), and init APIs (`__mt76u_init()`, `mt76u_init()`). Queue ops are `mt76u_tx_queue_skb()` and `mt76u_tx_kick()`.

## Control Flow
Register access serializes through `usb_ctrl_mtx` and retries vendor control messages, marking the device removed on ENODEV/EPROTO. Init allocates the control buffer, sets bus/queue ops, records USB drvdata, detects scatter-gather support, discovers endpoints, and starts RX/status workers. RX URBs complete into queue entries, schedule `rx_worker`, are parsed into SKBs/frags, passed to `drv->rx_skb()`, refilled, and resubmitted. TX prepares SKBs, fills bulk URBs, submits pending URBs, completes via status worker, and optionally polls firmware TX status data.

## State And Persistence
State lives in `dev->usb`: endpoint arrays, control buffer, mutex, SG enable, RX/status workers, stat work, and URBs stored in queue entries. Queue state tracks `head`, `tail`, `first`, `queued`, `done`, endpoint mapping, and page-pool buffers. Module parameter `disable_usb_sg` persistently controls SG use.

## Dependencies And Integration Points
Depends on Linux USB core, page_pool, scatterlist helpers, mt76 worker and queue APIs, mt76 DMA header constants, driver callbacks `tx_prepare_skb()`, `rx_skb()`, `rx_check()`, and `tx_status_data()`, plus USB tracepoints.

## Risks
URB ownership and page-pool recycling are delicate, especially with SG RX where an SKB may own multiple pages. Stop paths must poison/kill URBs and manually complete queued SKBs after removal. Vendor requests log writes even for some non-register control operations. Endpoint mapping has chip-specific cases; wrong mapping can route PSD/AC traffic incorrectly.

## Test Signals
Probe on supported USB chips, SG enabled/disabled operation, RX aggregation and fragmented SKBs, TX queue drain, MCU RX queue allocation, suspend/resume RX, removal during TX submission, vendor request timeout handling, and visible `mt76_usb` trace events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/usb_trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/usb_trace.c

## Purpose
Instantiates USB-specific mt76 tracepoints declared in `usb_trace.h`.

## Important APIs, Types, And Functions
Defines `CREATE_TRACE_POINTS` and includes `usb_trace.h` under `#ifndef __CHECKER__`. No explicit symbols are exported in this file; tracepoint definitions are generated by the tracing infrastructure.

## Control Flow
No runtime driver flow. Loading the object registers the USB tracepoint definitions generated from the header.

## State And Persistence
Trace metadata persists in the kernel tracing subsystem. No device state is stored by this file.

## Dependencies And Integration Points
Depends on Linux module and tracepoint infrastructure, `usb_trace.h`, and build flags that add the source directory to trace include resolution.

## Risks
Duplicate `CREATE_TRACE_POINTS` definitions would cause link errors. Missing include path would prevent trace generation.

## Test Signals
Successful build/load and visible `mt76_usb` trace events for register access, URB submission, and RX URB completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/usb_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/usb_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/usb_trace.h

## Purpose
Declares mt76 USB tracepoints for vendor-register reads/writes and URB transfer activity.

## Important APIs, Types, And Functions
Defines event class `dev_reg_evt` and events `usb_reg_rr` and `usb_reg_wr`. Defines event class `urb_transfer` and events `submit_urb` and `rx_urb`. Each record includes a wiphy name plus register/value or URB pipe/length fields.

## Control Flow
No executable control flow. USB code emits these tracepoints around control-message register access and URB submission/completion.

## State And Persistence
Trace records persist in tracing buffers only. URB records capture pipe and transfer length, not payload data.

## Dependencies And Integration Points
Depends on Linux tracepoints, `mt76.h`, and `usb_trace.c` for instantiation. Used heavily by `usb.c`.

## Risks
Event names and field formats are diagnostic ABI for trace tooling. The fixed 32-byte wiphy field can truncate names.

## Test Signals
Enabled tracepoints show correct register, value, pipe, and length during USB register access and RX/TX URB flow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/usb_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/util.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/util.c

## Purpose
Implements small shared mt76 utilities for register polling, WCID bitmap allocation, minimum average RSSI sampling, and the common kthread worker loop used by USB/SDIO/TX paths.

## Important APIs, Types, And Functions
Exports `__mt76_poll()`, `____mt76_poll_msec()`, `mt76_wcid_alloc()`, `mt76_get_min_avg_rssi()`, and `__mt76_worker_fn()`. Poll helpers repeatedly read registers until masked values match. WCID allocation scans a bitmap for the first free index. RSSI sampling walks allocated WCIDs under RCU and uses EWMA signal values. The worker loop responds to schedule, park, and stop states.

## Control Flow
Poll helpers delay in microsecond or millisecond intervals until timeout. `mt76_get_min_avg_rssi()` disables BH, enters RCU, scans the WCID mask, locks RX state for RSSI/inactive counter updates, and returns the most negative active RSSI. `__mt76_worker_fn()` sleeps until scheduled, handles parking, sets RUNNING, calls the worker callback, reschedules cooperatively, and repeats until kthread stop.

## State And Persistence
State touched includes WCID masks, WCID inactive counters, EWMA RSSI values, and `mt76_worker.state` bits. Worker tasks persist until teardown.

## Dependencies And Integration Points
Depends on mt76 register access wrappers, RCU WCID lookups, RX spinlock, Linux kthreads, and `util.h` inline setup/schedule/disable/enable helpers.

## Risks
Polling timeouts can hide hardware stalls if callers ignore false returns. WCID allocation assumes the mask size and requested size match. Worker scheduling intentionally coalesces requests; code needing edge-counted work must keep its own queue.

## Test Signals
Register poll success/failure paths, WCID allocation exhaustion, RSSI values dropping to zero after inactive counts, worker schedule/park/unpark/teardown under load, and no lockdep issues in BH/RCU sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/util.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/util.h

## Purpose
Declares shared mt76 utility types and inline helpers for WCID bitmaps, SKB More Data bit manipulation, ring-index incrementing, and kthread worker lifecycle.

## Important APIs, Types, And Functions
Defines `struct mt76_worker`, worker state bits `MT76_WORKER_SCHEDULED` and `MT76_WORKER_RUNNING`, `MT76_INCR()`, `mt76_wcid_mask_set()`, `mt76_wcid_mask_clear()`, `mt76_skb_set_moredata()`, and inline worker helpers `mt76_worker_setup()`, `mt76_worker_schedule()`, `mt76_worker_disable()`, `mt76_worker_enable()`, and `mt76_worker_teardown()`.

## Control Flow
Worker setup creates a named kthread running `__mt76_worker_fn()`. Scheduling sets the scheduled bit and wakes the task unless already running. Disable parks the kthread and clears state; enable unparks and schedules it; teardown stops the thread. More Data helper directly toggles the 802.11 frame-control bit in an SKB header.

## State And Persistence
Worker state is held in the task pointer, callback pointer, and state bits. WCID bitmap helpers mutate caller-owned bitmaps. SKB frame control is modified in place.

## Dependencies And Integration Points
Depends on Linux SKB, bitops, bitfield, mac80211, wiphy names, and the implementation of `__mt76_worker_fn()` in `util.c`. Used by generic TX, USB, SDIO, and chip-specific worker paths.

## Risks
`mt76_worker_schedule()` coalesces events while RUNNING, so callbacks must drain all available work. `mt76_skb_set_moredata()` assumes the SKB data starts with an 802.11 header. Disable/enable must not race with object destruction.

## Test Signals
Correct worker names, scheduling after enable, no wake after teardown, correct More Data bit in PS-buffered frames, and WCID bitmap set/clear consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/wed.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/wed.c

## Purpose
Implements shared integration with MediaTek WED hardware offload. It provisions RX buffers and tokens, configures WED-backed DMA rings, toggles offload token ranges, bridges TC setup, and coordinates WED reset completion with mt76 DMA reset flow.

## Important APIs, Types, And Functions
Exports `mt76_wed_release_rx_buf()`, `mt76_wed_init_rx_buf()`, `mt76_wed_offload_enable()`, `mt76_wed_dma_setup()`, `mt76_wed_offload_disable()`, `mt76_wed_reset_complete()`, `mt76_wed_net_setup_tc()`, and `mt76_wed_dma_reset()`. Compile-time `CONFIG_NET_MEDIATEK_SOC_WED` gates the full RX-buffer and ring-setup implementation.

## Control Flow
RX buffer initialization allocates RXWI cache entries and page-pool buffers, writes WED buffer descriptors, consumes RX tokens, and encodes token/high DMA address bits. DMA setup inspects queue WED flags and type, then calls the appropriate WED ring setup for TX, TXFREE, RX, RRO data, MSDU page, or indication rings, temporarily clearing mt76 WED flags where software ring reset/fill must happen first. Offload enable shrinks the mt76 token range to reserve WED tokens and waits for outstanding WED tokens.

## State And Persistence
State includes RX token IDRs, RXWI cache objects, page-pool buffers, queue flags, `q->wed_regs`, `dev->token_size`, `dev->wed_token_count`, and reset completions `wed_reset`/`wed_reset_complete`. WED ring base registers persist in queue metadata after setup.

## Dependencies And Integration Points
Depends on mtk_wed_device APIs, mt76 DMA queue reset/fill, page-pool DMA addresses, mt76 token management in `tx.c`, TC offload integration, and queue flag conventions from mt76 DMA code.

## Risks
RX buffer initialization must unwind all tokens and pages on partial failure. Changing `token_size` while TX is active must be protected by `token_lock`. Ring setup mutates queue flags temporarily; failing to restore them would break later DMA logic. Reset completion has a fixed timeout and logs if WED firmware/hardware does not answer.

## Test Signals
WED active and inactive probe paths, TX/RX offload traffic, RX buffer release without leaks, token range restoration on disable, setup of all supported ring types, TC offload handoff, WED reset completion, and successful build with and without WED config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/wed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/Kconfig

## Purpose
Adds the kernel configuration option for the MT7601U USB Wi-Fi driver.

## Important APIs, Types, And Functions
Defines `config MT7601U` as a tristate with prompt `MediaTek MT7601U (USB) support`, depending on `MAC80211` and `USB`. Help text states it supports MT7601U-based USB wireless dongles.

## Control Flow
No runtime flow. Kconfig selection controls whether the mt7601u object is built in, as a module, or omitted.

## State And Persistence
The persistent state is the kernel build configuration symbol.

## Dependencies And Integration Points
Integrates with the kernel wireless driver Kconfig tree, mac80211, and USB subsystems. The Makefile consumes `CONFIG_MT7601U`.

## Risks
Missing dependencies would allow invalid builds; extra dependencies would hide the driver. The option does not select firmware or helper libraries, so packaging must handle runtime firmware separately if needed by adjacent code.

## Test Signals
`CONFIG_MT7601U=m/y` builds the driver only when MAC80211 and USB are enabled, and disabling the symbol omits the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/Makefile

## Purpose
Defines the object composition for the MT7601U driver module.

## Important APIs, Types, And Functions
`obj-$(CONFIG_MT7601U) += mt7601u.o` builds the module from `usb.o init.o main.o mcu.o trace.o dma.o core.o eeprom.o phy.o mac.o util.o debugfs.o tx.o`. `CFLAGS_trace.o := -I$(src)` supports trace header include resolution.

## Control Flow
No runtime flow. Kbuild links listed objects into the `mt7601u` module when enabled.

## State And Persistence
Build state is the object list and per-object CFLAGS.

## Dependencies And Integration Points
Integrates with Kbuild, the Kconfig symbol, and tracepoint generation for `trace.o`.

## Risks
Omitting an object causes unresolved symbols or missing driver behavior. Trace CFLAGS are required for `TRACE_INCLUDE_PATH .` patterns.

## Test Signals
Successful module build, no unresolved symbols across the listed objects, and tracepoint generation for mt7601u trace events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/core.c

## Purpose
Provides low-level readiness and polling helpers for the legacy MT7601U driver.

## Important APIs, Types, And Functions
`mt7601u_wait_asic_ready()` polls `MT_MAC_CSR0` until the chip returns a valid nonzero/non-all-ones value. `mt76_poll()` and `mt76_poll_msec()` poll arbitrary registers using microsecond or 10 ms sleep intervals and abort if `MT7601U_STATE_REMOVED` is set.

## Control Flow
All helpers repeatedly read registers, compare masked values, delay, and fail on timeout or removal. Poll helpers log timeout register addresses.

## State And Persistence
They read hardware registers and device removal state. No persistent driver state is written.

## Dependencies And Integration Points
Used during probe, hardware init, MAC start/stop, efuse reads, and reset flows throughout mt7601u. Depends on `mt7601u_rr()` register access and state bits.

## Risks
Timeout values are caller-selected and may be too short for slow USB devices or firmware states. A removed device forces false/EIO to prevent further USB access.

## Test Signals
Probe readiness after USB attach, timeout logging on unplug/stall, and successful waits around DMA idle, MAC idle, and efuse kick completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/debugfs.c

## Purpose
Creates MT7601U debugfs files for live register access, temperature metadata, AMPDU/stat counters, and parsed EEPROM calibration parameters.

## Important APIs, Types, And Functions
`mt7601u_init_debugfs()` creates the directory and files. `regidx`/`regval` expose arbitrary register read/write through `mt76_reg_get()` and `mt76_reg_set()`. `mt7601u_ampdu_stat_show()` dumps accumulated RX/TX/aggregation counters and average AMPDU length. `mt7601u_eeprom_param_show()` dumps EEPROM-derived RF offset, RSSI offset, temperature/LNA values, regulatory channels, per-rate/channel power, and TSSI parameters.

## Control Flow
Initialization runs after `ieee80211_register_hw()`. Reads of show files format current in-memory driver state; `regval` writes issue immediate register writes to the address selected by `regidx`.

## State And Persistence
Reads `dev->stats`, `avg_ampdu_len`, `raw_temp`, `temp_mode`, `debugfs_reg`, and parsed `dev->ee` contents. Arbitrary `regval` writes persist in hardware state.

## Dependencies And Integration Points
Depends on Linux debugfs/seq_file helpers, EEPROM parsed data from `eeprom.c`, MAC statistics accumulated in `mac.c`, and register access wrappers.

## Risks
Writable raw register access can disrupt hardware state and should be considered a diagnostic-only interface. The EEPROM show path assumes `dev->ee` has been initialized before debugfs creation.

## Test Signals
Files appear under the wiphy debugfs directory, register read/write works, AMPDU counters update after traffic, EEPROM parameters match efuse data, and absent TSSI hides the TSSI block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/dma.c

## Purpose
Implements the MT7601U-specific USB DMA datapath. It allocates RX/TX URBs, wraps TX SKBs with MT7601U DMA headers, submits bulk URBs, parses RX DMA aggregation segments into mac80211 SKBs, and completes TX/RX work through tasklets.

## Important APIs, Types, And Functions
Exports `mt7601u_dma_enqueue_tx()`, `mt7601u_dma_init()`, and `mt7601u_dma_cleanup()`. Key internal functions include RX parsing (`mt7601u_rx_next_seg_len()`, `mt7601u_rx_process_seg()`, `mt7601u_rx_skb_from_seg()`), URB callbacks (`mt7601u_complete_rx()`, `mt7601u_complete_tx()`), tasklets (`mt7601u_rx_tasklet()`, `mt7601u_tx_tasklet()`), TX submission (`mt7601u_dma_submit_tx()`), and queue allocation/free helpers.

## Control Flow
RX init allocates pages and URBs, submits all RX URBs, and completions add pending entries then schedule the RX tasklet. The tasklet parses one or more DMA segments from the page, handles RXWI/FCE metadata, builds SKBs with optional page frags, delivers them through `ieee80211_rx_list()`, resubmits the URB, and batches `netif_receive_skb_list()`. TX wraps the SKB with DMA info/padding, submits a bulk URB to the mapped endpoint, and completion queues the SKB for TX status processing and wakes mac80211 queues when near-full thresholds clear.

## State And Persistence
State includes RX ring `start/end/pending`, TX per-endpoint `start/end/used`, URB pointers, RX pages, queued SKBs, tasklets, `tx_skb_done`, and driver state bits for removed/initialized/stat reading. Hardware-visible state is the DMA header prepended to transmitted SKBs.

## Dependencies And Integration Points
Depends on Linux USB bulk APIs, tasklets, mac80211 RX/TX status, MT7601U DMA format from `dma.h`, RXWI processing in `mac.c`, USB endpoint discovery in `usb.c`, and statistics work scheduling.

## Risks
RX aggregation parsing must reject invalid lengths without overrunning the page. Page-frag ownership is subtle when replacing large RX pages. TX URB completion after removal must not touch freed queues. Queue stop/wake thresholds must avoid deadlock. Cleanup poisons RX URBs before killing tasklets and freeing pages.

## Test Signals
RX with single and aggregated segments, malformed frame rejection, TX queue full/wake behavior, unplug during RX/TX, DMA cleanup on init failure, TX status delivery after completion, and no page/URB leaks under USB fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/dma.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/dma.h

## Purpose
Defines MT7601U USB DMA header layout, packet/command descriptor fields, queue selectors, RX descriptor fields, event types, and inline TX SKB wrapping helpers.

## Important APIs, Types, And Functions
Important constants are `MT_DMA_HDR_LEN`, `MT_RX_INFO_LEN`, `MT_FCE_INFO_LEN`, `MT_DMA_HDRS`, TX/RX descriptor `GENMASK` fields, packet flags such as `MT_TXD_PKT_INFO_80211` and `MT_TXD_PKT_INFO_WIV`, and RX packet/error flags. Enums define DMA ports, info types, queue selectors, and MCU event types. `mt7601u_dma_skb_wrap()` and `mt7601u_dma_skb_wrap_pkt()` prepend TXINFO and pad SKBs.

## Control Flow
Inline wrapping computes the rounded transfer length, encodes destination port and info type, pushes a little-endian TXINFO word, and pads to a 4-byte boundary plus trailing zero word.

## State And Persistence
The header modifies SKB contents in place for TX. Descriptor definitions describe hardware-visible state exchanged with the USB DMA/FCE engine.

## Dependencies And Integration Points
Used by `dma.c` for data packets and by MCU command paths for command packet framing. Depends on Linux SKB, unaligned access, and bitfield helpers.

## Risks
Incorrect padding or length fields will desynchronize the USB DMA engine. The wrapping helper mutates SKB headroom, so callers must ensure sufficient headroom before calling.

## Test Signals
TX packets accepted by firmware/hardware, command responses parsed correctly, no SKB headroom warnings, and RX descriptor type/length checks matching observed USB data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/eeprom.c

## Purpose
Reads MT7601U efuse/EEPROM calibration data and converts it into driver calibration, regulatory, MAC address, power, RSSI, frequency-offset, and TSSI state.

## Important APIs, Types, And Functions
`mt7601u_eeprom_init()` is the exported initializer. Internal helpers read efuse blocks, validate physical usage-map size, detect TSSI support, set chip capabilities, compute per-channel power, choose country channel bounds, calculate RF frequency offset compensation, validate RSSI offsets, program per-rate TX power registers, and initialize TSSI slope/offset data.

## Control Flow
Initialization first checks the efuse usage map to reject devices that require an unsupported default EEPROM file. It allocates `dev->ee`, reads 256 bytes in 16-byte efuse blocks, warns on newer EEPROM versions, installs MAC address, parses capabilities and power tables, writes TX power configuration registers, and frees the temporary EEPROM buffer.

## State And Persistence
Persistent parsed state is stored in `dev->ee`: TSSI enable/data, RF frequency offset, RSSI offsets, reference temperature, LNA gain, per-channel power, per-rate power table, original CCK BW20 powers, and regulatory channel range. It also writes MAC address registers and TX power configuration hardware registers.

## Dependencies And Integration Points
Depends on MTD/OF headers only indirectly here, register access/polling, EEPROM field definitions in `eeprom.h`, MAC address setup in `mac.c`, and PHY calibration code that later consumes `dev->ee`.

## Risks
Invalid or all-0xff fields require fallback defaults; mishandling signed six-bit power values can over/under-program TX power. Region parsing has vendor quirks and a TODO for region 33/channel 14. Devices needing an external default EEPROM are explicitly unsupported.

## Test Signals
Probe logs EEPROM version/region, valid MAC address selection, correct 1-14 channel exposure by region, sane per-channel/per-rate power in debugfs, TSSI-enabled calibration on matching devices, and graceful failure on unusable efuse maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/eeprom.h

## Purpose
Defines MT7601U EEPROM/efuse offsets, bitfields, calibration data structures, and signed six-bit conversion helpers.

## Important APIs, Types, And Functions
Defines `MT7601U_EEPROM_SIZE`, max EEPROM version, default TX power, `enum mt76_eeprom_field`, NIC config bit masks, TX power by-rate offset macro, `enum mt7601u_eeprom_access_modes`, `struct power_per_rate`, `struct mt7601u_rate_power`, `struct reg_channel_bounds`, `struct mt7601u_eeprom_params`, and helpers `s6_validate()`, `s6_to_int()`, and `int_to_s6()`.

## Control Flow
No runtime flow except inline signed-six-bit validation/conversion used by EEPROM parsing and PHY power programming.

## State And Persistence
The structures define persistent parsed EEPROM state attached to `dev->ee`, including power tables, regulatory channel bounds, TSSI calibration, RSSI offsets, LNA gain, and frequency offset.

## Dependencies And Integration Points
Consumed by `eeprom.c`, debugfs, and PHY calibration code. Depends on bitfield macros and `struct mt7601u_dev` forward declaration.

## Risks
Offsets are hardware ABI; wrong values corrupt calibration. `s6_validate()` warns on out-of-range values but masks them, so caller validation remains important.

## Test Signals
Parsed debugfs EEPROM output matches raw efuse contents and signed power conversions behave for boundary values -32 and +31.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/init.c

## Purpose
Handles MT7601U device allocation, hardware power-on/reset, firmware/MCU/DMA/MAC/BBP/RF initialization, MAC start/stop, cleanup, supported band/rate registration, and mac80211 hardware registration.

## Important APIs, Types, And Functions
Exports `mt7601u_mac_start()`, `mt7601u_mac_stop()`, `mt7601u_init_hardware()`, `mt7601u_cleanup()`, `mt7601u_alloc_device()`, and `mt7601u_register_device()`. Internal helpers control WLAN power/reset, USB DMA configuration, BBP/MAC initval writes, beacon offsets, WCID/key memory initialization, counter reset, MAC stop hardware drain, and supported-band setup.

## Control Flow
Hardware init powers on WLAN, waits ASIC ready, initializes MCU, waits DMA idle, resets CSR/BBP, configures USB DMA, initializes MCU command path and DMA, writes MAC/BBP init values, clears WCID/key memories, disables beacon timing, reads EEPROM, initializes PHY, and sets default channel bandwidth/path state. Error paths unwind DMA, MCU command, and power state. Registration reserves WCID 0, creates monitor WCID, sets mac80211 capabilities, exposes 2 GHz channels/rates from EEPROM region, initializes work items, registers hardware, and creates debugfs.

## State And Persistence
Persistent state includes device locks, workqueues, WCID mask, beacon offsets, EEPROM pointer, macaddr, supported bands/rates, mac80211 hw flags, work items, DMA/MCU state, WLAN running/initialized bits, RX filter, and hardware registers programmed by init tables.

## Dependencies And Integration Points
Depends on mac80211 allocation/registration, MCU, DMA, EEPROM, PHY, MAC, debugfs, init tables, USB DMA registers, and MT7601U register definitions. It is the central probe/register path called by the USB driver.

## Risks
Initialization order is strict: MCU must be loaded before command register access, DMA before RX, EEPROM before band setup, and PHY after calibration data. MAC stop waits for several busy/page counters; timeout warnings indicate possible stale DMA state. Cleanup must be idempotent through `MT7601U_STATE_INITIALIZED`.

## Test Signals
Probe/register/unregister, init error injection at MCU/DMA/EEPROM/PHY steps, MAC start/stop with queues active, 2 GHz channel list matching EEPROM region, debugfs creation, and no busy warnings during normal stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/initvals.h

## Purpose
Holds static BBP and MAC register initialization tables for MT7601U hardware startup.

## Important APIs, Types, And Functions
Defines arrays `bbp_common_vals`, `bbp_chip_vals`, `mac_common_vals`, and `mac_chip_vals`, each containing `struct mt76_reg_pair` entries consumed by initialization code. The values configure BBP AGC/sync/RX/CCK controls, GLRT indexed registers, MAC basic rates, filters, backoff/timeout/protection, PBF/FCE, TX power attenuation, and beacon offsets.

## Control Flow
No executable flow. `init.c` writes these tables through `mt7601u_write_reg_pairs()` during hardware initialization.

## State And Persistence
The arrays are static const data. Their values persist in hardware registers after init until reset or later runtime configuration changes.

## Dependencies And Integration Points
Depends on MT7601U register definitions and `struct mt76_reg_pair`. Used by `mt7601u_init_bbp()` and `mt7601u_write_mac_initvals()`.

## Risks
Magic register values encode vendor hardware knowledge. A wrong value can break RX sensitivity, TX protection, DMA buffering, or beacon memory layout. Some later runtime code assumes these defaults before applying channel or association changes.

## Test Signals
Successful BBP/MAC initialization, association stability, expected RX filter/protection defaults, sane aggregation behavior, and no regressions when comparing register dumps with known-good vendor values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/initvals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/initvals_phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/initvals_phy.h

## Purpose
Provides static RF and BBP temperature/bandwidth tuning tables for MT7601U PHY initialization and runtime calibration.

## Important APIs, Types, And Functions
Defines `RF_REG_PAIR()` and tables `rf_central`, `rf_channel`, `rf_vga`, plus BBP mode tables for normal/high/low temperature and 20/40 MHz operation. `bbp_mode_table[3][3]` maps temperature state and bandwidth/group selection to a register table and count.

## Control Flow
No executable flow. PHY code writes these tables during initialization, channel changes, bandwidth changes, and temperature compensation.

## State And Persistence
Static const tables become persistent RF/BBP register state once written. They configure central RF blocks, channel RX/TX/PA/LOGEN sections, VGA, and temperature-dependent BBP AGC values.

## Dependencies And Integration Points
Consumed by MT7601U PHY code via `struct mt76_reg_pair`. The tables complement EEPROM power/TSSI data and BBP init values from `initvals.h`.

## Risks
The values are hardware-specific and opaque. Comments note a TODO around BBP178/channel 14 behavior, so channel-14 CCK bandwidth handling is a known fragility. Wrong table selection can damage sensitivity or spectral behavior.

## Test Signals
RF bring-up, channel switching across 1-14, 20/40 MHz operation, low/normal/high temperature calibration, RSSI/throughput stability, and spectral compliance around channel 14.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/initvals_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mac.c

## Purpose
Implements MT7601U MAC-level helpers for MAC address programming, TX/RX rate translation, TX status reporting, protection/TSF/preamble configuration, statistics work, WCID/key programming, RX status construction, and RSSI/beacon monitoring.

## Important APIs, Types, And Functions
Exports `mt7601u_set_macaddr()`, `mt76_mac_tx_rate_val()`, `mt76_mac_wcid_set_rate()`, `mt7601u_mac_fetch_tx_status()`, `mt76_send_tx_status()`, `mt7601u_mac_set_protection()`, `mt7601u_mac_set_short_preamble()`, `mt7601u_mac_config_tsf()`, `mt7601u_mac_work()`, `mt7601u_mac_wcid_setup()`, `mt7601u_mac_set_ampdu_factor()`, `mt76_mac_process_rx()`, `mt76_mac_wcid_set_key()`, and `mt76_mac_shared_key_setup()`.

## Control Flow
TX status reads `MT_TX_STAT_FIFO`, translates rates, fills mac80211 status, and reports no-SKB status under `mac_lock`. RX processing interprets RXWI fields, sets decrypted/stripped flags, leaves PN validation to mac80211 when needed, computes RSSI/rate/band/status, updates beacon/RSSI monitors, and returns MPDU length. Key setup writes WCID key/IV memory and cipher attributes, while shared-key setup writes per-BSS shared key tables. Periodic MAC work accumulates clear-on-read counters and recalculates average AMPDU length.

## State And Persistence
State includes `dev->macaddr`, `dev->stats`, `avg_ampdu_len`, `avg_rssi`, beacon frequency/PHY info, WCID rate/key attributes, hardware key memory, shared key memory, protection registers, TSF/beacon timer state, and RX status fields in SKBs.

## Dependencies And Integration Points
Depends on mac80211 rate/status APIs, register definitions, EEPROM/PHY RSSI helpers, tracepoints, WCID structures, key ciphers, delayed work, and `main.c` callbacks for BSS/key/rate changes.

## Risks
`mt7601u_mac_config_tsf()` computes a new value but does not write it in the enable path in this source, which is a suspicious behavior to validate against surrounding history. Hardware PN validation is intentionally not trusted. Key programming must keep WCID pairwise/shared key attributes synchronized. Clear-on-read stats require periodic accumulation to avoid losing counters.

## Test Signals
Correct RX rates/RSSI/decryption flags, TX status ACK/retry/rate reporting, WPA/WEP/TKIP/CCMP key install/remove, association protection mode changes, AMPDU factor changes with stations, MAC error reset logging, and TSF/beacon timer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mac.h

## Purpose
Defines MT7601U MAC descriptor structures, RX/TX info bitfields, PHY mode enums, TXWI layout, and MAC helper prototypes.

## Important APIs, Types, And Functions
Key structures are `struct mt76_tx_status`, `struct mt7601u_rxwi`, and `struct mt76_txwi`. The header defines `MT_RXINFO_*`, `MT_RXWI_*`, `MT_TXWI_*`, `enum mt76_phy_type`, and `enum mt76_phy_bandwidth`. Prototypes expose RX processing, key programming, rate programming, TX status fetch/report, and MAC address setup.

## Control Flow
No direct control flow. The bitfield definitions drive parsing/creation of hardware RXWI/TXWI/status records in `mac.c`, `dma.c`, and TX code.

## State And Persistence
Structures mirror hardware-visible descriptors and persistent per-WCID/rate/key state. RXWI fields carry RSSI, rate, MPDU length, decrypt status, and control metadata from hardware to driver.

## Dependencies And Integration Points
Used by MT7601U DMA, MAC, TX, and main callback code. Depends on SKB/mac80211 types via included translation units.

## Risks
Packed/aligned layout must match hardware exactly. The comments warn that some RSSI/SNR naming is based on vendor-driver interpretation rather than clean public documentation.

## Test Signals
RXWI parsing yields correct frame lengths/rates/RSSI, TXWI produced by TX code is accepted by hardware, and key/rate helper prototypes match all call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/main.c

## Purpose
Provides the MT7601U mac80211 operation table and callback implementations for start/stop, interface lifetime, channel config, RX filters, BSS changes, station add/remove, scan notifications, key setup, RTS threshold, AMPDU actions, and rate table updates.

## Important APIs, Types, And Functions
The exported object is `const struct ieee80211_ops mt7601u_ops`. Key callbacks are `mt7601u_start()`, `mt7601u_stop()`, `mt7601u_add_interface()`, `mt7601u_remove_interface()`, `mt7601u_config()`, `mt76_configure_filter()`, `mt7601u_bss_info_changed()`, `mt7601u_sta_add()`, `mt7601u_sta_remove()`, `mt7601u_set_key()`, `mt76_ampdu_action()`, `mt76_sta_rate_tbl_update()`, and `mt7601u_set_rts_threshold()`.

## Control Flow
Start enables MAC TX/RX and schedules MAC/calibration work. Stop cancels work and stops the MAC. Interface add programs the device MAC address if changed, reserves a group WCID, and initializes vif private state. Station add allocates a WCID, writes WCID address/attributes, publishes RCU pointer, and updates AMPDU factor; removal reverses it. BSS changes program BSSID, basic rates, TSF, protection, preamble, slot time, and calibration. Key setup selects hardware-supported ciphers, updates WCID and shared key memory, or falls back to software for unsupported ciphers.

## State And Persistence
State includes `wcid_mask`, RCU `dev->wcid[]`, vif group WCID, station WCID, MAC address, RX filter bits, scan state bit, calibration work, BSSID/protection/rate/slot registers, hardware key tables, and per-station aggregation sequence state.

## Dependencies And Integration Points
Depends on mac80211 callbacks, MT7601U MAC/PHY/DMA/TX helpers, WCID register definitions, scan calibration helpers, and cipher/key APIs.

## Risks
The driver supports station mode only, but some comments mention AP-style group WCID assumptions. WCID allocation is local and limited to 119. The RX filter helper inverts mac80211 filter flags into drop bits and must keep `total_flags` consistent. AMPDU actions directly manipulate WCID BA bits and send BARs.

## Test Signals
Station association/disassociation, channel changes, scan start/complete calibration restore, RX filter toggles in monitor/promisc-like modes, WPA/WEP/TKIP/CCMP key install/remove, AMPDU RX/TX start/stop, and rate table updates reflected in TXWI rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/main.c -->
