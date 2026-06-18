# subset-b-004715 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/admtek/adm8211.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/admtek/adm8211.h

Purpose: Hardware contract header for the ADMtek ADM8211 PCI 802.11b driver. It maps the device CSR register block, descriptor formats, EEPROM layout, RF/BBP constants, SRAM offsets, and the driver-private runtime state used by the companion C file.

Important APIs/types/functions: `ADM8211_CSR_READ` and `ADM8211_CSR_WRITE` wrap MMIO access through `priv->map`. `struct adm8211_csr` is the packed memory map for PCI CSRs. `struct adm8211_desc`, `adm8211_rx_ring_info`, and `adm8211_tx_ring_info` describe DMA rings and per-buffer state. `struct adm8211_tx_hdr` is the firmware/hardware transmit header prepended to frames. `struct adm8211_eeprom` captures calibration, regulatory, power, and identity data. `struct adm8211_priv` is the central persistent driver object, carrying PCI device state, MMIO base, DMA rings, ring cursors, mac80211 band/channel data, EEPROM image, RF/BBP type, and cached `nar` control bits.

Control flow: This header does not execute independently, but its macros define critical flow in the implementation. `ADM8211_IDLE`, `ADM8211_IDLE_RX`, and `ADM8211_RESTORE` stop or restore DMA by rewriting CSR6/NAR, forcing posted-write ordering with a readback, then sleeping to let hardware quiesce. Descriptor ownership bits (`RDES0_STATUS_OWN`, `TDES0_CONTROL_OWN`) control the RX/TX handoff between host and hardware.

State/persistence: Persistent state is kernel-resident and hardware-backed: EEPROM contents are cached in `adm8211_priv`, ring descriptors live in coherent DMA memory, and `nar` mirrors the hardware access register so stop/restart operations can restore the configured RX/TX state. No filesystem persistence is performed.

Dependencies/integration: Integrates with PCI MMIO (`ioread32`, `iowrite32`), DMA, sk_buff storage, and mac80211 (`ieee80211_supported_band`, channel/rate state, low-level stats). The EEPROM and RF/BBP constants feed regulatory, PHY, channel, and power setup.

Risks: Register and descriptor definitions are hardware ABI; bit mistakes can wedge DMA, corrupt frames, or violate regulatory limits. Endianness is explicit for descriptors and EEPROM but callers must preserve conversions. The idle macros assume a local `priv` symbol and sleep, so they are unsafe in atomic paths.

Test signals: Successful probe and traffic on ADM8211 hardware validate CSR layout, descriptor ownership, EEPROM parsing, RX/TX ring movement, channel ranges, and RF/BBP setup. Interrupt status bits and low-level stats provide runtime diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/admtek/adm8211.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/Kconfig

Purpose: Top-level Kconfig menu for Atheros/Qualcomm wireless drivers. It gates vendor visibility, declares common debug/regulatory feature switches, and sources all per-driver Atheros family Kconfig files.

Important APIs/types/functions: Defines `ATH_COMMON` as a tristate selected by individual drivers, `WLAN_VENDOR_ATH` as the visible vendor menu, and feature booleans `ATH_DEBUG`, `ATH_TRACEPOINTS`, `ATH_REG_DYNAMIC_USER_REG_HINTS`, and `ATH_REG_DYNAMIC_USER_CERT_TESTING`. The file then includes `ath5k`, `ath9k`, `carl9170`, `ath6kl`, `ar5523`, `wil6210`, `ath10k`, `wcn36xx`, `ath11k`, and `ath12k` configuration trees.

Control flow: Kernel configuration first asks whether to show the vendor menu. When enabled, the debug/regulatory options are exposed, then child Kconfig files provide concrete driver selections. `ATH_TRACEPOINTS` depends on both `ATH_DEBUG` and `EVENT_TRACING`; the dynamic regulatory options require `CFG80211_CERTIFICATION_ONUS`.

State/persistence: The only persisted state is the generated kernel `.config`, which determines which modules and feature objects are built. There is no runtime state.

Dependencies/integration: Integrates with cfg80211/mac80211 regulatory policy, the kernel event tracing subsystem, and downstream Atheros driver directories. `ATH_COMMON` corresponds to the common object built by the adjacent Makefile.

Risks: Regulatory options are intentionally warned as "Say N"; enabling them incorrectly can allow user regulatory hints or certification behavior outside permitted environments. Debug and trace options can increase binary size and expose additional diagnostics.

Test signals: Kconfig coverage is validated by `olddefconfig`, `allyesconfig`, `allmodconfig`, and targeted builds that select individual Atheros drivers and ensure dependencies pull in `ATH_COMMON` and tracing/debug objects as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/Makefile

