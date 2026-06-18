# Research: subset-b-004859

Grouped research for MediaTek mt76 MT7925/MT792x and MT7996 wireless driver files. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mt7925.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mt7925.h

## Purpose
This header is the MT7925-specific public contract for the mt76 MT792x common driver family. It layers chip constants, firmware event structures, CLC/regulatory records, EEPROM offsets, TX power tables, ring IDs, and MT7925 function prototypes on top of `mt792x.h` and the MT7925 register map.

## Important APIs, Types, And Functions
Important constants include PCI/USB ring sizes, EEPROM size/block size, token count, beacon-rate table index, SKU power table sizing, and firmware image names inherited through `mt792x.h`. The file defines firmware event and command payload structures such as `mt7925_mcu_hif_ctrl_basic_tlv`, ROC grant/beacon-loss/RSSI monitor events, CLC country segment records, and the large `mt7925_txpwr` per-rate power report. It declares the MT7925 mac80211 ops object and cross-file entry points for registration, firmware load, MCU operations, MAC init/reset, TXWI preparation/freeing, USB/SDIO TX helpers, regulatory updates, testmode, SAR, sniffer, ROC, beacon offload, and runtime PM.

## Control Flow
No executable control flow lives here, but it shapes compilation and linkage. Bus probe files call the declared `mt7925_register_device()`, `mt7925e_mcu_init()`, `mt7925u_mcu_init()`-backed paths, `mt7925_run_firmware()`, `mt7925_mcu_set_eeprom()`, `mt7925_mac_init()`, and `__mt7925_start()`. MAC, MCU, regulatory, and testmode files exchange the packed event structures declared here when parsing firmware events or building MCU commands.

## State And Persistence
The header describes persistent hardware and firmware state rather than storing it directly: EEPROM content at fixed offsets, CLC country/channel capabilities, `dev->has_eht`/CLC-derived EHT support, ROC tokens and grant state, WTBL/TXWI bookkeeping, and rate-power tables queried from firmware. The packed structures are ABI-sensitive firmware contracts and must remain byte-exact.

## Dependencies And Integration Points
It depends on Linux bitfield/endian helpers through included mt76 headers, shared `mt792x` objects, and MT7925 register definitions. Integration points are broad: mac80211 callbacks, mt76 TX/RX queues, connac MCU command helpers, regulatory/SAR code, USB/SDIO and PCI bus files, debugfs, and testmode.

## Risks
The main risks are ABI drift with firmware, wrong packed layout, mismatched ring IDs, and stale prototypes when common MT792x behavior changes. Power-table and CLC structure size changes are especially risky because regulatory and SAR code index variable firmware blobs. Ring constants must match the bus-specific queue initialization in PCI/USB paths.

## Test Signals
Build coverage across PCI and USB MT7925 modules, successful firmware load, parsed ROC/beacon/RSSI events, valid EEPROM/SAR power reports, regulatory country changes, testmode netlink commands, and reset recovery all validate this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mt7925.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/pci.c

## Purpose
This file implements the MT7925E PCIe bus driver. It matches PCI IDs, wraps register access through MT7925 remap windows, initializes WFDMA rings and interrupts, wires mt76 driver/HIF operations, registers the mac80211 device, and handles suspend/resume/remove/shutdown.

## Important APIs, Types, And Functions
The public module entry is `module_pci_driver(mt7925_pci_driver)`. Key helpers are `mt7925_pci_probe()`, `mt7925_pci_remove()`, `mt7925_pci_suspend()`, `_mt7925_pci_resume()`, `mt7925_dma_init()`, and `mt7925e_unregister_device()`. Register remapping is implemented by `__mt7925_reg_addr()`, `mt7925_reg_map_l1()`, `mt7925_reg_map_l2()`, `mt7925_reg_remap_restore()`, and bus-op wrappers `mt7925_rr()/wr()/rmw()`.

## Control Flow
Probe enables the PCI device, maps BAR0, enables bus mastering and IRQ vectors, sets a 32-bit DMA mask, optionally disables ASPM, clones mac80211 ops based on firmware features, allocates `mt792x_dev`, installs remapped bus ops, takes driver ownership from firmware, reads chip revision, resets WFSYS, requests IRQ, initializes DMA queues, then calls `mt7925_register_device()`. DMA setup disables WFDMA, creates data/MCU/FWDL TX rings, event/data RX rings, initializes NAPI, and enables DMA. Suspend aborts ROC, waits for regulatory updates to finish, enables deep sleep and HIF suspend, waits for idle, disables NAPI/DMA/interrupts, then gives ownership to firmware. Resume reacquires driver ownership, conditionally reinitializes WPDMA, reenables interrupts/DMA/NAPI, resumes HIF, restores deep-sleep policy, and reapplies regulatory state.

## State And Persistence
Persistent driver state includes `dev->backup_l1/l2` remap registers, ASPM support, `hif_idle`, `hif_resumed`, PM suspended state, IRQ masks, NAPI state, queued MCU response SKBs, DMA queues, and firmware/regulatory flags. Suspend persists country information and deep-sleep preference but tears down active host DMA/interrupt state until resume.

## Dependencies And Integration Points
The file integrates Linux PCI PM, mt76 MMIO/DMA/NAPI, connac PM ownership, MT7925 MCU/MAC routines, regulatory update code, and the shared `mt792x_dma`/reset helpers. Its `mt76_driver_ops` bind PCI TX preparation, RX parsing, station events, and survey update callbacks to the rest of the driver.

## Risks
Register remapping is fragile: the L1/L2 backup/restore sequence must bracket indirect accesses without leaving the HIF window pointing at the wrong range. Suspend/resume has several timeout paths where NAPI, deep sleep, HIF suspend, and ownership state must be restored correctly. DMA initialization and reset depend on exact ring IDs and interrupt masks. ASPM and ownership polling timing can expose platform-specific failures.

## Test Signals
PCI probe/remove, firmware load, association traffic, module unload, ASPM on/off, suspend/resume/freeze/thaw/poweroff/restore, regulatory update during suspend, IRQ/NAPI activity, WPDMA reset, and firmware reset recovery are the primary validation signals. Timeout paths should trigger `mt792x_reset()` without leaking IRQs, NAPI, or queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/pci_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/pci_mac.c

## Purpose
This file contains MT7925 PCIe MAC-side TX preparation and reset recovery. It builds PCIe TXWI/TXP descriptors, manages mt76 TX tokens, and reinitializes firmware, EEPROM, MAC, queues, interrupts, and runtime state after a PCIe MAC reset.

## Important APIs, Types, And Functions
`mt7925e_tx_prepare_skb()` is the PCIe `tx_prepare_skb` callback. `mt7925_tx_token_put()` frees all outstanding TXWI token cache entries. `mt7925e_mac_reset()` is the PCIe HIF reset callback used through `struct mt792x_hif_ops`.

## Control Flow
TX preparation validates packet length, falls back to the global WCID when needed, stores the SKB in a TXWI cache object, consumes an mt76 token, periodically requests TX status for stations, registers the SKB for TX status, writes an MT7925 TXWI, zeroes and fills the hardware TXP descriptor, and transfers SKB ownership to the queue. Reset takes driver PM ownership, frees pending TX SKBs, disables interrupts, sets reset bits, wakes MCU waiters, purges MCU responses, disables workers/NAPI, frees tokens, resets WPDMA, reenables NAPI and schedules RX/TX polling, clears firmware assertion state, reenables interrupts, reacquires firmware/driver ownership, reruns firmware, reapplies EEPROM, initializes MAC, and starts the PHY.

