# subset-b-004852 research

Grouped research report for the mt7615/mt76 Connac driver files in `sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76`. Each section preserves the source path and is bounded for deterministic splitting into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mcu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mcu.h

Purpose: Defines MT7615/MT7663 MCU wire formats, firmware state constants, regulatory/test power SKU indexes, radar report layouts, remain-on-channel TLVs, and DBDC type identifiers. It is a protocol contract header used by transport-specific MCU implementations and by higher-level mt7615 control code.

Important APIs, types, and constants: `struct mt7615_mcu_txd` and `struct mt7615_uni_txd` describe legacy and unified MCU command descriptors, including command IDs, sequence numbers, packet type, source/destination index, and ACK/set/query options. `struct mt7615_mcu_rxd` is the common MCU event header. `struct mt7615_mcu_csa_notify`, `struct mt7615_mcu_rdd_report`, and `struct mt7615_roc_tlv` model channel-switch, radar-detection, and remain-on-channel payloads. `MT_SKU_*` indexes map EEPROM/rate families into firmware TX power tables. `FW_STATE_PWR_ON` and `FW_STATE_N9_RDY` are used by USB/SDIO/PCI firmware bring-up polling.

Control flow and integration: This file has no executable code, but its packed/aligned structures are serialized directly into skb command buffers by `mt7615_mcu_fill_msg()`, `mt7663u_mcu_send_message()`, and `mt7663s_mcu_send_message()`. Transport code relies on `sizeof(struct mt7615_mcu_txd)` for MCU headroom, so layout drift changes DMA-visible packet framing. Radar and ROC structures are consumed by MCU event and command paths outside this subset.

State and persistence: The header defines transient host/firmware command state only. Persistent data is in firmware, EEPROM, and device registers; this file preserves host-side binary interpretation.

Dependencies: Includes `../mt76_connac_mcu.h` for command macros and shared MCU definitions; depends on Linux endian and packing conventions through included mt76 headers.

Risks: Any field size, packing, alignment, endian annotation, SKU order, or enum value change can break firmware ABI. The large radar report arrays are fixed-format hardware reports and should not be resized without matching firmware. `set_query` is documented as firmware-don't-care in one descriptor but remains part of the ABI.

Test signals: Build coverage catches type/layout references. Runtime signals include successful firmware load, MCU command replies, DFS/radar reports, CSA notifications, ROC grants, and testmode TX power command success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mmio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mmio.c

Purpose: Provides PCI/platform MMIO registration glue, register base maps for MT7615E and MT7663E, interrupt dispatch, and mt76 bus operation wrappers that translate logical register addresses through `mt7615_reg_map()`.

Important APIs and functions: `mt7615e_reg_map[]` and `mt7663e_reg_map[]` map `enum mt7615_reg_base` indexes to chip-specific physical bases. `mt7615_irq_handler()` masks interrupts and schedules `irq_tasklet` after initialization. `mt7615_irq_tasklet()` reads `MT_INT_SOURCE_CSR`, acknowledges interrupts, schedules TX/RX NAPI, and queues SER reset work when MCU error bits appear. `mt7615_rr()`, `mt7615_wr()`, and `mt7615_rmw()` wrap original bus ops after applying register remapping. `mt7615_mmio_probe()` allocates the mt76 device, installs driver ops, requests IRQ, enables MT7663 PCI IRQ if needed, and calls `mt7615_register_device()`.

Control flow: PCI or platform probe passes a BAR/resource base and IRQ into `mt7615_mmio_probe()`. The function clones `mt7615_ops`, allocates `mt7615_dev`, initializes MMIO, records ASIC revision, replaces mt76 bus callbacks with remapping wrappers, disables interrupts, requests IRQ, then registers the device. Interrupt flow masks IRQs in hardirq context, drains sources in the tasklet, selectively disables sources while NAPI owns them, and re-enables RX through `mt7615_rx_poll_complete()`.

State and persistence: Runtime state includes `dev->reg_map`, `dev->bus_ops`, `dev->mt76.mmio.irqmask`, NAPI/tasklet scheduling state, and `dev->reset_state`. No persistent storage is written.

Dependencies and integration: Integrates Linux module init/exit, PCI driver registration, optional MT7622 platform driver registration, mt76 core allocation/MMIO/NAPI APIs, register macros from `regs.h`, MAC callbacks from `mac.h`, and tracepoint `trace_dev_irq()`.

Risks: Interrupt masking mistakes can lose RX/TX completions or spin tasklets. Register-map errors redirect MMIO operations to wrong hardware blocks. Reset work depends on accurate MCU error masks, which differ for MT7663. Error unwind must free IRQ/device without double-freeing devm resources.

Test signals: Probe success with correct ASIC revision log, IRQ/NAPI packet flow, firmware reset recovery after MCU error, suspend/resume coverage through PCI, and module load/unload without leaked IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mt7615.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mt7615.h

Purpose: Primary private header for the mt7615 driver family. It defines firmware names, device limits, ring sizes, core per-device/per-phy/per-station structures, MCU operation indirection, inline helpers, and cross-file prototypes.