Purpose: Build orchestration for the Atheros/Qualcomm wireless subtree. It descends into selected driver directories and assembles the common `ath.o` support object.

Important APIs/types/functions: `obj-$(CONFIG_ATH5K)`, `obj-$(CONFIG_AR5523)`, `obj-$(CONFIG_ATH10K)`, and similar lines map configuration symbols to subdirectories. `obj-$(CONFIG_ATH_COMMON) += ath.o` builds the shared common module from `main.o`, `regd.o`, `hw.o`, `key.o`, `dfs_pattern_detector.o`, and `dfs_pri_detector.o`. Conditional fragments add `debug.o` and `trace.o`; `CFLAGS_trace.o := -I$(src)` supports local trace header inclusion.

Control flow: Kbuild evaluates selected config symbols and builds only enabled subtrees. Drivers selecting `ATH_COMMON` cause `ath.o` to be linked. Optional debug and trace code are compiled only when their Kconfig booleans are true.

State/persistence: Produces build artifacts under the kernel build tree. No runtime state is held here.

Dependencies/integration: Ties Kconfig selections to object layout. Common regulatory, key, DFS, debug, and tracing helpers are shared by multiple Atheros drivers through `ATH_COMMON`.

Risks: Mismatches between Kconfig symbols and Makefile object lists can silently omit a driver or common helper. Trace builds require include path correctness because trace headers often rely on local relative inclusion.

Test signals: Targeted `make M=drivers/net/wireless/ath` builds under different configs confirm object selection. `modpost` failures catch missing objects or unresolved references from selected drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/Kconfig

Purpose: Kconfig entry for the Atheros AR5523 USB wireless driver.

Important APIs/types/functions: Defines `AR5523` as a tristate option labeled "Atheros AR5523 wireless driver support". It depends on `MAC80211` and `USB`, selects `ATH_COMMON`, and selects `FW_LOADER` for runtime firmware loading.

Control flow: When enabled as built-in or module, the adjacent Makefile builds `ar5523.o`. The selected firmware loader is required because pre-firmware devices receive `ar5523.bin` over USB before they re-enumerate as operational devices.

State/persistence: The selection persists only in kernel configuration and build outputs. Runtime state is in the driver, not Kconfig.

Dependencies/integration: Integrates the AR5523 driver with mac80211, USB core, shared Atheros helpers, and firmware loading infrastructure.

Risks: Without firmware loader support or the external firmware blob, supported pre-firmware USB IDs cannot transition to the usable post-firmware IDs. Incorrect dependency weakening would allow impossible builds without USB or mac80211.

Test signals: Configuring `CONFIG_AR5523=m` should build the module and select `ATH_COMMON` and `FW_LOADER`. Runtime probe logs should request `ar5523.bin` for pre-firmware devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/Makefile

Purpose: Kbuild mapping for the AR5523 driver.

Important APIs/types/functions: `obj-$(CONFIG_AR5523) := ar5523.o` compiles and links the single-source driver when the Kconfig symbol is enabled.

Control flow: Kbuild includes this directory from the Atheros parent Makefile. A disabled `CONFIG_AR5523` produces no objects; built-in or module selection produces the corresponding kernel object/module.

State/persistence: Build artifact only; no runtime state.

Dependencies/integration: Depends on the parent `ath/Makefile` and the `AR5523` Kconfig entry. The single object contains USB probe/disconnect, firmware loading, command protocol, and mac80211 operations.

Risks: Because all behavior is in one C file, any future split must update this Makefile or Kbuild will omit new objects.

Test signals: `make M=drivers/net/wireless/ath/ar5523 CONFIG_AR5523=m` should produce `ar5523.ko` with no unresolved symbols when mac80211, USB, firmware loader, and Atheros common support are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/ar5523.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/ar5523.c

Purpose: Minimal mac80211 USB driver for Atheros AR5523/AR5005UG/UX dongles. It loads firmware for pre-firmware USB IDs, exchanges vendor command messages with target firmware, manages bulk URBs for data RX/TX, and exposes a station-mode 2.4 GHz 802.11 interface.

Important APIs/types/functions: USB entry points are `ar5523_probe`, `ar5523_disconnect`, `ar5523_load_firmware`, and `module_usb_driver`. mac80211 operations are collected in `ar5523_ops`: `start`, `stop`, `tx`, `flush`, `add_interface`, `remove_interface`, `config`, `bss_info_changed`, `configure_filter`, and RTS setup. Firmware command helpers include `ar5523_cmd`, `ar5523_cmd_read`, `ar5523_cmd_write`, `ar5523_config`, `ar5523_get_status`, and `ar5523_get_capability`. Data paths center on `ar5523_data_rx_cb`, `ar5523_rx_refill_work`, `ar5523_tx`, `ar5523_tx_work_locked`, and `ar5523_data_tx_cb`.