## State And Persistence
Token state lives in `dev->mt76.token`, `token_count`, and TXWI cache entries. Reset mutates `MT76_RESET`, `MT76_MCU_RESET`, `fw_assert`, TX worker state, NAPI state, MCU response queues, and hardware interrupt registers. Firmware, EEPROM, and MAC state are reloaded rather than preserved in place.

## Dependencies And Integration Points
The file depends on mt76 token/status infrastructure, `mt7925_mac_write_txwi()`, `mt76_connac_write_hw_txp()`, common WPDMA reset code, MT7925 firmware and EEPROM setters, MAC init, and the shared MT792x PM ownership functions. It is selected by PCI probe through `mt76_driver_ops`.

## Risks
Token leaks or double-frees can corrupt TX completion. Reset ordering is high risk: interrupts and NAPI must be quiesced before token destruction and reenabled only after WPDMA is valid. Firmware rerun failure paths must still clear reset state and reenable TX worker only when safe. Periodic TX status requests depend on per-station `last_txs` timing.

## Test Signals
Heavy TX, management TX, TX status reporting, firmware assert/reset, queue cleanup, IDR token consistency, NAPI disable/enable lockdep checks, and recovery into a working association validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/pci_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/pci_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/pci_mcu.c

## Purpose
This file provides the MT7925 PCIe MCU transport glue. It installs MCU send/parse operations, routes firmware scatter download commands to the FWDL queue, and performs initial PM ownership plus firmware boot.

## Important APIs, Types, And Functions
`mt7925_mcu_send_message()` fills the MT7925 MCU header and submits the SKB to either `MT_MCUQ_WM` or `MT_MCUQ_FWDL`. `mt7925e_mcu_init()` installs a static `mt76_mcu_ops` table using `mt7925_mcu_parse_response()` and starts firmware.

## Control Flow
MCU send calls `mt7925_mcu_fill_message()`, sets the MCU timeout to three seconds, selects FWDL for `MCU_CMD(FW_SCATTER)`, and queues the raw SKB to the selected mt76 MCU queue. MCU init assigns the ops table, gives firmware then driver PM ownership through PCIe helpers, disables PCIe L0s in `MT_PCIE_MAC_PM`, runs firmware, and cleans the FWDL queue after boot.

## State And Persistence
The file mutates `dev->mt76.mcu_ops`, `mdev->mcu.timeout`, PCIe PM register L0s state, and FWDL queue contents. Firmware boot state is established by `mt7925_run_firmware()` and later consumed by register/device init.

## Dependencies And Integration Points
It depends on the shared MT7925 MCU header/response helpers, mt76 MCU queueing, PCIe PM ownership helpers, and `mt7925_run_firmware()`. PCI probe exposes this through `hif_ops.mcu_init`.

## Risks
Routing the wrong command to the wrong queue can hang firmware download. Header fill errors must not leak the SKB into a queue. Ownership sequencing and L0s disable timing are hardware-sensitive, and FWDL cleanup must run after firmware load to avoid stale descriptors.

## Test Signals
Successful patch/RAM download, MCU command response parsing, timeout behavior, FWDL queue cleanup, and reset-time MCU reinitialization validate this transport layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/pci_mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/regd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/regd.c

## Purpose
This file implements MT7925 regulatory CLC handling. It applies country-list constraints to channel availability and EHT support, responds to cfg80211 regulatory notifications, handles firmware CLC updates, and supports automatic 11d-driven country changes when allowed.

## Important APIs, Types, And Functions
Exports are `mt7925_regd_clc_supported()`, `mt7925_regd_be_ctrl()`, `mt7925_mcu_regd_update()`, `mt7925_regd_notifier()`, `mt7925_regd_change()`, and `mt7925_regd_init()`. The `disable_clc` module parameter disables CLC support. Important internal logic includes ACPI MTCL interpretation, CLC BE-control rule scanning, and channel-flag updates for UNII-4 through UNII-8.

## Control Flow
Regulatory notification records user-initiated changes, ignores repeated or late world-domain updates, copies alpha2/DFS/env into mt76 state, marks `regd_change`, and either defers during suspend or calls `mt7925_mcu_regd_update()`. The update path sets `regd_in_progress`, takes the MT792x mutex/PM reference, sends CLC to firmware, updates BE/EHT capability, disables unavailable 5.9/6 GHz channels, sends the channel domain, reapplies SAR TX power, then clears state and wakes waiters. The 11d change helper validates alpha2, CLC support, user override state, and current alpha2 before either issuing `regulatory_hint()` or directly setting CLC for non-11d chips.

## State And Persistence
Persistent state includes `mdev->alpha2`, `mdev->region`, `dev->country_ie_env`, `dev->regd_user`, `dev->regd_change`, `dev->regd_in_progress`, `dev->has_eht`, `phy->clc_chan_conf`, and channel flags in the wiphy bands. Updates can be postponed across suspend and replayed by PCI resume.

## Dependencies And Integration Points
The file integrates cfg80211 regulatory callbacks, ACPI MTCL helpers from `mt792x_acpi_sar.c`, MT7925 MCU CLC/channel-domain/SAR commands, wiphy band/channel flag storage, PM mutex handling, and the PCI suspend/resume wait path.

## Risks
Regulatory handling is high impact: incorrect CLC interpretation can expose disabled 5.9/6 GHz channels or incorrectly clear EHT support. The code mutates channel flags additively and does not visibly clear previous disables in this path, so update sequencing depends on cfg80211/mac80211 reset behavior. Suspended updates rely on resume replay. User-set regulatory domains intentionally block automatic 11d changes.

## Test Signals
Country changes for world, US/EU/6 GHz countries, user override, 11d beacons, suspend during regdom change, ACPI MTCL present/absent cases, `disable_clc`, USB exclusion, EHT flag changes, and SAR reapplication validate the behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/regd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/regd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/regd.h

## Purpose
This header exposes the MT7925 regulatory helper API to bus, MCU, init, and mac80211-facing code.

## Important APIs, Types, And Functions
It declares `mt7925_mcu_regd_update()`, `mt7925_regd_be_ctrl()`, `mt7925_regd_notifier()`, `mt7925_regd_clc_supported()`, `mt7925_regd_change()`, and `mt7925_regd_init()`. These are the external hooks used for cfg80211 regulatory notifier registration, 11d country changes, CLC updates, and EHT/channel capability recalculation.

## Control Flow
No runtime logic is implemented here. The header enables PCI resume and regulatory callback code to call into `regd.c` while keeping the file boundaries explicit.

## State And Persistence
No state is stored here. The declared functions manipulate `mt792x_dev`, `mt792x_phy`, wiphy regulatory flags, alpha2/country environment state, CLC data, and channel flags.

## Dependencies And Integration Points
It includes `mt7925.h`, so consumers get MT792x/MT7925 type definitions and firmware environment enums. It is included by PCI and regulatory-related MT7925 sources.

## Risks
The main risk is API mismatch with `regd.c` or missing declarations when regulatory behavior changes. Since it includes the large MT7925 header, circular include changes can have broad build impact.

## Test Signals
Compilation of MT7925 PCI/USB and regulatory code, plus successful notifier registration and resume-time `mt7925_mcu_regd_update()` calls, validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/regd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/regs.h

## Purpose
This header defines MT7925-specific register addresses and bitfields that extend the shared MT792x register map. It covers MDP filtering, WFDMA interrupt/ring layout, HIF remap registers, WFSYS reset, and WTBL update fields.

## Important APIs, Types, And Functions
Important macros include `MT_MDP_*` receive filter/forwarding fields, `MT_WFDMA0_HOST_INT_ENA`, MT7925 RX/TX interrupt masks, data/event ring bases, `MT_HIF_REMAP_L1/L2` fields, `MT_WFSYS_SW_RST_B`, and WTBL update helpers. There are no functions.