Important APIs and types: `struct mt7615_dev` embeds `struct mt76_dev` first, stores bus ops, register map, MCU ops, PM/coredump state, reset work, firmware version, DBDC support, and rate-work lists. `struct mt7615_phy` stores per-radio state: channel/filter state, survey/MIB counters, scan/ROC work, radar state, and optional testmode snapshots. `struct mt7615_sta` and `struct mt7615_vif` extend mt76/mac80211 station and interface data. `struct mt7615_mcu_ops` abstracts firmware generations and buses for BA, station, BSS, beacon, PM ownership, and decap offload. Inline helpers choose hardware phy/device, ext phy, WTBL size, queue mapping, MCU TX interrupt mask, firmware offload mode, and PM mutex acquisition.

Control flow and integration: All bus frontends allocate `mt7615_dev`, initialize common fields, and enter common registration through `mt7615_register_device()` or `mt7663_usb_sdio_register_device()`. mac80211 callbacks from `mt7615_ops`, mt76 driver ops, MCU code, DMA code, PCI reset code, USB/SDIO helpers, debugfs, EEPROM, and testmode all share this header as their contract.

State and persistence: Describes runtime state for radios, stations, VIFs, reset sequencing, PM stats, rate control, and coredump buffering. Persistent device identity/calibration come from EEPROM and firmware files named here; the header only stores pointers and parsed state.

Dependencies: Includes Linux completion/interrupt/regmap primitives, mt76 Connac MCU headers, and `regs.h`. Assumes mt76 structures are embedded first for `container_of()` casting.

Risks: Structure layout assumptions are strong: `mt76_dev`, `mt76_phy`, `mt76_wcid`, and `mt76_vif_link` must remain first in wrapper structs. The duplicate `mt7615_reg_map()` prototype is harmless but noisy. MCU op indirection means NULL or incomplete ops cause runtime faults. Ring sizes/token sizes and WTBL limits must match hardware/firmware.

Test signals: Compile-time coverage across all mt7615 translation units, successful multi-bus probe, ext-phy registration for DBDC, station add/remove, PM wake/sleep, reset recovery, testmode commands, and firmware loading for listed blobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mt7615.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mt7615_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mt7615_trace.h

Purpose: Defines mt7615-specific Linux tracepoints, currently a reusable device/token event class and the `mac_tx_free` event.

Important APIs and types: `DECLARE_EVENT_CLASS(dev_token)` records the wiphy name and a TX token. `DEFINE_EVENT(dev_token, mac_tx_free, ...)` instantiates the trace event. Macros `DEV_ENTRY`, `DEV_ASSIGN`, `TOKEN_ENTRY`, and related print macros keep tracepoint field definitions consistent.

Control flow and integration: Included by `trace.c` with `CREATE_TRACE_POINTS` to emit tracepoint definitions and included by other code for declarations. Runtime users can enable the `mt7615:mac_tx_free` tracepoint through ftrace/perf to observe token completion behavior.

State and persistence: No persistent state. Each trace event snapshots the wiphy name and token at emission time.

Dependencies: Linux tracepoint infrastructure and `mt7615.h` for `struct mt7615_dev` and `mt76_hw()`. `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` are set for kernel trace generation.

Risks: Trace headers are sensitive to include guards and `TRACE_HEADER_MULTI_READ`; wrong names or paths break generated trace code. `strscpy()` bounds the wiphy name to 32 bytes, so trace names can truncate.

Test signals: Kernel build with tracepoints enabled, presence of generated trace events under tracing, and successful event emission during TX token free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mt7615_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/pci.c

Purpose: PCI bus frontend for MT7615/MT7663/MT7611 devices. It binds PCI IDs, prepares PCI resources, enters common MMIO probe, and implements PCI power-management suspend/resume.

Important APIs and functions: `mt7615_pci_device_table[]` matches MediaTek device IDs `0x7615`, `0x7663`, and `0x7611`. `mt7615_pci_probe()` enables the device, maps BAR0, allocates IRQ vectors, sets DMA mask, disables ASPM, chooses the register map, and calls `mt7615_mmio_probe()`. `mt7615_pci_remove()` unregisters common device state and frees IRQ vectors. PM callbacks `mt7615_pci_suspend()` and `mt7615_pci_resume()` coordinate firmware HIF suspend, NAPI/worker disablement, DMA reset, PDMA sleep protection, PCI D-state transitions, and ownership handoff.

Control flow: Probe is linear resource setup with a single error path freeing IRQ vectors. Suspend wakes the device, optionally tells firmware to suspend HIF, disables software packet processing, resets DMA, waits for PDMA idle, enables MT7663 sleep protection, saves PCI state, changes power state, and gives control to firmware. Resume reverses ownership, restores PCI D0/state, clears MT7663 sleep protection, detects whether PDMA rings need reinitialization, re-enables workers/NAPI, schedules NAPI, and clears HIF suspend.

State and persistence: Tracks PCI power state, wake capability, saved PCI config, mt76 worker/NAPI enabled state, and device PM ownership. No filesystem persistence; firmware blobs are declared through `MODULE_FIRMWARE()`.

Dependencies: Linux PCI APIs, mt76 PCI helpers, `mt7615_mmio_probe()`, `mt7615_dma_reset()`, `mt7615_wait_pdma_busy()`, Connac MCU HIF suspend, and register macros in `regs.h`.

Risks: Suspend/resume ordering is delicate; failing to stop NAPI/workers before DMA reset can race RX/TX rings. Returning early after setting HIF suspend can leave firmware/host state mismatched if later restore paths miss it. PDMA reset detection only logs and does not reinitialize in this file. PCI IRQ cleanup mixes devm IRQ and vector freeing.