Control flow: Probe validates four bulk endpoints. Pre-firmware IDs call `ar5523_load_firmware`, which sends 2048-byte firmware blocks and expects the device to detach/re-enumerate. Post-firmware probe allocates `ieee80211_hw`, initializes work/timer/list/atomic state, allocates command/data URBs, submits the command RX URB, announces host availability, reads max RX size/capabilities/MAC/serial, registers mac80211 hardware, and stores USB interface data. `ar5523_start` binds firmware, writes MAC/config knobs, starts target, switches channel, wakes target, resets key cache, starts RX refill, installs RX filters, and enables LEDs. TX queues sk_buffs in `tx_queue_pending`; work prepends a chunk and `ar5523_tx_desc`, submits bulk URBs, tracks submitted frames atomically, and waits for firmware `WDCMSG_SEND_COMPLETE` or URB completion. RX refill posts sk_buffs to the data endpoint; completion validates chunk/descriptor/status, fixes alignment, fills `ieee80211_rx_status`, and hands packets to mac80211. Association changes create target connections, ratesets, associd, LEDs, and periodic stats work.

State/persistence: Driver state lives in `struct ar5523`: USB device, mac80211 hardware, flags (`HW_UP`, `USB_DISCONNECTED`, `CONNECTED`), single serialized command object, delayed stats work, watchdog timer/work, TX pending/submitted lists, RX free/used lists, atomics, RX buffer size, serial, channels/rates, and one station VIF. Firmware is loaded from `ar5523.bin` but not persisted by the driver. Command replies complete a shared completion, so command operations are serialized by `ar->mutex` in higher-level paths.

Dependencies/integration: Integrates with USB bulk pipes, Linux firmware loader, mac80211 station APIs, workqueues, timers, sk_buffs, and the private AR5523 WDC message ABI from `ar5523_hw.h`. The driver selects `ATH_COMMON` but does not use much shared Atheros runtime directly.

Risks: Hardware behavior is black-boxed and comments note magic values and minimal functionality. The single command slot requires careful serialization; unexpected firmware replies or timeouts can poison command state. RX descriptor length/status parsing and alignment memmove are packet-safety sensitive. TX completion depends on both URB completion and firmware send-complete messages; mismatched accounting can stop queues or underflow atomics. Watchdog recovery resets the dongle rather than doing fine-grained queue repair. Disconnect suppresses repeated USB errors but must kill URBs before freeing buffers.

Test signals: Useful signals are firmware request and re-enumeration, successful `ieee80211_register_hw`, MAC/serial/capability logs, station association, RX beacons/data with sane RSSI, TX completion counters returning to zero, queue wake after low watermark, no flush timeouts, and no watchdog "TX queue stuck" resets under sustained traffic. Hot-unplug should complete without use-after-free or repeated error spam.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/ar5523.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/ar5523.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/ar5523.h

Purpose: Internal runtime header for the AR5523 USB driver. It defines device flags, endpoint pipe helpers, queue sizing, command/RX/TX per-transfer structures, and the main `struct ar5523` private object.

Important APIs/types/functions: Pipe helpers map endpoint addresses to USB bulk pipes: `ar5523_cmd_tx_pipe`, `ar5523_data_tx_pipe`, `ar5523_cmd_rx_pipe`, and `ar5523_data_rx_pipe`. Constants define command/data timeouts, TX/RX ring counts, refill thresholds, watchdog and flush timeouts. `struct ar5523_tx_cmd` represents the single outstanding firmware command URB and completion. `struct ar5523_tx_data` is stored in `ieee80211_tx_info.driver_data`. `struct ar5523_rx_data` owns one RX URB/sk_buff slot. `struct ar5523` aggregates USB, mac80211, locks, workqueues, TX/RX queues, atomics, firmware command buffers, radio band data, and the single VIF.

Control flow: The C file uses these structures to move objects between pending/submitted/free/used lists. RX refill consumes `rx_data_free` entries and returns them from completion. TX uses `driver_data` to link sk_buffs onto the pending and submitted lists, with `tx_nr_total` and `tx_nr_pending` controlling mac80211 queue stop/wake and flush waits.

State/persistence: All state is volatile kernel memory. Flags encode hardware-up, disconnected, and associated/connected states. The serial number is cached after firmware status reads. No persistent storage is modified.

Dependencies/integration: Depends on USB URBs, mac80211 `ieee80211_hw`/VIF/TX info, kernel workqueues, timers, wait queues, spinlocks, mutexes, and sk_buffs.