## Control Flow
The macros are consumed by PCI register remap and DMA setup, shared MT792x DMA/interrupt code, MAC RX filter setup, and WTBL update routines. They determine which hardware rings drive NAPI and which interrupt bits are enabled.

## State And Persistence
Register writes through these definitions persist in hardware until reset or reconfiguration. HIF remap state is backed up/restored in the PCI file, while WFDMA interrupt and ring state is managed during DMA init/reset/suspend.

## Dependencies And Integration Points
It includes `../mt792x_regs.h` and is included by `mt7925.h`. It integrates with mt76 MMIO helpers, PCI bus ops, DMA queue allocation, interrupt masking, MAC initialization, and WTBL management.

## Risks
Wrong bit definitions can misroute interrupts, break register reads through remap windows, corrupt WTBL updates, or direct RX management/control frames to the wrong destination. Conditional `MT_HIF_REMAP_BASE_L2` differs under `CONFIG_MT76_DEV`, which must match build/runtime access expectations.

## Test Signals
Interrupt delivery on all enabled rings, successful register reads above direct MMIO range, WFDMA reset/init, RX filter behavior, and WTBL update correctness validate this map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/testmode.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/testmode.c

## Purpose
This file implements MT7925 vendor testmode netlink commands for RF/test control and query responses. It lets monitor-mode users switch test mode on/off, send firmware test-control commands, and query testmode/RX-stat events.

## Important APIs, Types, And Functions
The exported callbacks are `mt7925_testmode_cmd()` and `mt7925_testmode_dump()`. Internal helpers are `mt7925_tm_set()` and `mt7925_tm_query()`. The file defines MT7925-specific nested netlink attributes, exact-length policies, `mt7925_tm_cmd`, and `mt7925_tm_evt`/response sizing.

## Control Flow
Command handling requires the PHY to be running and the hw config to be monitor mode. The set path parses nested driver data, copies it into an RF test command, locks the mt76 mutex, detects mode-switch actions, disables runtime PM and takes driver ownership before entering test mode, marks `phy->test.state`, sends `MCU_UNI_CMD(TESTMODE_CTRL)`, and restores normal test/PM state when switching back. The dump path accepts only one callback iteration, validates running/monitor/testmode state, sends either `MCU_UNI_QUERY(TESTMODE_CTRL)` or `MCU_UNI_QUERY(TESTMODE_RX_STAT)` based on the padding command selector, copies 512 bytes from the event payload, and emits `MT7925_TM_ATTR_RSP`.

## State And Persistence
State includes `phy->test.state`, `pm->enable`, pending PM work, and firmware testmode state. Query responses are transient SKBs. Testmode deliberately forces full-power driver ownership while active.

## Dependencies And Integration Points
The file depends on mac80211 testmode plumbing, mt76 testmode policies, nested netlink parsing, MT7925 MCU command IDs and RF test command structures, and MT792x PM ownership helpers.

## Risks
The query path uses a fixed 512-byte copy from `skb->data + 8`; firmware response size assumptions must hold. Entering testmode disables PM and cancels work, so failed transitions can leave PM/test state inconsistent. The command selector is read from raw padding bytes, which is ABI-sensitive. Requiring monitor mode prevents accidental use but can surprise tooling.

## Test Signals
Netlink set/query commands in monitor mode, transition to test and back to normal mode, PM reenable after normal transition, firmware response lengths, invalid attribute rejection, and single-dump iteration behavior validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/testmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/usb.c

## Purpose
This file implements the MT7925U USB bus driver. It matches USB IDs, sends MCU messages over USB endpoints, powers on and initializes USB DMA, registers the shared MT7925 device, and handles USB reset/suspend/resume/disconnect through MT792x USB helpers.

## Important APIs, Types, And Functions
The module entry is `module_usb_driver(mt7925u_driver)`. Key functions are `mt7925u_probe()`, `mt7925u_mcu_send_message()`, `mt7925u_mcu_init()`, `mt7925u_mac_reset()`, and PM callbacks `mt7925u_suspend()`/`mt7925u_resume()`. Driver ops select `mt7925_usb_sdio_tx_prepare_skb()`, `mt7925_usb_sdio_tx_complete_skb()`, `mt7925_usb_sdio_tx_status_data()`, MT7925 RX and station callbacks, and shared survey updates.

## Control Flow
Probe clones mac80211 ops and replaces stop with USB stop, allocates `mt792x_dev`, resets the USB device, initializes mt76 USB state and bus ops, reads revision, resets WFSYS if firmware is already ready, powers on the MCU, allocates MCU/data queues, initializes USB DMA, sets max TX fragments based on scatter-gather support, then registers the MT7925 device. MCU send fills the MT7925 message header, chooses in-band command or AC_BE/FWDL endpoint, prepends USB/SDIO header, pads to a four-byte boundary plus tail, sends a bulk message, and frees the SKB. Reset stops RX/TX, resets WFSYS, resumes RX, powers on MCU, initializes DMA, reloads firmware/eeprom/MAC, and restarts the PHY. Suspend requests HIF suspend and waits for idle before stopping USB RX/TX. Resume polls firmware suspend flags, optionally reinitializes DMA, resumes RX, clears HIF suspend, and resets on failure.

## State And Persistence
State includes USB interface data, device reference, bus ops, MCU ops, FWDL mode bit in `MT_UDMA_TX_QSEL`, `MT76_STATE_MCU_RUNNING`, PM suspended/HIF flags, queue allocations, scatter-gather TX fragment capability, and firmware suspend event bits.

## Dependencies And Integration Points
It integrates Linux USB core, mt76 USB queue/control helpers, shared MT792x USB register access and WFSYS reset, MT7925 firmware/MAC/EEPROM code, and connac HIF suspend commands.

## Risks
USB control and bulk endpoint selection must match firmware boot state. Padding/header length errors break MCU commands. Resume reinitialization depends on firmware SER suspend bits and DMA reinit detection. Error paths must release USB references, interface data, queues, and mt76 device memory correctly.

## Test Signals
USB probe for MediaTek and Netgear IDs, firmware load, traffic with and without SG, suspend/resume/reset_resume, unplug/disconnect, forced MAC reset, MCU command responses, and queue teardown under errors validate this driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x.h

## Purpose
This is the shared MT792x family header. It defines firmware names, chip capabilities, per-vif/station/link/phy/device state, HIF operation indirection, common helpers for MLO-aware link lookup, and prototypes for shared core, MAC, DMA, USB, PM, ACPI SAR, and firmware routines used by MT7902/MT7920/MT7921/MT7922/MT7925.

## Important APIs, Types, And Functions
Core structures are `mt792x_link_sta`, `mt792x_sta`, `mt792x_bss_conf`, `mt792x_vif`, `mt792x_phy`, `mt792x_irq_map`, `mt792x_hif_ops`, and `mt792x_dev`. Inline helpers convert mac80211 objects to MT792x link state, map RX channel frequencies, choose firmware names, add USB/SDIO headers, and detect WPDMA reinit need. Prototypes cover TX/stop/interface removal, TSF, channel context, debugfs/ethtool stats, DMA reset/enable, IRQ/NAPI, firmware load, PM ownership, USB helpers, and ACPI SAR.

## Control Flow
No direct executable logic beyond inline helpers lives here. Bus drivers install `hif_ops` so common code can call init/reset/MCU/ownership methods without knowing PCI/USB/SDIO details. mac80211 callbacks use the MLO helpers to select deflink or per-link station/vif state. Firmware selection helpers dispatch by chip ID.

## State And Persistence
The header defines the persistent in-memory state for this driver family: firmware/reset flags, EHT and regulatory bits, PM/coredump state, work items/timers, CLC blobs, ACPI SAR pointer, MLO valid links and PM state, per-link WCIDs, queue params, RSSI EWMA, ROC tokens, remap backups, and MAC address list. Hardware state is accessed through mt76 bus ops and reset through HIF operations.