Test signals: Device probe/remove, module autoload by PCI ID, runtime and system suspend/resume, traffic after resume, MT7663 sleep-protection polling, and absence of stuck queues or IRQ storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/pci_init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/pci_init.c

Purpose: Common PCI/MMIO registration and teardown path after raw MMIO probing. It initializes EEPROM/DMA/global WCID state, registers with mac80211, starts asynchronous MCU initialization, and tears down the device.

Important APIs and functions: `mt7615_pci_init_work()` retries `mt7615_mcu_init()` up to ten times on `-EAGAIN`, then calls `mt7615_init_work()`. `mt7615_init_hardware()` clears interrupt source, initializes EEPROM, performs MT7663 RGU toggling, initializes DMA, marks `MT76_STATE_INITIALIZED`, and allocates global WCID 0 for beacon/mgmt frames. `mt7615_register_device()` performs common device init, reset work setup, optional LED callbacks, MT7622 WMAC init, hardware init, `mt76_register_device()`, thermal init, MCU work scheduling, TX power init, ext-phy registration, and debugfs init. `mt7615_unregister_device()` waits for MCU, unregisters ext phy and mac80211, exits MCU, releases tokens/DMA/tasklet, and frees mt76 device.

Control flow: Bus probe calls `mt7615_register_device()` after IRQ/MMIO setup. Registration initializes low-level state before mac80211 registration, then schedules firmware init asynchronously so the netdev can complete setup while firmware retry logic runs in workqueue context. Unregister reverses order, avoiding MCU exit if firmware never ran.

State and persistence: Initializes EEPROM-backed state in `dev->mt76.eeprom`, DMA rings, global WCID array, LED callbacks, reset work, thermal/debugfs state, and optional DBDC ext phy. Persistent calibration comes from EEPROM/efuse, not written here.

Dependencies: EEPROM, DMA, MCU, thermal, debugfs, init, MT7622 platform support, mac80211 registration, and mt76 WCID allocation.

Risks: If global WCID allocation returns nonzero, registration fails because management frames are required to use index 0. Asynchronous MCU failure is silently left after retries. Error paths after `mt76_register_device()` can return without fully unregistering earlier registration work, so callers must handle partial state carefully.

Test signals: Successful device registration, EEPROM/DMA init logs, MCU retry behavior, global WCID index 0 allocation, thermal/debugfs availability, ext-phy registration for DBDC, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/pci_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/pci_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/pci_mac.c

Purpose: PCI/MMIO TX preparation, DMA reset, and firmware-coordinated MAC reset recovery for mt7615.

Important APIs and functions: `mt7615_write_fw_txp()` converts mt76 scatter-gather buffers into firmware TXP descriptors for MT7615 firmware TX processing. `mt7615_tx_prepare_skb()` allocates a token, sets rate-probe state, writes TXWI, writes either firmware or hardware TXP, and hands skb ownership to the queue. `mt7615_dma_reset()` disables DMA, cleans TX/MCU/RX queues, flushes TX status, and restarts DMA. `mt7615_mac_reset_work()` handles SER reset by stopping queues, setting reset bits, disabling workers/NAPI, notifying firmware, resetting DMA/tokens, reinitializing PDMA, resuming NAPI/queues, updating beacons, and rescheduling MAC work.

Control flow: TX begins in mt76 driver ops and enters `mt7615_tx_prepare_skb()`. Rate-probe frames update WTBL rates under lock before descriptor writing. For reset, interrupt code stores `dev->reset_state` and queues `reset_work`; reset work waits for firmware state transitions (`STOP_PDMA`, `RESET_DONE`, `RECOVERY_DONE`, `NORMAL_STATE`) and mirrors each phase with HIF events.

State and persistence: Manages token IDR/cache entries, queue contents, per-station rate-probe fields, reset bits in `mphy.state`, `reset_state`, ROC timers/work, NAPI/worker enablement, and beacon offload state. No persistent storage.

Dependencies: mt76 DMA/queue/token APIs, Connac TXP helpers, `mt7615_mac_write_txwi()`, MCU beacon offload, MT7622 HIF interrupt trigger, register definitions, and mac80211 queue control.

Risks: TX token leaks or incorrect `tx_info->nbuf` rewrites can break completions and DMA unmap. Reset sequencing is highly race-sensitive around NAPI, workers, ROC timers, MCU waits, and token IDR reinitialization. Firmware state waits only warn on timeout, so partial recovery may continue. Beacon updates must cover both main and ext phys.

Test signals: TX traffic with software and hardware TXP modes, rate probing, token exhaustion recovery, forced SER/reset events, post-reset beaconing, NAPI reenablement, and DMA queue cleanup without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/pci_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/regs.h

Purpose: Central register map and bitfield definition header for MT7615/MT7663/MT7622 variants across MMIO, USB, and SDIO transports.

Important APIs and constants: `enum mt7615_reg_base` indexes chip-specific base arrays. Macros cover hardware IDs, firmware state, MCU remap windows, HIF/PDMA registers, interrupt masks, PLE/PSE/PP/DMASHDL scheduler fields, PHY/RF controls, MAC CFG/AGG/ARB/TMAC/RMAC blocks, WTBL update/rate/key fields, LPON TSF registers, MIB counters, LED controls, efuse controls, MT7622 infracfg, UDMA, and antenna switch controls.