Risks: `struct ar5523_tx_data` must fit in `IEEE80211_TX_INFO_DRIVER_DATA_SIZE`; the C file enforces this with `BUILD_BUG_ON`. Error logging is suppressed after hot-unplug by `ar5523_err`, which reduces noise but can hide late cleanup failures. Queue constants are small, so accounting bugs are visible as queue starvation.

Test signals: Compile-time size checks, clean hot-unplug, balanced TX/RX list counts, RX refill activity, TX flush completion, and station-mode operation validate this header's state model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/ar5523.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/ar5523_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/ar5523_hw.h

Purpose: Private AR5523 firmware protocol header. It defines big-endian command, firmware download, RX/TX descriptor, chunking, rateset, connection, LED, queue, filter, config, capability, and status message layouts used over USB bulk endpoints.

Important APIs/types/functions: `struct ar5523_fwblock` is the pre-firmware block metadata used by `ar5523_load_firmware`. `struct ar5523_cmd_hdr` is the common WDC command header and enumerates host-to-target and target-to-host message IDs. `struct ar5523_chunk` wraps data endpoint messages. `struct ar5523_rx_desc` and `struct ar5523_tx_desc` describe packet receive metadata and transmit requests. Command payloads include `ar5523_write_mac`, `ar5523_cmd_rateset`, `ar5523_cmd_set_associd`, `ar5523_cmd_reset`, `ar5523_cmd_rates`, `ar5523_cmd_create_connection`, LED controls, TX queue setup, and RX filter updates. Enumerations define `CFG_*`, `CAP_*`, `ST_*`, target power states, and WLAN modes.

Control flow: The driver builds these payloads, converts fields to big endian, and submits them through `ar5523_cmd_*` or data URBs. Firmware replies use command IDs and `priv` values to distinguish command completions from async events such as send completion, stats update, and device availability. RX data places the descriptor at the end of a chunk-aligned packet buffer.

State/persistence: This file defines wire formats only. Runtime state emerges when firmware applies configs such as MAC address, channel, RX filters, TX queues, association ID, rates, and power mode.

Dependencies/integration: Integrated tightly with the AR5523 firmware revision assumptions; comments note rev 1.5 command IDs and rev 1.6 differences. The driver also relies on mac80211 rate/channel/VIF state to populate these protocol structures.

Risks: Almost all fields are big endian; missing conversions will break firmware communication. Many constants were derived from black-box analysis and comments flag uncertain fields. Buffer-size constants (`AR5523_MAX_RXCMDSZ`, `AR5523_MAX_TXCMDSZ`, `AR5523_MAX_FWBLOCK_SIZE`, `AR5523_MIN_RXBUFSZ`) protect USB transfers; incorrect changes can overflow command buffers or reject valid frames.

Test signals: Firmware load acknowledgment, successful `HOST_AVAILABLE`, capability/status reads, channel reset, queue setup, association command sequence, RX filter behavior, and valid RX descriptor parsing validate this protocol surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/ar5523_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath.h

Purpose: Shared Atheros wireless support header. It defines common device state, regulatory/key/cipher abstractions, register access operations, power-save hooks, cycle counters, debug masks, logging helpers, and common helper prototypes used by multiple Atheros drivers.

Important APIs/types/functions: `struct ath_common` is the core shared object with hardware/private pointers, mac80211 hardware, debug mask, op flags, ANI state, MAC/BSSID data, key cache bitmaps, crypto capabilities, cycle counters, regulatory data, operation tables, and supported bands. `struct ath_ops` abstracts register read/write, buffered writes, and read-modify-write operations. `struct ath_ps_ops` abstracts wake/restore hooks. Key APIs include `ath_key_config`, `ath_key_delete`, `ath_hw_keyreset`, `ath_hw_keysetmac`, `ath_rxbuf_alloc`, `ath_is_mybeacon`, `ath_hw_setbssidmask`, cycle counter helpers, and `ath_printk`.

Control flow: Individual drivers fill `ath_common` and operation tables, then call common helpers for key programming, regulatory setup, beacon recognition, and diagnostics. Debug macros compile to masked logging under `CONFIG_ATH_DEBUG` and to no-op stubs otherwise. Operation flags in `enum ath_op_flags` coordinate higher-level states such as beacons, ANI, scanning, reset, multi-channel, and WoW.

State/persistence: Maintains in-memory shared driver state only. Key cache bitmaps track hardware key slot allocation; regulatory fields mirror EEPROM/world regulatory decisions; cycle counters accumulate survey/ANI observations.

Dependencies/integration: Depends on mac80211, cfg80211 regulatory types, sk_buffs, spinlocks, Linux logging, and common Atheros implementation files built as `ath.o`.

Risks: `ATH_KEYMAX` fixes bitmap capacity; drivers with larger hardware key caches would need dynamic handling. Debug masks influence observability. Operation table callbacks must match bus/hardware locking expectations or common helpers can access registers unsafely.