## Dependencies And Integration Points
It depends on mt76 connac MCU, mt76 register definitions, mac80211/cfg80211 MLO types, ACPI SAR structures, Linux work/timer/interrupt APIs, and bus-specific files. It is the central include for MT7925 PCI/USB, shared core/DMA/MAC, regulatory, and ACPI SAR code.

## Risks
Structure layout is driver ABI with mac80211 private areas and mt76 WCID assumptions; several comments require fields to be first. MLO helpers use RCU protected dereferences and require the mt76 mutex. HIF ops must be fully populated for a bus or common PM/reset code will dereference NULL. Firmware-name selection must track chip IDs and packaging.

## Test Signals
Builds across all MT792x bus/chip configs, mac80211 private-size correctness, MLO and non-MLO interface/station paths, firmware selection, PM ownership calls through HIF ops, USB/PCI reset paths, and KASAN/RCU/lockdep around link dereferences validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_acpi_sar.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_acpi_sar.c

## Purpose
This file parses MediaTek ACPI SAR and country-list tables for MT792x devices. It reads ACPI methods, validates dynamic/geographic SAR tables, initializes per-frequency power limits, exposes firmware flag bits, and converts MTCL country lists into 5.9 GHz, 6 GHz, and 11be policy configuration.

## Important APIs, Types, And Functions
Exports are `mt792x_init_acpi_sar()`, `mt792x_init_acpi_sar_power()`, `mt792x_acpi_get_flags()`, and `mt792x_acpi_get_mtcl_conf()`. Internal readers handle ACPI methods `MTCL`, `MTDS`, `MTGS`, and `MTFG`. Power helpers include `mt792x_asar_get_geo_pwr()` and `mt792x_asar_range_pwr()`. Country-list parsing uses static all/EU/BE country tables and version-specific MTCL map helpers.

## Control Flow
Initialization allocates `mt792x_acpi_sar`, then tries MTCL, MTDS, optional MTGS, and optional MTFG reads. Each ACPI read evaluates a package method, validates integer elements, and stores byte tables in devm memory. Dynamic and geographic tables are validated against version-specific record sizes and min/max counts. SAR power initialization walks cfg80211 SAR ranges, assigns default ranges when requested, and clamps existing or default power by ACPI dynamic plus geographic limits. MTCL lookup first parses v3 BE policy, then older 6 GHz/5.9 GHz policy, and returns an aggregate config or invalid.

## State And Persistence
Parsed ACPI data persists in `phy->acpisar` for device lifetime. SAR limits are materialized into `phy->mt76->frp[]`. Geographic power depends on `phy->mt76->dev->region`. MTCL config is queried later by MT7925 regulatory code to disable channels or EHT.

## Dependencies And Integration Points
The file integrates Linux ACPI evaluation, cfg80211 SAR capabilities, mt76 frequency-range power storage, MT7925 regulatory CLC handling, and firmware feature flags. It is compiled only under `CONFIG_ACPI`, with stubs in `mt792x.h` otherwise.

## Risks
ACPI package validation is strict but byte-sized; malformed platform tables can disable SAR/CLC features silently after freeing the table. Versioned unions require `asar->ver` to match the populated pointer type. Country table mappings are hard-coded and must track platform firmware definitions. Power clamping assumes SAR capability ranges align with ACPI FRP indices.

## Test Signals
Systems with and without MTCL/MTDS/MTGS/MTFG, versions 1/2/3, all/FCC/ETSI/world regions, cfg80211 SAR user specs, 6 GHz/5.9 GHz country changes, and `mt7925_regd_channel_update()` effects validate the parser.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_acpi_sar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_acpi_sar.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_acpi_sar.h

## Purpose
This header defines the packed ACPI SAR table layouts and constants used by the MT792x ACPI SAR parser.

## Important APIs, Types, And Functions
It defines min/max counts for dynamic/geographic/flag tables, ACPI method names `MTCL`, `MTDS`, `MTGS`, `MTFG`, invalid MTCL sentinel, and packed structures for dynamic SAR v1/v2, geographic SAR v1/v2, country-list v1/v3, flag tables, and the aggregate `mt792x_acpi_sar` container. There are no functions.

## Control Flow
The parser in `mt792x_acpi_sar.c` casts ACPI byte packages to these structures after validating package length. Version fields select which union view is valid and which flexible array record sizes are used.

## State And Persistence
Instances are allocated with devm lifetime and stored in `phy->acpisar`. The flexible arrays hold platform-provided regulatory and power-limit tables; they are treated as immutable after initialization.

## Dependencies And Integration Points
The header is included by `mt792x.h` and therefore visible to MT792x driver files. It relies on Linux bitfield/flexible-array conventions through included kernel headers.

## Risks
Packed layout and flexible arrays must match ACPI firmware exactly. The include guard name still says `MT7921`, which is cosmetic but could confuse maintenance. Adding table versions requires updating both this header and parser validation.

## Test Signals
Compilation under `CONFIG_ACPI`, correct parsing of v1/v2/v3 ACPI method payloads, and SAR/MTCL behavior on real platform firmware validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_acpi_sar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_core.c

## Purpose
This file provides shared MT792x mac80211/core behavior: TX routing with PM gating, stop and interface removal, TSF and channel context helpers, ethtool/station statistics, wiphy capability initialization, firmware feature probing, PM ownership wrappers, firmware loading, WCID initialization, and MAC address list generation.

## Important APIs, Types, And Functions
Exports include `mt792x_tx()`, `mt792x_stop()`, `mt792x_remove_interface()`, `mt792x_conf_tx()`, `mt792x_get_stats()`, `mt792x_get_tsf()`, `mt792x_set_tsf()`, `mt792x_tx_worker()`, timers, `mt792x_flush()`, channel context assign/unassign, wakeup, ethtool string/count/stats callbacks, `mt792x_sta_statistics()`, `mt792x_set_coverage_class()`, `mt792x_init_wiphy()`, `mt792x_get_mac80211_ops()`, `mt792x_init_wcid()`, PM ownership wrappers, `mt792x_load_firmware()`, and `mt792x_config_mac_addr_list()`.

## Control Flow
TX selects a WCID from station link state or vif pseudo-station, rewrites MLO addresses for MLD data frames, and either sends immediately under a PM reference or queues the SKB for wake. Stop cancels MAC/PM/reset work, frees pending PM SKBs, optionally disables the MAC in firmware, and clears running state. Interface removal calls the shared BSS cleanup routine under the MT792x mutex. Wiphy init advertises interface combinations based on CNM firmware capability and sets scan, ROC, offload, PS, ACK-signal, channel-switch, and aggregation features. Firmware feature probing reads the firmware trailer release-info tags to decide whether channel context/ROC ops remain native or are replaced by mac80211 emulation. Firmware load restarts MCU, loads patch/RAM images, waits for N9 ready, and enables WoWLAN support under PM.

## State And Persistence
The file mutates PM queues and stats, `mphy` running/PM state, `dev->mt76.wcid[]`, global WCID, vif/omac masks, per-vif queue params, mib/aggr stats, station TX rate/stat state, wiphy capabilities, firmware feature bits, MAC address list, and PM awake/doze counters. Firmware state is persistent after load but reset/replay is handled elsewhere.

## Dependencies And Integration Points
It is tightly integrated with mac80211/cfg80211, mt76 TX/WCID/firmware helpers, connac PM, firmware image format, page-pool/ethtool stats, MLO link APIs, and bus-specific HIF ops.