Control flow and integration: Executable files combine these macros with `dev->reg_map` to read/write logical device blocks. `mmio.c` maps high logical addresses via `mt7615_reg_map()`. PCI/USB/SDIO initialization, PM ownership, testmode antenna setup, DMA scheduling, MAC reset, RX filtering, WTBL rate updates, LED callbacks, efuse reads, and survey/MIB updates all use these definitions.

State and persistence: The file describes hardware state stored in registers: interrupt sources/masks, DMA enable/busy state, firmware ownership and readiness, WTBL contents, MIB counters, efuse data, LED blink state, and scheduler quotas. It does not store host state itself.

Dependencies: Linux `BIT`, `GENMASK`, and field-prep helpers through included kernel headers. Depends on callers having a `dev` variable in scope for many macros, which is a deliberate local style.

Risks: Register offsets and bit masks are hardware ABI. A wrong base index, overlapping mask, or variant mismatch can corrupt unrelated hardware blocks. Some names are duplicated, such as `MT_HIF0_MIN_QUOTA`, reflecting shared bit positions; edits need caution. Macros that use implicit `dev` are easy to misuse outside mt7615 code.

Test signals: Successful probe across chip variants, correct ASIC revision, interrupt delivery, firmware readiness polling, efuse reads, DMA scheduling, LED behavior, testmode antenna switching, and survey/MIB values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/sdio.c

Purpose: SDIO bus frontend for MT7663S devices. It binds SDIO IDs, initializes mt76 SDIO transport, parses SDIO interrupt data, registers the shared USB/SDIO mt7615 device, and implements SDIO suspend/resume.

Important APIs and functions: `mt7663s_table[]` matches vendor/device `0x7603`. `mt7663s_txrx_worker()` wraps `mt76s_txrx_worker()` in Connac PM references and queues wake work if asleep. `mt7663s_init_work()` initializes SDIO MCU then common work. `mt7663s_parse_intr()` reads `MCR_WHISR` into `struct mt7663s_intr` and copies ISR/TX/RX/mailbox fields into mt76's generic SDIO interrupt structure. `mt7663s_probe()` allocates mt76 device, installs SDIO bus ops, initializes hardware, allocates queues, creates a FIFO-low TX/RX worker, and calls `mt7663_usb_sdio_register_device()`. PM callbacks coordinate HIF suspend, keep-power, ownership, worker disable/enable, and TX status flushing.

Control flow: SDIO probe creates `mt7615_dev`, sets `mt7663_usb_sdio_reg_map`, uses `mt76s_init()`/`mt76s_hw_init()`, reads ASIC revision, allocates interrupt buffer and queues, starts a worker, then enters shared USB/SDIO registration. Remove unregisters hw only if initialized and deinitializes mt76 SDIO.

State and persistence: Tracks SDIO function drvdata, `mdev->sdio.parse_irq`, interrupt buffer, SDIO workers, PM ownership/state, and initialized bit. No persistent storage.

Dependencies: Linux MMC/SDIO APIs, mt76 SDIO helpers, `mt7663s_mcu_init()`, shared USB/SDIO data path helpers, Connac PM helpers, and firmware declarations.

Risks: SDIO host claiming must wrap register reads/writes correctly. PM reference failure must not run TX/RX while firmware owns the device. Suspend disables multiple workers and clears stats state; missed reenable can stall traffic. Interrupt struct layout must match device WHISR layout.

Test signals: SDIO enumeration, interrupt parsing under traffic, TX/RX worker wake from low power, suspend/resume with `MMC_PM_KEEP_POWER`, post-resume traffic, and clean remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/sdio_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/sdio_mcu.c

Purpose: SDIO-specific MCU transport and power-ownership control for MT7663S.

Important APIs and functions: `mt7663s_mcu_init_sched()` reads PSE/PLE quotas and TX descriptor count into `sdio->sched`. `mt7663s_mcu_send_message()` fills the mt7615 MCU descriptor and sends the skb on the WM MCU queue. `__mt7663s_mcu_drv_pmctrl()` clears firmware ownership via `WHLPCR_FW_OWN_REQ_CLR` and polls for driver ownership. `mt7663s_mcu_fw_pmctrl()` sets firmware ownership via `WHLPCR_FW_OWN_REQ_SET`, using `mt76_connac_skip_fw_pmctrl()` to avoid sleeping with tokens or wake refs. `mt7663s_mcu_init()` installs mt76 MCU ops, restarts firmware if N9 is already ready, loads firmware, clones mt7615 MCU ops to override PM callbacks, initializes SDIO scheduling, and marks MCU running.

Control flow: SDIO init first forces driver ownership, sets low-level MCU ops, handles pre-existing firmware state, loads firmware with `__mt7663_load_firmware()`, then patches the high-level `dev->mcu_ops` PM functions to SDIO-specific ownership routines.

State and persistence: Updates `MT76_STATE_PM`, `MT76_STATE_MCU_RUNNING`, PM wake/doze timestamps and counters, SDIO scheduler quotas/deficit, and firmware ownership state in WHLPCR. Firmware image persists only in device memory after load.

Dependencies: mt76 SDIO register helpers, Connac PM helpers, mt7615 MCU parser/fill logic, firmware loader, and register definitions for PSE/PLE/PP/CONN.

Risks: Ownership polling timeouts leave the host and firmware disagreeing about who may access registers. PM stats are updated only after successful transitions. Cloning `dev->mcu_ops` assumes base MCU init populated all required callbacks before override. Firmware restart polling on `MT_CONN_ON_MISC` must match chip state bits.