Test signals: Cross-driver builds, key install/remove tests, regulatory domain selection, debugfs/module debug output, survey/cycle counter updates, and beacon detection behavior exercise the contracts in this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/Kconfig

Purpose: Kconfig definitions for the ath10k 802.11ac driver family and its bus/debug feature variants.

Important APIs/types/functions: `ATH10K` is the main tristate requiring `MAC80211` and `HAS_DMA`; it selects `ATH_COMMON`, `CRC32`, `WANT_DEV_COREDUMP`, and `ATH10K_CE`. Bus options include `ATH10K_PCI`, `ATH10K_AHB`, `ATH10K_SDIO`, `ATH10K_USB`, and `ATH10K_SNOC`. Feature switches include `ATH10K_DEBUG`, `ATH10K_DEBUGFS`, `ATH10K_LEDS`, `ATH10K_SPECTRAL`, `ATH10K_TRACING`, and `ATH10K_DFS_CERTIFIED`.

Control flow: `ATH10K` enables the core object and CE support. PCI, SDIO, USB, and SNOC create separate bus modules; AHB is a bool depending on `ATH10K_PCI`, OF, and reset controller support because the AHB implementation reuses PCI internals. Debugfs, tracing, thermal, LEDs, spectral, and DFS support conditionally compile extra code from the Makefile.

State/persistence: Configuration persists in kernel `.config` and controls module composition. Runtime state is in ath10k core/bus drivers.

Dependencies/integration: Integrates with mac80211, DMA, PCI/MMC/USB/platform/QCOM subsystems, debugfs, relay, event tracing, LED class, devcoredump, QMI helpers, power sequencing, and DFS certification policy.

Risks: Some options are intentionally experimental or policy-sensitive. `ATH10K_USB` is marked work in progress. `ATH10K_DFS_CERTIFIED` requires certification onus. The `ATH10K_AHB` dependency on PCI is non-obvious but required by code reuse.

Test signals: Matrix builds across bus variants and feature flags, plus `allmodconfig`/`allyesconfig`, validate dependency correctness and object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/Makefile

Purpose: Kbuild file for ath10k core and bus-specific modules.

Important APIs/types/functions: `ath10k_core-y` lists core mac80211, HTC/HTT, WMI, BMI, hardware, P2P, swap, TX/RX, and debug objects. Conditional additions include spectral, testmode, trace, thermal, LEDs, station debugfs, WoW, coredump, and CE. Bus modules are `ath10k_pci.o`, `ath10k_sdio.o`, `ath10k_usb.o`, and `ath10k_snoc.o`; `ahb.o` is conditionally linked into `ath10k_pci` when `ATH10K_AHB` is enabled.

Control flow: Kbuild creates a core module for `CONFIG_ATH10K`, then adds bus modules according to their symbols. The AHB source is linked with PCI support, reflecting its reuse of PCI CE, interrupt, resource, and HIF helpers.

State/persistence: Build outputs only.

Dependencies/integration: Mirrors Kconfig feature choices and wires source files into the module graph. `CFLAGS_trace.o := -I$(src)` supports local trace header discovery.

Risks: Because many features are optional, missing conditional objects create unresolved references only in specific configs. AHB's placement under `ath10k_pci` can surprise maintainers splitting bus code.

Test signals: Compile tests for combinations of PCI/AHB/SDIO/USB/SNOC and optional debugfs/tracing/spectral/thermal/PM/devcoredump options are the primary validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/ahb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/ahb.c

Purpose: ath10k platform/AHB bus support for Qualcomm IPQ4019 Wi-Fi. It adapts ath10k's PCI-oriented CE/HIF infrastructure to a memory-mapped platform device with OF resources, clocks, resets, TCSR/GCC control registers, and a legacy shared interrupt.

Important APIs/types/functions: Platform entry points are `ath10k_ahb_probe`, `ath10k_ahb_remove`, `ath10k_ahb_init`, and `ath10k_ahb_exit`. Bus register ops are `ath10k_ahb_read32`, `ath10k_ahb_write32`, and `ath10k_ahb_get_num_banks`. Resource/power helpers include `ath10k_ahb_resource_init/deinit`, `ath10k_ahb_clock_init/enable/disable`, `ath10k_ahb_rst_ctrl_init`, `ath10k_ahb_release_reset`, `ath10k_ahb_halt_chip`, `ath10k_ahb_prepare_device`, and `ath10k_ahb_chip_reset`. HIF operations are collected in `ath10k_ahb_hif_ops`; CE bus operations are in `ath10k_ahb_bus_ops`.