## Risks
PM gating can reorder or defer TX; failure to wake or unref can stall queues. MLO address rewriting dereferences RCU link objects and assumes valid link IDs. Firmware feature parsing is offset-sensitive and can disable native ROC/channel context if trailer parsing fails. Wiphy flags must match firmware/driver capabilities or mac80211 will call unsupported flows.

## Test Signals
TX under awake/sleep states, MLO station traffic, interface add/remove, TSF read/write, CNM and non-CNM firmware, ethtool stats, station statistics, firmware load failures, WoWLAN exposure, and PM ownership errors validate this shared core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_debugfs.c

## Purpose
This file provides shared MT792x debugfs/seqfile helpers for TX aggregation statistics, hardware/software queue state, and runtime PM statistics/idle timeout controls.

## Important APIs, Types, And Functions
Exports are `mt792x_tx_stats_show()`, `mt792x_queues_acq()`, `mt792x_queues_read()`, `mt792x_pm_stats()`, `mt792x_pm_idle_timeout_set()`, and `mt792x_pm_idle_timeout_get()`. `mt792x_ampdu_stat_read_phy()` is the main internal aggregation-stat printer.

## Control Flow
TX stats take the MT792x mutex, refresh MIB stats, print AMPDU length ranges and BA miss count, then print AMSDU packing histogram. AC queue debug reads PLE empty masks, walks non-empty AC subqueues, selects each queue via `MT_PLE_FL_Q0_CTRL`, and accumulates lengths from `MT_PLE_FL_Q3_CTRL`. Queue read prints mt76 software head/tail/queued counters for data, WM MCU, and FWDL queues. PM stats derive current awake/doze durations from accumulated counters plus current jiffies depending on `MT76_STATE_PM`. Idle timeout setters/getters translate milliseconds to jiffies.

## State And Persistence
The file reads and updates MIB accumulation through shared MAC helpers, reads PLE and queue registers, reports mt76 queue state, and mutates `dev->pm.idle_timeout`. Debugfs changes persist until device removal or another write.

## Dependencies And Integration Points
It depends on `seq_file`, debugfs attribute wiring in chip-specific init code, MT792x register definitions, shared MAC MIB update logic, mt76 queues, and connac PM statistics.

## Risks
Debugfs reads take the device mutex and touch registers, so they must not race with sleep/reset paths. Queue walking assumes PLE register layout and only covers the queues listed. Idle timeout writes can materially alter runtime PM behavior during traffic tests.

## Test Signals
Readable debugfs files during idle and traffic, sane AMPDU/AMSDU counters, queue depth changes under load, PM awake/doze accounting, idle-timeout writes, and no lockdep/reset races validate these helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_dma.c

## Purpose
This file implements shared PCIe/MMIO WFDMA interrupt, NAPI, enable/disable/reset, prefetch, and WFSYS reset handling for MT792x devices.

## Important APIs, Types, And Functions
Exports include `mt792x_irq_handler()`, `mt792x_irq_tasklet()`, `mt792x_rx_poll_complete()`, `mt792x_dma_enable()`, `mt792x_wpdma_reset()`, `mt792x_wpdma_reinit_cond()`, `mt792x_dma_disable()`, `mt792x_dma_cleanup()`, `mt792x_poll_tx()`, `mt792x_poll_rx()`, and `mt792x_wfsys_reset()`. Internal helpers include chip-specific `mt792x_dma_prefetch()` and `mt792x_dma_reset()`.

## Control Flow
The hard IRQ disables host interrupts and schedules a tasklet if initialized. The tasklet reads and acks WFDMA interrupt status, traces it, masks active RX/MCU rings, handles MCU software wake interrupts, disables those sources while NAPI runs, then schedules TX/RX NAPI instances. RX poll completion re-enables the matching interrupt source. DMA enable programs prefetch windows, resets ring pointers, disables delayed interrupts, sets WFDMA global configuration bits, applies MT7925-specific priority settings, marks the dummy reinit bit, and enables TX/RX/MCU interrupts. Reset disables DMA, resets all TX/MCU/RX queues, checks TX status, reenables DMA, and resets RX queues. Poll paths require a PM reference and schedule wake work if the device is asleep.

## State And Persistence
State spans WFDMA registers, mt76 irqmask, NAPI enabled/scheduled state, queue head/tail/ring memory, PM wake counters, `MT_WFDMA_NEED_REINIT`, and WFSYS reset bits. WFSYS reset persists by toggling hardware reset and waiting for init done.

## Dependencies And Integration Points
It integrates mt76 DMA queues, Linux NAPI/tasklets/IRQ, connac PM, MT792x register maps, tracepoints, and bus reset flows in PCI/MT7925 code.

## Risks
Interrupt masking must pair with NAPI completion or rings can stall. PM references in poll functions must not be taken while firmware-owned. DMA busy polling can timeout during suspend/reset. Chip-specific prefetch values and MT7925 priority bits must match hardware ring allocation. WFSYS reset addresses differ for connac2 vs later chips.

## Test Signals
Sustained RX/TX, MCU event traffic, interrupt storm protection, PM sleep/wake while traffic arrives, WPDMA reinit after low power, forced reset, DMA timeout injection, and tracepoint IRQ visibility validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_mac.c

## Purpose
This file provides shared MT792x MAC maintenance: periodic survey/MIB work, timing/coverage programming, MIB/stat accumulation, RX WCID selection, association RSSI tracking, channel accounting, reset scheduling, band initialization, and runtime PM wake/sleep workers.

## Important APIs, Types, And Functions
Exports include `mt792x_mac_work()`, `mt792x_mac_set_timeing()`, `mt792x_mac_update_mib_stats()`, `mt792x_rx_get_wcid()`, `mt792x_mac_assoc_rssi()`, `mt792x_mac_reset_counters()`, `mt792x_update_channel()`, `mt792x_reset()`, `mt792x_mac_init_band()`, `mt792x_pm_wake_work()`, and `mt792x_pm_power_save_work()`.

## Control Flow
Periodic MAC work takes the mutex, updates survey counters, refreshes MIB every second run, releases the mutex, checks TX status, and reschedules itself. Timing setup temporarily disables TX/RX arbitration, programs CCK/OFDM timeouts plus coverage offset, SIFS/slot/EIFS/RIFS, selects CF-end rate, and reenables arbitration. MIB update accumulates counters for FCS/ACK/BA/RTS, TX/RX MPDU/AMPDU, beamforming, AMSDU, and aggregation buckets. Channel update wakes hardware, samples busy/TX/RX/OBSS time, clears OBSS airtime, and schedules power save. PM wake work reacquires driver ownership, dequeues pending SKBs, schedules NAPI or SDIO worker, restarts MAC work, wakes mac80211 queues, and wakes PM waiters. PM save work avoids sleeping during scanning, firmware assert, mutex-held register access, or recent activity; otherwise it gives ownership to firmware and cancels MAC work.

## State And Persistence
State includes `phy->mib`, aggregation stats, survey time/channel state, RSSI EWMA, coverage/slottime/noise, PM awake/doze counters, pending SKB queues, reset work state, firmware assertion flag, and hardware timing/MIB registers.

## Dependencies And Integration Points
It integrates with mt76 survey/TX status, mac80211 interface iteration, connac PM, MT792x register definitions, DMA/NAPI workers, and chip-specific reset work.

## Risks
Register access during PM sleep is guarded but still timing-sensitive. MIB counters are accumulated by reading clear-on-read or rolling hardware registers; missed reads or reset races skew stats. Multicast RX WCID remapping assumes station/vif links remain valid. Power-save scheduling must not sleep during scans or while the mutex protects active register transactions.

## Test Signals
Survey/airtime accuracy, coverage-class changes, association RSSI, stats under traffic, runtime PM wake/sleep cycles, reset work scheduling, scan while idle, and lockdep around PM mutex/register access validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_regs.h