Test signals: Firmware load on SDIO, successful driver/firmware ownership transitions, PM doze/awake stats, SDIO scheduler values, MCU command replies, and resume from low power without command timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/sdio_mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/soc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/soc.c

Purpose: Platform-driver frontend for MT7622 integrated WMAC using the mt7615 MMIO core.

Important APIs and functions: `mt7622_wmac_init()` looks up the `mediatek,infracfg` syscon regmap for MT7622 devices. `mt7622_wmac_probe()` obtains platform IRQ and MMIO resource, then calls `mt7615_mmio_probe()` with the MT7615E register map. `mt7622_wmac_remove()` unregisters the common device. `mt7622_wmac_driver` binds the `mediatek,mt7622-wmac` compatible.

Control flow: Platform probe maps SoC resources and delegates almost all device setup to the common MMIO path. During common registration, `mt7622_wmac_init()` is called to acquire infracfg support for HIF wake/interrupt integration.

State and persistence: Stores `dev->infracfg` regmap for MT7622-specific wake/interrupt control. No persistent storage.

Dependencies: Linux platform device, device tree, syscon/regmap, common `mt7615_mmio_probe()`, and firmware declarations for MT7622 N9/ROM patch.

Risks: Device tree must provide a valid IRQ, MMIO resource, and `mediatek,infracfg` phandle. The SoC uses the mt7615e map, so incompatible register layout would break shared MMIO code. Remove assumes platform drvdata is set by common mt76 probe path.

Test signals: Device-tree match/probe, successful infracfg lookup, firmware load, HIF interrupt triggering on MT7622, and platform remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/testmode.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/testmode.c

Purpose: Implements mt76 nl80211 testmode operations for MT7615, including test TX power control, frequency offset, antenna path control, RX enablement, TX frame state, and RX stat dumping.

Important APIs and functions: `mt7615_tm_set_tx_power()` builds an MCU `SET_TX_POWER_CTRL` message from EEPROM data and optional test TX power overrides. `mt7615_tm_reg_backup_restore()` snapshots/restores selected PHY, antenna-switch, and RF registers. `mt7615_tm_init()` toggles SKU control, refreshes channel/filter state, and handles register backup/restore. `mt7615_tm_set_rx_enable()` toggles ARB RX/RXV bits. `mt7615_tm_set_tx_antenna()` programs PHY/RF/antenna-switch registers for requested chain masks. `mt7615_tm_set_tx_frames()` prepares TX frame mode. `mt7615_tm_update_params()`, `mt7615_tm_set_state()`, `mt7615_tm_set_params()`, and `mt7615_tm_dump_stats()` implement `mt7615_testmode_ops`.

Control flow: mt76 testmode invokes `set_state` and `set_params` with parsed nl80211 attributes. State transitions into/out of idle or TX frames update MCU parameters, channel/filter state, RX enablement, antenna masks, and register backup. Dump stats emits last RX frequency offset, RCPI, IB RSSI, and WB RSSI arrays into nested netlink attributes.

State and persistence: Uses `phy->mt76->test` current state, param bitmaps, tx power, freq offset, tx antenna mask, and tx skb. Stores backup registers in `phy->test.reg_backup` for restoration when testmode exits. No persistent device storage is intentionally modified, though hardware registers are temporarily changed.

Dependencies: mt76 testmode framework, EEPROM power index helpers, MCU test parameter APIs, channel/filter ops, RF read/write helpers, register definitions, and nl80211 netlink attributes.

Risks: Register backup allocation failure silently disables restore protection. Incorrect antenna masks can leave RF paths disabled until reinit. Testmode changes normal RX/TX behavior and must restore SKU, filters, RX, and RF state on exit. TX power index calculations must match EEPROM layout and band/chain rules.

Test signals: nl80211 testmode state transitions, TX frame generation, RX stat dumps, frequency offset and TX power MCU command success, register restoration after OFF, invalid antenna mask rejection, and normal traffic after leaving testmode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/testmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/trace.c

Purpose: Instantiates mt7615 tracepoints declared in `mt7615_trace.h`.

Important APIs and functions: Defines `CREATE_TRACE_POINTS` before including `mt7615_trace.h`, guarded by `#ifndef __CHECKER__` for sparse compatibility.

Control flow and integration: Compiled once into the driver so the tracepoint declarations become definitions. Other files can include the trace header without defining storage.

State and persistence: No runtime state beyond kernel tracepoint registration.

Dependencies: Linux module infrastructure and tracepoint generation macros.

Risks: If this file is omitted from the build, tracepoint users link-fail. If `CREATE_TRACE_POINTS` is duplicated elsewhere, duplicate definitions occur.

Test signals: Successful module link and visibility of mt7615 tracepoints in kernel tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/usb.c

Purpose: USB bus frontend for MT7663U devices. It implements USB register access, bulk copy, probe/disconnect, queue setup, and USB suspend/resume.

Important APIs and functions: `mt7615_device_table[]` matches two MT7663 USB IDs. `mt7663u_rr()`, `mt7663u_wr()`, `mt7663u_rmw()`, and `mt7663u_copy()` perform vendor-request register access under `usb_ctrl_mtx`. `mt7663u_stop()` overrides mac80211 stop for USB, canceling ROC/scan/MAC work and stopping TX. `mt7663u_probe()` clones ops, resets USB device, initializes mt76 USB, reads revision, powers on MCU if needed, allocates MCU/data queues, and enters shared USB/SDIO registration. PM callbacks stop/resume RX/TX and coordinate firmware HIF suspend.