Control flow: Probe reads the OF match hardware revision, creates ath10k core with `ATH10K_BUS_AHB`, maps device/GCC/TCSR registers, sets 32-bit DMA masks, acquires clocks and reset controls, gets the legacy IRQ, connects the PCI-private CE state to AHB MMIO, initializes PCI-style resources/NAPI, requests IRQ, prepares the device, reads chip ID, and registers ath10k core. Device preparation enables clocks, writes target CPU clock info to scratch, deasserts resets, disables interrupts, marks host ready, and waits for target init. Runtime HIF start enables NAPI, CE interrupts, INTx, and RX posting; stop disables interrupts, synchronizes IRQ, disables NAPI, and flushes PCI-style queues. Removal unregisters core, disables IRQs, releases resources, halts chip, disables clocks, deinitializes resources, and destroys core.

State/persistence: State is held in `struct ath10k_ahb` embedded after `struct ath10k_pci`: platform device, mapped MMIO regions, lengths, IRQ, clocks, and reset handles. Hardware state includes clock/reset lines, scratch registers, halt requests, CE ring resources, NAPI, and target firmware state. No disk persistence.

Dependencies/integration: Depends on OF platform matching (`qcom,ipq4019-wifi`), clk/reset frameworks, DMA API, platform IRQ resources, TCSR/GCC register maps from `ahb.h`, and many `pci.c` helpers for CE setup, BMI exchange, IRQ masking, NAPI, resource setup, and HIF TX/diagnostic operations.

Risks: Resource unwinding spans devm and manual `ioremap` mappings and must stay ordered. Reset/halt sequencing is hardware-sensitive; failure to halt AXI or assert resets can leave the Wi-Fi core wedged. AHB IRQ handling masks PCI-style INTx/firmware bits and schedules NAPI; incorrect pending detection can lose interrupts. Address translation in `ath10k_ahb_qca4019_targ_cpu_to_ce_addr` special-cases SRAM and must match firmware memory layout.

Test signals: Platform probe on IPQ4019 DT, successful clock/reset acquisition, target init wait, valid chip ID, ath10k core registration, firmware boot, interrupts/NAPI RX/TX, clean remove/reprobe, and suspend-like power-cycle/reset loops validate this file. Debug categories `BOOT` and `AHB` are useful for sequencing failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/ahb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/ahb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/ahb.h

Purpose: Header for ath10k AHB platform support. It defines the AHB-private state, IPQ4019 control register constants, reset/clock-related offsets, halt protocol values, and init/exit stubs.

Important APIs/types/functions: `struct ath10k_ahb` stores the platform device, main device MMIO, GCC/TCSR mappings, IRQ, clocks (`cmd`, `ref`, `rtc`), and reset controls (`core_cold`, `radio_cold`, `radio_warm`, `radio_srif`, `cpu_init`). Register constants cover GCC and TCSR base/size, PLL divider, scratch register, WLAN core ID, global clock disable bits, WCSS halt request/ack pairs, halt timeout, and core CPU interrupt mask. `ath10k_ahb_init` and `ath10k_ahb_exit` are real declarations under `CONFIG_ATH10K_AHB` and no-op stubs otherwise.

Control flow: The C file uses the constants to map shared control registers, write clock information, select per-core halt registers, request AXI halt, gate core clocks, assert/deassert reset controls, and wake target CPU. The stubs let common ath10k module code call AHB init/exit unconditionally.

State/persistence: Holds runtime platform-resource handles only. No persistent data.

Dependencies/integration: Integrates with Linux `platform_device`, clk, reset controller, AHB C implementation, and PCI-private ath10k structures that embed this AHB state.

Risks: Constants are SoC-specific; using them on non-IPQ4019-compatible hardware would access wrong registers. Stub behavior must match module init ordering so non-AHB builds remain linkable.

Test signals: Successful AHB build with and without `CONFIG_ATH10K_AHB`, correct DT probe, and observed halt/reset behavior on both WLAN core IDs validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/ahb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/bmi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/bmi.c

Purpose: Implementation of ath10k Bootloader Messaging Interface operations. BMI is the one-shot boot-time protocol for reading/writing target memory and registers, downloading firmware/patch data, executing target code, setting the app start address, and finally closing bootloader access with `BMI_DONE`.

Important APIs/types/functions: Public exported lifecycle and transfer APIs include `ath10k_bmi_start`, `ath10k_bmi_done`, `ath10k_bmi_get_target_info`, `ath10k_bmi_get_target_info_sdio`, `ath10k_bmi_read_memory`, `ath10k_bmi_write_memory`, `ath10k_bmi_read_soc_reg`, `ath10k_bmi_write_soc_reg`, `ath10k_bmi_execute`, `ath10k_bmi_lz_stream_start`, `ath10k_bmi_lz_data`, `ath10k_bmi_fast_download`, and `ath10k_bmi_set_start`. All real transport is delegated to `ath10k_hif_exchange_bmi_msg`.