## Purpose
This shared register header maps MT792x hardware blocks: MCU/WFDMA, PLE/PSE, TMAC, DMA, WTBL, AGG, ARB, RMAC, MIB/ETBF, WFDMA rings/interrupts, top/conn-on PM registers, DMASHDL, USB UDMA, and WFSYS reset fields.

## Important APIs, Types, And Functions
It defines register address constructors such as `MT_WF_TMAC()`, `MT_WF_MIB()`, `MT_WFDMA0()`, bitfields for timing/MIB/filter/aggregation/DMA/interrupt state, firmware ownership registers, USB DMA flags, and chip-specific reset/init-done addresses. There are no functions.

## Control Flow
All control flow is indirect: MAC timing/stat code writes TMAC/AGG/MIB/RMAC registers, DMA code programs WFDMA/DMASHDL and interrupt masks, USB code accesses UDMA and endpoint reset controls, and PM code polls conn-on ownership bits.

## State And Persistence
The macros name persistent hardware state. WFDMA registers control queue operation and interrupt delivery; MIB registers accumulate counters; PM ownership bits determine host/firmware control; USB UDMA bits gate TX/RX; WFSYS reset bits reset the wireless subsystem.

## Dependencies And Integration Points
It is included by `mt792x.h`, MT7925 register extensions, shared MAC/DMA/USB files, debugfs, and bus drivers. It relies on Linux bit macros and mt76 register access helpers.

## Risks
Incorrect register offsets or masks can silently corrupt hardware state, especially around WFDMA reset, firmware ownership, and MIB clear-on-read counters. The header spans multiple chip generations, so chip-specific users must select compatible fields.

## Test Signals
Working DMA, IRQ, PM ownership, USB power/reset, MAC timing, MIB stats, queue debugfs output, and reset recovery across MT7921/MT7922/MT7925 variants validate this register map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_trace.c

## Purpose
This file instantiates MT792x tracepoints and exports the low-power event tracepoint symbol.

## Important APIs, Types, And Functions
It defines `CREATE_TRACE_POINTS`, includes `mt792x_trace.h`, and exports `lp_event` with `EXPORT_TRACEPOINT_SYMBOL_GPL()` when sparse checking is not active.

## Control Flow
There is no runtime control flow beyond tracepoint registration generated by the kernel trace infrastructure at build/module load time.

## State And Persistence
Tracepoint metadata persists while the module is loaded. Event payload state is defined in the header and populated by trace callers elsewhere.

## Dependencies And Integration Points
It depends on Linux tracepoint infrastructure and the companion `mt792x_trace.h`. External modules or driver files can use the exported low-power tracepoint.

## Risks
Tracepoint definition and instantiation must remain split exactly once; duplicate `CREATE_TRACE_POINTS` use would cause link errors. Exported tracepoint ABI should be stable for in-tree users.

## Test Signals
Kernel build/link, available `mt792x:lp_event` tracepoint, and successful tracing during PM low-power transitions validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_trace.h

## Purpose
This header declares the MT792x trace event format for low-power state transitions.

## Important APIs, Types, And Functions
It defines trace system `mt792x`, helper macros for device name fields, and `TRACE_EVENT(lp_event)` with arguments `struct mt792x_dev *dev` and `u8 lp_state`. The printed event includes the wiphy name and either `lp ready` or `lp not ready`.

## Control Flow
Callers invoke `trace_lp_event(dev, state)` generated from this declaration. The tracepoint copies the wiphy name and low-power state into the event record and formats it for trace output.

## State And Persistence
The trace event stores transient event records in the kernel tracing buffers when enabled. It does not mutate driver state.

## Dependencies And Integration Points
It depends on Linux tracepoint macros and `mt792x.h` for device types and `mt76_hw()`. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation back at this header.

## Risks
Trace event field names and print format become observable tracing ABI. The helper uses a fixed 32-byte wiphy name buffer and depends on a valid mt76 hw pointer at trace time.

## Test Signals
Successful trace header generation, event enable/disable under ftrace/perf, and correctly formatted low-power PM events validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_usb.c

## Purpose
This file provides shared USB helpers for MT792x devices: vendor register access, block copy, MCU power-on, USB WFDMA/UDMA configuration, endpoint reset options, WFSYS reset, initial reset, stop, disconnect, and cleanup.

## Important APIs, Types, And Functions
Exports include `mt792xu_rr()`, `mt792xu_wr()`, `mt792xu_rmw()`, `mt792xu_copy()`, `mt792xu_mcu_power_on()`, `mt792xu_dma_init()`, `mt792xu_wfsys_reset()`, `mt792xu_init_reset()`, `mt792xu_stop()`, and `mt792xu_disconnect()`. Internal helpers include UHW register access, `mt792xu_wfdma_init()`, `mt792xu_dma_rx_evt_ep4()`, endpoint reset option toggling, and chip-specific WFSYS descriptors for MT7921 and MT7925.

## Control Flow
Register access serializes USB vendor requests under `usb_ctrl_mtx`. DMA init programs WFDMA prefetch, UDMA RX/TX enable, aggregation/padding settings, optional RX-event EP4 routing, and endpoint reset options. WFSYS reset toggles the chip-specific whole-path reset bit through UHW vendor access, waits, optionally selects status, and polls init-done. Initial reset marks reset, wakes MCU waiters, purges responses, stops USB RX/TX, resets WFSYS, clears reset, and resumes RX. Disconnect cancels init work, unregisters initialized devices, resets WFSYS, purges MCU queues, deinitializes USB queues, clears interface data, drops the USB device reference, and frees mt76 state.

## State And Persistence
State includes USB control mutex, vendor request buffers, queue allocation/initialization, UDMA/WFDMA registers, endpoint reset option bits, `MT76_STATE_INITIALIZED`, `MT76_RESET`, MCU response queue, and USB interface data/reference ownership.

## Dependencies And Integration Points
It integrates with Linux USB core, mt76 USB vendor helpers, MT792x register map, MT7925/MT7921 bus drivers, connac MAC stop logic, and mt76 queue cleanup.

## Risks
USB vendor requests must be serialized and chunked correctly. WFSYS reset descriptors differ by chip; wrong done register/mask causes reset timeouts. Endpoint reset options affect hub/device recovery. Disconnect must tolerate partially initialized devices without leaking references or freeing live queues.

## Test Signals
USB register reads/writes/copies, firmware power-on, DMA init with RX event EP4, reset on MT7921 and MT7925, suspend/resume through chip driver, unplug during init, and queue cleanup validate this helper layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/Kconfig

## Purpose
This Kconfig file declares build-time options for the MT7996 PCIe driver and optional NPU acceleration support.

## Important APIs, Types, And Functions
`CONFIG_MT7996E` is a tristate driver option selecting `MT76_CONNAC_LIB`, `WANT_DEV_COREDUMP`, and `RELAY`, and depending on `MAC80211` plus `PCI`. `CONFIG_MT7996_NPU` is a bool option depending on MT7996E and compatible `NET_AIROHA_NPU`, selecting `MT76_NPU`.

## Control Flow
There is no runtime flow. Kconfig resolution controls whether mt7996 objects are built and whether NPU-specific code is included.

## State And Persistence
Configuration persists in the kernel build `.config`. Selecting devcoredump and relay enables runtime support used by `coredump.c` and `debugfs.c`.

## Dependencies And Integration Points
It integrates with the kernel wireless menu, mac80211, PCI, mt76 connac library, devcoredump, relayfs, and optional Airoha NPU support.

## Risks
Incorrect dependency expressions can expose unbuildable combinations. The NPU dependency is specialized and must match symbol tristate semantics. Selecting RELAY is required for firmware binary logging support.