Control flow: USB probe allocates device state, takes a USB device reference, resets hardware, sets interface drvdata, initializes USB bus ops, handles firmware power state, allocates queues, then calls `mt7663_usb_sdio_register_device()`. Disconnect unregisters hw, cleans queues, clears drvdata/ref, and frees mt76 state.

State and persistence: Tracks USB interface drvdata, USB device refcount, queue allocation, power-off flag, running/initialized bits, worker/work cancellation state, and firmware HIF suspend. No host persistence; firmware blobs are declared.

Dependencies: Linux USB APIs, mt76 USB helpers, shared USB/SDIO helpers, mt7663 USB MCU init/power-on, Connac firmware suspend, and register definitions.

Risks: Vendor register access must be serialized. Probe error paths must release USB refs and queue resources. Power-on polling currently returns 0 after timeout path assignment unless `ret` is propagated carefully in future edits. Stop/disconnect must cancel delayed work before freeing device.

Test signals: USB enumeration, register read/write over vendor requests, firmware power-on/load, queue allocation, traffic, disconnect cleanup, suspend/resume with RX/TX restart, and no leaks of USB device refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/usb_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/usb_mcu.c

Purpose: USB-specific MCU message transport and power-on sequence for MT7663U.

Important APIs and functions: `mt7663u_mcu_send_message()` fills mt7615 MCU descriptors, selects in-band command or firmware scatter endpoint, prepends USB length, pads to required alignment, sends a bulk message, and frees the skb. `mt7663u_mcu_power_on()` issues the vendor power-on request and polls firmware power state. `mt7663u_mcu_init()` installs USB MCU ops, enables firmware download routing, restarts/powers on firmware when recovering from power-off, loads firmware, disables firmware download routing, and marks MCU running.

Control flow: USB probe may call power-on before queue allocation. Later async MCU work calls `mt7663u_mcu_init()`, which sets mt76 MCU headroom/tailroom and send/parse ops, handles prior power-off state, loads firmware via `__mt7663_load_firmware()`, then sets `MT76_STATE_MCU_RUNNING`.

State and persistence: Updates UDMA firmware-download register bit, `MT76_STATE_POWER_OFF`, `MT76_STATE_MCU_RUNNING`, and firmware memory contents. No persistent storage.

Dependencies: mt76 USB bulk/vendor helpers, mt7615 MCU fill/parse, common firmware loader, USB/UDMA register definitions, and firmware power state constants from `mcu.h`.

Risks: Endpoint selection must keep firmware scatter packets on the data endpoint and normal commands on in-band command endpoint. Padding/length framing is USB ABI. `mt7663u_mcu_power_on()` sets an error on timeout but returns 0 in the current code, which can mask a power-on failure signal. Firmware download routing must be cleared after load.

Test signals: MCU command replies over USB, firmware scatter load, power-on polling behavior, firmware restart from power-off, and command timeout absence after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/usb_mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/usb_sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/usb_sdio.c

Purpose: Shared MT7663 USB/SDIO helper layer for register maps, TX descriptor preparation/completion, rate update work, USB DMA scheduler setup, common hardware init, and common mac80211 registration.

Important APIs and functions: `mt7663_usb_sdio_reg_map[]` defines absolute register bases for non-PCI transports. `mt7663_usb_sdio_write_txwi()` writes a USB/SDIO-sized TXWI before skb data. `mt7663_usb_sdio_set_rates()` programs WTBL rate fields and LPON TSF-derived rate-set state. `mt7663_usb_sdio_rate_work()` drains queued WTBL rate descriptors under PM mutex. `mt7663_usb_sdio_tx_status_data()` polls station stats. `mt7663_usb_sdio_tx_complete_skb()` removes transport headroom and completes skb status. `mt7663_usb_sdio_tx_prepare_skb()` handles rate-probe setup, packet ID, TXWI push, USB length header, and padding. `mt7663u_dma_sched_init()` configures DMASHDL/UDMA for USB. `mt7663_usb_sdio_register_device()` performs common init, headroom/max-fragment setup, mac80211 registration, VHT AMSDU adjustment, MCU work scheduling, TX power init, and debugfs init.

Control flow: USB and SDIO probes allocate transport queues, then call `mt7663_usb_sdio_register_device()`. TX preparation rewrites skb headroom in-place before mt76 queueing. Rate changes are queued on `dev->wrd_head`, then workqueue context programs WTBL with device awake. Common registration initializes EEPROM/global WCID before mac80211 registration and schedules transport-specific MCU init work.

State and persistence: Maintains WTBL rate fields, station `rate_probe`, `rate_set_tsf`, `rate_count`, `wcid.tx_info`, queued rate descriptors, global WCID 0, `MT76_STATE_INITIALIZED`, USB SG-dependent headroom/fragment limits, and VHT capability adjustment. No persistent storage beyond EEPROM reads.

Dependencies: mt76 USB/SDIO helpers, `mt7615_mac_write_txwi()`, EEPROM init, mt7615 common init/debugfs/TX power, WTBL/LPON/DMASHDL/UDMA registers, and Connac PM mutex wrappers.