Control flow: `ath10k_bmi_start` clears `ar->bmi.done_sent`. Each command rejects use after `BMI_DONE` with `-EBUSY`. Standard target-info sends `BMI_GET_TARGET_INFO` and validates response length; the SDIO variant handles a sentinel/version-length split response. Memory reads and writes chunk transfers at `BMI_MAX_DATA_SIZE`, with writes rounded to 4 bytes after copying. Large LZ data optionally uses a heap-allocated command buffer up to `BMI_MAX_LARGE_DATA_SIZE`. `ath10k_bmi_fast_download` starts an LZ stream, sends aligned bulk data, pads a trailing partial word, then starts a fake zero stream to flush target caches. `ath10k_bmi_done` sends `BMI_DONE` once and marks the window closed before exchange.

State/persistence: The only persistent driver state is `ar->bmi.done_sent`. Effects are target-side boot state: memory contents, SoC registers, patch data, execution results, app start address, and final exit from BMI mode. No host filesystem persistence.

Dependencies/integration: Used by ath10k core firmware boot paths across PCI/AHB/SDIO/USB/SNOC HIFs. Depends on `bmi.h` wire formats, HIF BMI exchange, host-interest address helpers for macros in the header, and debug/warn logging.

Risks: BMI is available only during early boot; accidental `BMI_DONE` ordering prevents further recovery commands. Chunking/rounding must avoid reading past caller buffers and keep target lengths aligned. SDIO target-info sequencing is special and easy to regress. Large download allocation failures and HIF timeouts directly fail firmware boot.

Test signals: Firmware boot success, target info version/type reads, board/OTP reads through BMI memory/register helpers, successful compressed firmware download, no commands after `BMI_DONE`, and debug logs under `ATH10K_DBG_BMI` validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/bmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/bmi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/bmi.h

Purpose: Wire-format and API header for ath10k's Bootloader Messaging Interface.

Important APIs/types/functions: Defines transfer sizes (`BMI_MAX_DATA_SIZE`, command buffer sizes, large transfer sizes), `enum bmi_cmd_id`, board/OTP parameter masks, `struct bmi_cmd`, `union bmi_resp`, `struct bmi_target_info`, segmented file headers/metadata, timeout and CE IDs, and prototypes for all BMI operations. Convenience macros `ath10k_bmi_read32` and `ath10k_bmi_write32` access host-interest items through BMI memory transfers.

Control flow: Callers construct one `struct bmi_cmd` with command ID and command-specific union member, then receive a matching `union bmi_resp`. Segmented file constants describe firmware/board-data streams with special high-bit length markers for done, board data, begin address, and immediate execution.

State/persistence: Defines protocol messages that mutate target boot memory/register/app-start state but keeps no host state itself.

Dependencies/integration: Includes `core.h` for `struct ath10k`, host-interest helpers, HZ timeout definitions, and hardware boot code. BMI command structures are shared conceptually with target bootloader firmware and must remain packed/little-endian.

Risks: Flexible arrays and packed unions require exact length calculations by callers. Command IDs alias old names (`READ_SOC_REGISTER`/`READ_SOC_WORD`) and must stay compatible with firmware. Buffer size constants cap transfer chunking; exceeding them would corrupt stack command buffers.

Test signals: Compile-time structure use, firmware download, BMI register/memory readbacks, segmented file processing, and cross-bus boot tests exercise this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/bmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/ce.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/ce.c

Purpose: ath10k Copy Engine hardware layer. It manages CE descriptor rings used for host-target transfers across PCIe-like interconnects, including AHB users, with 32-bit and WCN3990 64-bit descriptor variants, interrupt control, send/receive posting, completion, shutdown cancellation, register dumps, and read-index-in-DDR support.

Important APIs/types/functions: Public APIs include `ath10k_ce_alloc_pipe`, `ath10k_ce_init_pipe`, `ath10k_ce_free_pipe`, `ath10k_ce_deinit_pipe`, `ath10k_ce_send`, `ath10k_ce_send_nolock`, `__ath10k_ce_send_revert`, `ath10k_ce_num_free_src_entries`, `ath10k_ce_rx_post_buf`, `ath10k_ce_rx_update_write_idx`, `ath10k_ce_completed_recv_next`, `ath10k_ce_completed_send_next`, `ath10k_ce_revoke_recv_next`, `ath10k_ce_cancel_send_next`, interrupt enable/disable/service helpers, `ath10k_ce_dump_registers`, `ath10k_ce_alloc_rri`, and `ath10k_ce_free_rri`. Internal ops tables `ce_ops` and `ce_64_ops` select descriptor-specific behavior.