## Test Signals
`allyesconfig`, modular `MT7996E=m`, NPU enabled/disabled builds, and absence of missing-symbol errors validate the configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/Makefile

## Purpose
This Makefile defines the object composition for the MT7996E driver module.

## Important APIs, Types, And Functions
It builds `mt7996e.o` when `CONFIG_MT7996E` is enabled. The base object list includes `pci.o`, `init.o`, `dma.o`, `eeprom.o`, `main.o`, `mcu.o`, `mac.o`, `debugfs.o`, and `mmio.o`. `npu.o` is conditional on `CONFIG_MT7996_NPU`, and `coredump.o` is conditional on `CONFIG_DEV_COREDUMP`.

## Control Flow
No runtime logic exists. Kbuild aggregates the listed objects into one module or built-in object.

## State And Persistence
Build state is determined by Kconfig symbols. Runtime coredump and NPU features appear only when their objects are linked.

## Dependencies And Integration Points
It integrates with the kernel Kbuild system and the surrounding mt76 directory build. It must stay synchronized with source files and Kconfig options.

## Risks
Missing an object can produce unresolved symbols or silently drop features. Adding coredump only under `CONFIG_DEV_COREDUMP` must match stubs in `coredump.h`.

## Test Signals
Incremental and clean builds with MT7996E built-in/module, DEV_COREDUMP on/off, and MT7996_NPU on/off validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/coredump.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/coredump.c

## Purpose
This file implements MT7996 firmware crash dump collection and submission through Linux devcoredump. It captures metadata, firmware state, PC/LR stacks, and optional firmware memory regions.

## Important APIs, Types, And Functions
Exports are `mt7996_coredump_get_mem_layout()`, `mt7996_coredump_new()`, `mt7996_coredump_submit()`, `mt7996_coredump_register()`, and `mt7996_coredump_unregister()`. Internal helpers compute memory dump size, read firmware assert state, read firmware PC/LR stack logs, and build the final `mt7996_coredump` buffer. The `coredump_memdump` module parameter enables optional memory content.

## Control Flow
Registration allocates crash data and optional memory buffer sized from chip memory layout. On a crash, `mt7996_coredump_new()` requires `dump_mutex`, optionally waits for firmware dump state, assigns a GUID, and timestamps the event. Submit builds a vmalloc buffer, fills magic/kernel/fw/device/time metadata, reads assert count to label normal vs exception, reads current PC and stack logs, copies optional memory dump payload, unlocks, then passes the buffer to `dev_coredumpv()`. Unregister frees optional memory and crash data.

## State And Persistence
State lives in `dev->coredump.crash_data`, optional `memdump_buf`, GUID/timestamp, firmware dump registers, and devcoredump's retained userspace-visible blob. Memory region layout is static for MT7996 device IDs.

## Dependencies And Integration Points
It depends on `devcoredump`, `utsname`, GUID/time APIs, MT7996 register definitions, `dump_mutex`, and firmware recovery paths that call `mt7996_coredump_new()/submit()`.

## Risks
Optional memory dumping can allocate large vmalloc buffers and is gated by a module parameter. Locking must protect crash data while building the dump. Stack log register indexing and exception/non-exception stop/start behavior must match firmware debug hardware. `mt7996_coredump_register()` returns success without memory content if no layout is known, which callers must tolerate.

## Test Signals
Firmware assert trigger, normal manual dump, coredump with and without `coredump_memdump`, GUID/timestamp correctness, PC/LR stack population, userspace devcoredump readout, and unregister cleanup validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/coredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/coredump.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/coredump.h

## Purpose
This header defines the MT7996 devcoredump wire format, memory-region descriptors, and CONFIG_DEV_COREDUMP-dependent function declarations/stubs.

## Important APIs, Types, And Functions
Types include `mt7996_coredump`, `mt7996_coredump_mem`, `mt7996_mem_hdr`, and `mt7996_mem_region`. It declares or stubs `mt7996_coredump_get_mem_layout()`, `mt7996_coredump_new()`, `mt7996_coredump_submit()`, `mt7996_coredump_register()`, and `mt7996_coredump_unregister()`.

## Control Flow
No executable logic exists except inline stubs when devcoredump is disabled. Those stubs return harmless defaults so core recovery code can compile without conditional call sites.

## State And Persistence
The packed coredump format persists in devcoredump output and includes magic, length, GUID, timestamp, kernel release, firmware version, device id, firmware state, PC/LR stacks, and optional memory data.

## Dependencies And Integration Points
It includes `mt7996.h` for device types and uses `ETHTOOL_FWVERS_LEN`, GUID types, and kernel packing conventions. It is consumed by coredump implementation and recovery paths.

## Risks
The packed format is userspace-visible. Changing fields can break dump parsers. Stubs must match real function signatures exactly. Optional memory headers must align with builder logic.

## Test Signals
Builds with `CONFIG_DEV_COREDUMP=y/n`, successful recovery code linkage, and parsable devcoredump blobs validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/coredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/debugfs.c

## Purpose
This file implements MT7996 debugfs controls and diagnostics for firmware logging, SER recovery testing, radar emulation, queue state, TX/beamforming stats, TWT flows, RF register access, firmware relay logging, and per-station fixed-rate/queue debugfs.

## Important APIs, Types, And Functions
The main entry is `mt7996_init_debugfs()`. Other exported/visible hooks are `mt7996_debugfs_rx_fw_monitor()`, `mt7996_debugfs_rx_log()`, `mt7996_sta_add_debugfs()`, and `mt7996_link_sta_add_debugfs()`. Key controls include `implicit_txbf`, `sys_recovery`, `radar_trigger`, `fw_debug_wm`, `fw_debug_wa`, `fw_debug_bin`, `fw_util_wa`, `rf_regval`, and station `fixed_rate`.

## Control Flow
Initialization registers the mt76 debugfs directory and creates global files. `sys_recovery` parses `<band>,<val>` commands, queries or triggers firmware SER levels, full reset, or firmware assert. Firmware debug setters configure WM/WA logging and optional relay binary logging, with relay callbacks creating `fwlog_data`. Queue readers dump PLE/PSE pages, non-empty hardware queues, per-station AC queues across all phys, and software TX queues. TX stats refresh MIBs per PHY and print AMPDU, PER, beamforming, MU/SU, and AMSDU counters. Radar trigger validates DFS/channel/background state and sends RDD emulate commands. TWT stats walk an RCU list. RF reg access proxies through MCU. Per-station fixed rate parses a ten-field rate tuple, resolves link station WCID under mutex, and sends fixed-rate control.

## State And Persistence
The file mutates debug flags `fw_debug_wm`, `fw_debug_wa`, `fw_debug_bin`, relay channel state, `fw_debug_seq`, `dev->ibf`, recovery state for full reset, and fixed-rate firmware state. It reads queue registers, MIB stats, TWT list, RDD channel state, station link/WCID state, and firmware logs.

## Dependencies And Integration Points
It integrates debugfs, relayfs, mac80211 per-station debugfs, mt76 queue/debugfs helpers, MT7996 MCU commands, DFS/cfg80211 radar checks, recovery/reset, firmware log RX path, RCU station/link iteration, and optional `CONFIG_MAC80211_DEBUGFS`.

## Risks
Debugfs write handlers can trigger firmware crashes, SER, full reset, or fixed rates; they require privileged/debug use. Input parsing must reject malformed strings. Relay logging uses a spinlock and reserve/flush path that must be safe from RX context. Queue readers touch hardware while stations/links are RCU-protected. Fixed-rate control assumes link PHY and WCID are still valid.

## Test Signals
Debugfs file creation, SER query/trigger, firmware assert and coredump, relay log capture, queue dumps under traffic, TWT list output, radar emulation on DFS channels, RF register read/write, implicit TXBF toggle, and per-station fixed-rate programming validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/dma.c