Risks: skb headroom and padding differ between USB and SDIO; mistakes corrupt packets or completion pulls. WTBL update polling can time out and rate-work return values are not surfaced. Packet ID must be removed on padding failure. USB SG capability changes maximum A-MSDU behavior. Register-map exports are shared by both bus modules.

Test signals: USB and SDIO TX/RX traffic, TX status completion, rate probing, WTBL rate update behavior, no-SG VHT cap downgrade, DMA scheduler register programming on USB, and common registration/debugfs success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/usb_sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac.h

Purpose: Shared Connac-family declarations for packet types, descriptor sizes, chip predicates, PM/coredump state, TXP layouts, inline helpers, and exported MAC/PM utility prototypes used by mt7615 and newer MediaTek chips.

Important APIs and types: `enum rx_pkt_type` classifies RX packet/event types. `struct mt76_connac_pm` stores power-save enable flags, wake refs, queued skbs, work items, waitqueue, mutex, idle timeout, and PM statistics. `struct mt76_connac_coredump` buffers firmware crash messages. `struct mt76_connac_fw_txp`, `struct mt76_connac_hw_txp`, and `struct mt76_connac_txp_common` define firmware and hardware TX pointer descriptors. Chip helpers such as `is_mt7615()`, `is_mt7663()`, `is_connac_v1()`, `is_connac2()`, and `is_mt799x()` drive variant behavior. Inline helpers map channel width, AC queues, TXWI to TXP, antenna masks to SPE index, IRQ reenablement, PM refs, skip-fw-PM decisions, and PM-aware mutex acquisition.

Control flow and integration: Drivers include this header to decide descriptor formats, PM transitions, and chip feature paths. mt7615 uses its PM mutex macros over `mt76_connac_mutex_acquire/release()`, TX paths call TXP helpers, interrupt code uses `mt76_connac_irq_enable()`, and USB/SDIO/PCI paths depend on chip predicates.

State and persistence: Defines host runtime PM, token/TXP, coredump, and pending TX state. Persistent firmware crash data may be buffered in memory for coredumps but not written here.

Dependencies: Core `mt76.h`, mac80211/nl80211 types, kernel workqueues/spinlocks/mutexes, and descriptor bit macros from companion MAC headers.

Risks: Chip predicate mistakes route devices through wrong descriptor, PM, or register paths. PM ref accounting must stay balanced; underflow or skipped unref can prevent sleep or allow sleep with active traffic. TXP layouts are DMA ABI and must match unmap logic. `mt76_connac_irq_enable()` schedules tasklets after mask changes, which assumes caller context can tolerate immediate bottom-half work.

Test signals: Build coverage across Connac drivers, PM wake/sleep stats, TX completion/unmap correctness, chip-specific feature selection, coredump collection, and packet flow on all supported buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac2_mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac2_mac.h

Purpose: Bitfield and enum contract for Connac2-generation MAC TX/RX descriptors, TX status, TX free events, RX vectors, HE radiotap decoding, and copy-engine TX metadata.

Important APIs and constants: Defines TX header formats, packet types, queue IDs, TX status formats, TX free masks, TXD DW0-DW8 fields, TX rate encoding, TXS fields, RXD normal/group fields, PRXV/CRXV rate vector fields, copy-engine parse lengths, CT info flags, MCU port queue IDs, port IDs, and fragment IDs.

Control flow and integration: `mt76_connac_mac.c` consumes these masks to write TXWI descriptors, parse TX status, decode RX rates/HE radiotap data, reverse mesh header translation, and free TXWI tokens. mt7615 USB/SDIO code also shares constants like `MT_CT_PARSE_LEN` and queue IDs for descriptor setup.

State and persistence: Describes hardware-visible descriptor and report state. No host state is stored.

Dependencies: Linux bitfield macros and mac80211 rate/descriptor semantics through including C files.

Risks: Constants are hardware ABI. Connac2 and Connac3 headers intentionally have similar names with different bit positions; mixing them corrupts descriptor parsing. Some fields are overloaded by bus or chip generation, requiring caller-side checks like `mt76_is_mmio()` and `is_connac2()`.

Test signals: TX descriptor correctness, TX status rate/stat updates, RX rate/radiotap decoding, mesh header translation, BA aggregation start, and traffic on Connac2 chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac2_mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac3_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac3_mac.c

Purpose: Connac3 RX vector to radiotap decoder for HE and EHT metadata.

Important APIs and functions: `mt76_connac3_mac_decode_he_radiotap()` pushes and fills `ieee80211_radiotap_he` data, including BSS color, LDPC extra symbol, spatial reuse, LTF, TXBF, TXOP, Doppler, format, UL/DL, beam change, RU allocation, and MU metadata. `mt76_connac3_mac_decode_eht_radiotap()` pushes EHT and EHT-USIG TLVs and fills known fields, user info, NSS, beamforming, coding, STA ID, BSS color, TXOP, and bandwidth. Helpers decode HE RU allocation, HE MU data, and push radiotap TLVs.

Control flow: RX status code passes skb, rxv array, and PHY mode after basic RX rate parsing. The functions prepend radiotap metadata to the skb and update `mt76_rx_status` flags. EHT decoding requires `skb_mac_header(skb) == skb->data` because TLVs are pushed at the top of the MAC header and flagged with `RX_FLAG_RADIOTAP_TLV_AT_END`.

State and persistence: Mutates skb headroom and `skb->cb` receive status for monitor-mode reporting. No persistent state.