Control flow: Allocation chooses 32-bit or 64-bit ops, allocates source/destination rings in coherent DMA memory, aligns descriptor bases, records callbacks, and stores per-transfer context arrays. Initialization zeros rings, reads existing hardware indices, writes base addresses/sizes/max transfer size/watermarks, and disables byte swap. Send checks ring space, fills a source descriptor with DMA address, length, metadata transfer ID, gather/byte-swap flags, stores context, advances write index, and notifies hardware unless gather is incomplete. RX posting fills destination descriptors with anonymous buffers and advances destination write index. Completion compares software indices with hardware/read indices, returns contexts/lengths, clears descriptor lengths and contexts, and advances software indices. Interrupt service clears copy/watermark status before invoking registered recv/send callbacks. Shutdown helpers revoke posted receives or cancel pending sends after target DMA is stopped. Crash dump captures CE read/write indices.

State/persistence: State lives in `struct ath10k_ce` and `ath10k_ce_ring`: spinlock, bus register ops, per-CE pipe state, DMA-coherent descriptor memory, per-transfer contexts, software/write/hardware cached indices, optional shadow bases, and optional DDR read-index memory. Hardware persists current CE registers and descriptor ownership while powered.

Dependencies/integration: Depends on `ce.h`, ath10k hardware register maps (`ar->hw_ce_regs`, `ar->regs`, `ar->hw_values`), bus read/write ops from PCI/AHB/SNOC-like layers, DMA coherent allocation, spinlocks, target hardware params (`target_64bit`, `rri_on_ddr`, `shadow_reg_support`), HIF/HTT callers, and firmware crash data structures.

Risks: Ring arithmetic is correctness-critical; off-by-one errors can make full rings look empty or overwrite in-flight descriptors. Some paths return `-EIO` for "not complete yet", so callers must interpret it correctly. CE5 has special RX context reuse. Gather sends intentionally defer write-index updates and require revert support on partial failure. 64-bit descriptors overload upper address bits and flags, making endian and mask handling fragile. Interrupt status must be cleared before callbacks because hardware may sleep after the last clear. `ath10k_ce_free_rri` assumes allocation happened; callers must pair carefully.

Test signals: Firmware BMI/HTC startup, sustained HTT TX/RX, interrupt and polling modes, WCN3990 64-bit operation, RRI-on-DDR targets, CE crash dumps with sane indices, clean shutdown cancellation/revoke loops, and lockdep coverage on no-lock APIs validate this layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/ce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/ce.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/ce.h

Purpose: Public/internal interface for ath10k Copy Engine support. It declares descriptor formats, ring/pipe state, bus operations, CE attributes, operation hooks, ring arithmetic helpers, interrupt summary helpers, host-target pipe configuration structures, and exported CE APIs.

Important APIs/types/functions: `struct ce_desc` and `struct ce_desc_64` define 32-bit and 64-bit descriptors. `struct ath10k_ce_ring` tracks ring sizes, software/write/hardware indices, DMA descriptor bases, optional shadow descriptors, and per-transfer contexts. `struct ath10k_ce_pipe` binds a CE ID to source/destination rings, callbacks, max send size, attrs, and ops. `struct ath10k_ce` holds the global lock, bus ops, CE pipe array, and optional RRI memory. `struct ce_attr` is the caller-provided pipe configuration. `struct ath10k_ce_ops` abstracts 32/64-bit descriptor variants. APIs cover send, receive posting/completion, cancellation, initialization, shutdown, interrupt control, register dump, and RRI allocation.

Control flow: HIF/bus code allocates and initializes pipes from `ce_attr`, then posts RX buffers and sends DMA buffers. Interrupt handlers call CE service functions, which invoke callbacks. Ring helper macros implement power-of-two modular movement and descriptor lookup. `ce_pipe_config` and `ce_service_to_pipe` are shared with firmware during startup to map HTC/WMI/HTT services to CE pipes.

State/persistence: Describes volatile host and hardware ring state only. Per-transfer contexts persist until completion/cancel/revoke. DMA descriptor memory is coherent and visible to device hardware.

Dependencies/integration: Includes `hif.h`, relies on ath10k register constants (`CE0_BASE_ADDRESS`, `CE1_BASE_ADDRESS`, wrapper registers), Linux DMA types, and firmware-facing service/pipe configuration. Bus-specific register access is injected through `ath10k_bus_ops`.

Risks: Structures are used across hardware/firmware boundaries; layout and endian expectations cannot change casually. `nentries` must be a power of two after rounding for masks to work. API users must respect locking distinction between locked and no-lock variants.

Test signals: Cross-bus ath10k boot, service-to-pipe setup, DMA traffic, CE interrupt summaries, and crash dumps validate the header contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/ce.h -->