## Purpose
This file implements MT7996/MT7992/MT7990 DMA queue mapping, WFDMA setup, interrupt enablement, WED/NPU/HWRRO queue integration, RRO initialization/start, reset, and cleanup.

## Important APIs, Types, And Functions
Key exports are `mt7996_init_tx_queues()`, `mt7996_dma_prefetch()`, `mt7996_dma_start()`, `mt7996_dma_rro_init()`, `mt7996_dma_rro_start()`, `mt7996_dma_init()`, `mt7996_dma_reset()`, and `mt7996_dma_cleanup()`. Internal helpers include queue config macros in `mt7996_dma_config()`, TX NAPI `mt7996_poll_tx()`, prefetch base calculation, `mt7996_dma_disable()`, and `mt7996_dma_enable()`.

## Control Flow
DMA config maps logical mt76 TX/RX/MCU queues to hardware ring IDs, WFDMA instances, and interrupt bits based on chip, WA support, HIF2, HWRRO, and NPU. Init attaches mt76 DMA, disables/reset WFDMA, allocates TX/MCU/FWDL rings, allocates event/data/txfree/RRO/MSDU-page RX rings with WED/NPU flags when active, initializes queues/NAPI, initializes NPU queues, and enables DMA. Enable resets ring pointers, disables delayed interrupts, programs prefetch, busy/extension config, pause thresholds, HIF2 band routing/outstanding settings, RX interrupt redirection, and starts WFDMA/interrupts. RRO init allocates either v3.1 RXDMAD-C or older IND/MSDU-page rings. Reset disables DMA, cleans TX/RX/MCU queues, handles WFSYS reset and WED/NPU reset, resets ring memory and RX buffers with special WED RRO exceptions, then reenables DMA.

## State And Persistence
Persistent state includes `q_wfdma_mask`, `q_int_mask[]`, `q_id[]`, mt76 queue objects and flags, WED/NPU queue associations, HIF2 pointer/speed/width-derived tuning, irqmask, RRO mode, WED RRO EMI pointers, and WFDMA/host-config registers. Reset recreates hardware ring state while preserving driver queue objects.

## Dependencies And Integration Points
It integrates mt76 DMA and connac queue helpers, MediaTek WED offload, optional NPU support, MT7996 register macros, chip/band validity helpers, RRO page-map helpers, IRQ enable/disable, PCI HIF2 topology, and firmware WA capabilities.

## Risks
The combinatorial queue matrix is the largest risk: chip type, band count, WA, HIF2, WED RX, HWRRO mode, and NPU all change ring IDs, sizes, flags, interrupts, and base offsets. Reset paths must skip or reset WED RRO queues exactly as expected by hardware. HIF2 routing and outstanding tuning depend on PCIe link speed/width. Incorrect irq masks can leave TX-free or RX rings unserviced.

## Test Signals
Boot on MT7996/MT7992/MT7990, one/two PCIe HIFs, WED on/off, NPU on/off, HWRRO v3/v3.1, tri-band traffic, TX-free handling, RRO reorder traffic, firmware/SER reset, DMA cleanup, and queue/interrupt counters validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/eeprom.c

## Purpose
This file loads, validates, defaults, and interprets MT7996-family EEPROM/efuse data. It chooses default EEPROM binaries by chip variant/FEM, reads efuse or external EEPROM blocks through MCU, parses per-band stream/path capabilities, applies efuse chip-config caps, sets MAC address, and exposes power/radar capability helpers.

## Important APIs, Types, And Functions
Public functions are `mt7996_eeprom_init()`, `mt7996_eeprom_parse_hw_cap()`, `mt7996_eeprom_get_target_power()`, `mt7996_eeprom_get_power_delta()`, and `mt7996_eeprom_has_background_radar()`. Important internals include `mt7996_check_eeprom()`, `mt7996_eeprom_name()`, `mt7996_eeprom_parse_stream()`, `mt7996_eeprom_variant_valid()`, `mt7996_eeprom_check_or_use_default()`, `mt7996_eeprom_load()`, `mt7996_eeprom_parse_efuse_hw_cap()`, and `mt7996_eeprom_parse_band_config()`.

## Control Flow
Initialization loads EEPROM data via `mt76_eeprom_init()`. Valid flash data is accepted; otherwise data is zeroed and loaded from external EEPROM or efuse block reads. Efuse free-block count can force default use when data is insufficient. The first block is checked for chip ID validity before reading remaining blocks. After loading, default firmware data is requested and either used as fallback or as a variant validation reference. Hardware capability parsing reads path/RX path/NSS fields per band, optionally clamps them by MCU chip-config capability, normalizes invalid values to max, detects aux RX, sets antenna mask, chainmask and chain shifts, and parses band selection. Init then copies the primary MAC address and applies mt76 EEPROM override.

## State And Persistence
State includes `dev->mt76.eeprom.data`, `dev->eeprom_mode`, variant fields `dev->var.type/fem`, `dev->has_eht`, `dev->wtbl_size_group`, per-phy antenna and chain masks, `phy->has_aux_rx`, `dev->chainmask`, `dev->chainshift[]`, and `dev->mphy.macaddr`. EEPROM content persists for device lifetime and drives channel/power/capability setup.

## Dependencies And Integration Points
It depends on Linux firmware loading, mt76 EEPROM initialization/override, MT7996 MCU efuse/eeprom/chip-config commands, chip/variant helpers, per-band PHY objects, channel group helpers, and default EEPROM binary names from `mt7996.h`.

## Risks
Wrong default binary selection can advertise invalid chains or FEM layout. Variant validation only ensures live EEPROM does not exceed default stream/path/NSS and FEM matches expected mode; subtle calibration mismatches still depend on firmware data quality. Efuse free-block heuristic can force defaults. Chainshift accumulation across bands must match present phys. Power delta sign handling affects regulatory TX power.

## Test Signals
Flash EEPROM, external EEPROM, efuse, and default-bin fallback boots; all supported chip IDs and variant/FEM combinations; per-band 2/5/6 GHz capability exposure; MAC override; target power/delta queries; background radar capability decisions; and invalid EEPROM fallback validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/eeprom.h

## Purpose
This header defines MT7996 EEPROM offsets, bitfields, band-selection enums, and channel-group helpers used by EEPROM parsing and power lookup.

## Important APIs, Types, And Functions
`enum mt7996_eeprom_field` names chip ID, version, MAC addresses, Wi-Fi config, rate-delta, and target-power offsets. Macros define TX/RX path, stream number, FEM PA/LNA config, and rate delta enable/sign/mask fields. `enum mt7996_eeprom_band` maps EEPROM band selectors. Inline helpers `mt7996_get_channel_group_5g()` and `mt7996_get_channel_group_6g()` map channel numbers to EEPROM target-power groups.

## Control Flow
There is no runtime flow beyond the inline channel group helpers. EEPROM code uses the offsets and masks to parse byte arrays and index target-power tables.

## State And Persistence
The constants describe persistent EEPROM layout and calibration/capability data. Channel group helpers determine which persistent target-power byte applies to a runtime channel.

## Dependencies And Integration Points
It includes `mt7996.h` for device context and kernel bit helpers. It is consumed by `eeprom.c` and power/regulatory code that needs target-power grouping.

## Risks
Offsets and masks are hardware/firmware ABI. Incorrect values can break chip validation, MAC address loading, chain capability, FEM validation, or TX power. Channel grouping must match the calibration table layout for 5 GHz and 6 GHz.

## Test Signals
EEPROM parsing across all bands, correct MAC address offsets, expected path/NSS capabilities, target-power lookup by 5/6 GHz channels, and fallback validation against default binaries validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/eeprom.h -->