Dependencies: `mt76_connac3_mac.h` bitfields, `mt76_connac.h`, mac80211 radiotap HE/EHT structures, and skb push semantics.

Risks: skb headroom and ordering are critical; EHT warns and returns if the MAC header is not positioned as expected. Incorrect rxv indexes or bit masks produce misleading monitor captures. NSS is intentionally zero-based for radiotap compatibility, so changes can break userspace decoders.

Test signals: Monitor-mode captures in Wireshark/iw, HE SU/MU/TB radiotap fields, EHT TLV presence, no skb headroom corruption, and exported symbol use by Connac3 drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac3_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac3_mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac3_mac.h

Purpose: Bitfield and enum contract for Connac3-generation MAC descriptors, RX descriptors, RX vectors, TX status/free reports, and EHT/HE radiotap source fields.

Important APIs and constants: Defines queue IDs, copy-engine parse lengths, RXD DW0-DW4 fields, group fields, PRXV fields, CRXV HE/EHT fields, TX header/packet/port/management/fragment enums, CT flags, TXD DW0-DW9 fields, TXP buffer/token fields, TX rate encoding, TXFREE fields, and TXS fields.

Control flow and integration: `mt76_connac3_mac.c` uses RX vector masks for HE/EHT radiotap decoding. Connac3 driver TX/RX paths use TXD, TXP, TXFREE, and TXS constants to build descriptors and parse hardware reports.

State and persistence: Describes DMA-visible descriptors and RX/TX hardware reports only.

Dependencies: Kernel bitfield macros and mac80211 PHY/radiotap semantics through consuming files.

Risks: Connac3 masks differ from Connac2, including wider WLAN IDs, RX band indexes, TX rate/NSS fields, and EHT fields. Copying Connac2 logic without adjusting bit positions is a high-risk regression. Some mask definitions are easy to misread, so tests should validate actual decoded captures.

Test signals: Connac3 TX/RX traffic, TX status and free event parsing, monitor-mode HE/EHT radiotap output, aggregation behavior, and descriptor validation under multiple bandwidth/NSS modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac3_mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac_mac.c

Purpose: Shared Connac MAC/PM implementation for PPE thresholds, power-save queuing, TXP setup/unmap, TX queue init, TXWI writing, TX status parsing, HE radiotap decoding, RX header translation repair, RX rate fill, aggregation checks, and token cleanup.

Important APIs and functions: `mt76_connac_gen_ppe_thresh()` generates HE PPE thresholds. PM functions `mt76_connac_pm_wake()`, `mt76_connac_power_save_sched()`, `mt76_connac_pm_queue_skb()`, `mt76_connac_pm_dequeue_skbs()`, and `mt76_connac_free_pending_tx_skbs()` coordinate non-USB low-power transitions and pending TX. TX functions `mt76_connac_write_hw_txp()`, `mt76_connac_txp_skb_unmap()`, `mt76_connac_init_tx_queues()`, and `mt76_connac2_mac_write_txwi()` implement descriptor setup. Status/RX functions `mt76_connac2_mac_fill_txs()`, `mt76_connac2_mac_add_txs_skb()`, `mt76_connac2_mac_decode_he_radiotap()`, `mt76_connac2_reverse_frag0_hdr_trans()`, and `mt76_connac2_mac_fill_rx_rate()` parse hardware reports. Cleanup helpers `mt76_connac2_tx_check_aggr()`, `mt76_connac2_txwi_free()`, and `mt76_connac2_tx_token_put()` complete and release TX resources.

Control flow: TX descriptor writing chooses queue and packet format from qid, beacon/discovery state, bus type, WMM index, and VIF/phy indexes; then fills 802.3 or 802.11 descriptor fields and optional fixed-rate fields. TX status maps TXS reports into mac80211 ACK/rate/stat state. RX decoding converts PRXV/CRXV vectors into `mt76_rx_status` and radiotap headers. PM wake queues work and waits for `MT76_STATE_PM` to clear; sleep scheduling defers firmware PM control until idle. Token cleanup unmaps DMA TXP buffers, completes skb status, checks BA aggregation, and resets pending management counters.

State and persistence: Mutates PM wake counters/stats/pending queues, TXWI cache and token IDR, wcid rate/statistics/aggregation state, skb data/headroom, rx status cb, mac80211 TX status queues, and mt76 TX queues. No disk persistence.

Dependencies: `mt76_connac.h`, Connac2 MAC bitfields, mt76 DMA/queue/status APIs, mac80211 radiotap/rate/aggregation APIs, skb manipulation, DMA unmap APIs, and chip predicates.

Risks: PM ref accounting and queued skb handling can deadlock queues or drop packets if imbalanced. TXWI bitfields vary by chip and bus; wrong packet format, qid, WLAN index, PN/protection bits, or fixed-rate fields cause firmware/hardware TX failures. TXP unmap must match firmware vs hardware TXP layout and last-buffer flags. RX/radiotap decoding trusts rxv indexes and skb headroom. `mt76_connac2_mac_decode_he_mu_radiotap()` mutates a static `mu_known` template for Connac2-specific flags, so changes should consider cross-call behavior.

Test signals: Traffic on Connac v1/v2 devices, suspend/power-save wake under TX, TX status ACK/rate updates, BA session auto-start, token drain on reset/unload, monitor-mode HE radiotap correctness, mesh header translation, and DMA debug checks for unmap balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac_mac.c -->
