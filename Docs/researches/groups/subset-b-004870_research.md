# Research: subset-b-004870

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800lib.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800lib.h

## Purpose
Defines the transport-neutral RT2800 library interface used by PCI/MMIO, SoC, and USB variants. It describes RT2800-specific private state, the `rt2800_ops` hardware access vtable, wrapper helpers that dispatch through `rt2x00dev->ops->drv`, and the public RT2800 library entry points consumed by bus drivers.

## Important APIs, Types, And Functions
`struct rt2800_drv_data` stores RT2800 calibration snapshots, TX mixer gain, max PSDU, beacon TBTT skew counter, AMPDU counters, and WCID-to-station mappings. `struct rt2800_ops` is the low-level bus contract: CSR read/write, multi-read/write, busy-register polling, EEPROM read, hardware crypto policy, firmware write, register initialization, TXWI lookup, and DMA-done index lookup. Inline wrappers such as `rt2800_register_read()`, `rt2800_read_eeprom()`, `rt2800_drv_write_firmware()`, and `rt2800_drv_get_dma_done()` hide the actual PCI/MMIO/USB/SOC implementation. Declared shared operations include firmware validation/load, TXWI/RXWI processing, tx status handling, beacon programming, watchdog, rfkill, key programming, STA WCID management, AMPDU, TSF, survey, and debugfs metadata.

## Control Flow
Bus drivers install a `struct rt2800_ops` in their `struct rt2x00_ops.drv`; shared RT2800 code calls these wrappers whenever it needs a register, firmware, EEPROM, or descriptor operation. Probe flows call shared `rt2800_probe_hw()` through bus `probe_hw`, which in turn relies on this vtable to populate capabilities and EEPROM-derived state. Runtime TX/RX and txdone paths use `rt2800_drv_get_txwi()` and `rt2800_drv_get_dma_done()` to interpret bus-specific descriptor layouts without duplicating the RT2800 MAC/PHY logic.

## State And Persistence
The header defines the RT2800 per-device persistence carried in `rt2x00dev->drv_data`. WCID state is bounded by `WCID_START`, `WCID_END`, and `STA_IDS_SIZE`, reflecting hardware table limits and beacon-buffer overlap. Calibration fields survive while the driver object exists and are reset only on device teardown or reprobe; hardware register state is rehydrated through callbacks after firmware/radio initialization.

## Dependencies And Integration Points
Depends on rt2x00 core objects (`rt2x00_dev`, queue entries, crypto descriptors), RT2800 register definitions from `rt2800.h`, mac80211 station/key structures, and debugfs support. It is the integration point between `rt2800lib.c` style shared logic and the bus-specific files in this work item.

## Risks
The vtable is type-erased through `const void *drv`, so a wrong bus ops table causes silent wrong register or descriptor behavior. WCID limits must stay aligned with hardware key/beacon table layout. Inline wrappers do no NULL checks; probe must fully initialize `ops->drv` before any shared RT2800 call. Bus implementations must agree on TXWI/RXWI sizes and descriptor offsets or RX/TX corruption follows.

## Test Signals
Probe RT2800 PCI, USB, and SoC devices and verify EEPROM parsing, firmware upload, radio enable, TX/RX, AP beaconing, hardware crypto, AMPDU, and tx status completion. KASAN and lockdep are useful around WCID allocation/removal, and debugfs register access should match the installed bus transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800mmio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800mmio.c

## Purpose
Implements the shared MMIO/DMA transport layer for RT2800 PCI and platform SoC devices. It owns MMIO TX/RX descriptor construction, RX descriptor interpretation, interrupt masking/dispatch, DMA queue register initialization, queue start/stop/kick/flush behavior, and the MMIO tx status timeout recovery loop.

## Important APIs, Types, And Functions
Exported functions include `rt2800mmio_get_dma_done()`, `rt2800mmio_get_txwi()`, `rt2800mmio_write_tx_desc()`, `rt2800mmio_fill_rxdone()`, tasklets for tx status/pre-TBTT/TBTT/RX/autowake, `rt2800mmio_interrupt()`, `rt2800mmio_toggle_irq()`, queue handlers, descriptor state helpers, `rt2800mmio_init_queues()`, `rt2800mmio_init_registers()`, `rt2800mmio_enable_radio()`, and `rt2800mmio_probe_hw()`. Descriptor fields come from `rt2800mmio.h`, while hardware access is via `rt2x00mmio_register_*()`.

## Control Flow
MMIO TX writes a DMA descriptor with SD_PTR0 pointing to TXWI, SD_PTR1 pointing to frame data, WIV/QSEL bits, burst/fragment flags, and records descriptor metadata in `skb_frame_desc`. TX kick updates `TX_CTX_IDX*` and starts the txstatus timer for EDCA queues. IRQ handling reads and acknowledges `INT_SOURCE_CSR`, masks active interrupt bits, pulls TX FIFO status into `txstatus_fifo`, and schedules tasklets. Tasklets process beacons, RX, autowake, or txdone and then re-enable their interrupt bit if the radio is still enabled. RX done reads descriptor word 3, flags CRC/cipher/L2PAD/MY_BSS/decryption status, then delegates RXWI parsing to shared RT2800 code.

## State And Persistence
Queue state is split between `data_queue` software indexes and hardware ring registers (`TX_BASE_PTR*`, `TX_MAX_CNT*`, `TX_CTX_IDX*`, `TX_DTX_IDX*`, `RX_BASE_PTR`, `RX_CRX_IDX`, `RX_DRX_IDX`). `txstatus_fifo` buffers ISR-collected status words, and `txstatus_timer` plus `txdone_work` recover missing or delayed status. `rt2800_drv_data.tbtt_tick` persists beacon interval skew compensation across TBTT interrupts while the radio is enabled.

## Dependencies And Integration Points
Used by both `rt2800pci.c` and `rt2800soc.c` through their `rt2x00lib_ops` and `rt2800_ops`. It depends on rt2x00 queue allocation/clear/index routines, RT2800 shared `rt2800_txdone*()` and `rt2800_process_rxwi()`, mac80211 beacon callbacks through `rt2x00lib_beacondone()`/`pretbtt()`, and kernel tasklets, hrtimers, workqueues, and kfifo.

## Risks
Interrupt masking is delicate: a missed re-enable can stall TX/RX/beacons, while a missed mask can race tasklet processing. TX status FIFO overflow or delayed hardware status can cause fallback `txdone_nostatus()` paths and misleading rate control. Descriptor DMA addresses and lengths must match the queue headroom/TXWI layout. Beacon skew compensation changes `BCN_TIME_CFG` every 64 beacons and can regress AP powersave clients if applied to the wrong mode. Flush waits are bounded and may leave hardware-owned entries on severe DMA hangs.

## Test Signals
Exercise TX/RX under high interrupt load, AP beaconing with powersave clients, tx status timeout recovery, suspend/remove during active tasklets, queue flush/drop, DMA ring wraparound, MMIC/ICV error reporting, and `ieee80211_restart_hw()` after watchdog. Useful diagnostics include interrupt counters, queue debugfs indexes, kfifo overflow warnings, and lockdep around `irqmask_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800mmio.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800mmio.h

## Purpose
Declares the RT2800 MMIO transport interface and the DMA descriptor bitfield layout used by PCI and SoC variants. It maps queue indexes to register offsets and defines TXD/RXD word fields consumed by `rt2800mmio.c`.

## Important APIs, Types, And Functions
The header defines queue register macros `TX_BASE_PTR()`, `TX_MAX_CNT()`, `TX_CTX_IDX()`, and `TX_DTX_IDX()`, descriptor sizes `TXD_DESC_SIZE` and `RXD_DESC_SIZE`, TX descriptor fields `TXD_W0_SD_PTR0`, `TXD_W1_SD_LEN*`, `TXD_W1_DMA_DONE`, `TXD_W3_WIV`, `TXD_W3_QSEL`, and checksum offload bits, plus RX descriptor fields for DMA ownership, CRC/cipher status, frame type, L2 padding, AMPDU, and PLCP/RSSI metadata. It declares all exported MMIO queue, interrupt, descriptor, probe, and radio helpers.

## Control Flow
Bus drivers include this header and wire its declared functions into `struct rt2x00lib_ops` and `struct rt2800_ops`. The descriptor macros are used to initialize outbound DMA rings, clear inbound descriptors for reuse, and translate RX descriptor state into `rxdone_entry_desc` flags before shared rt2x00 RX handling.

## State And Persistence
This header itself stores no runtime state. Its field definitions define the persistent ABI between driver memory descriptors and RT2800 MMIO hardware rings; those descriptors persist across queue lifetime and are reset by queue initialization and clear-entry paths.

## Dependencies And Integration Points
Depends on rt2x00 field macros (`FIELD32`), queue descriptors, `struct rt2x00_dev`, `data_queue`, and interrupt/tasklet types. It is tightly coupled with RT2800 register definitions such as `TX_BASE_PTR0` and `RX_CRX_IDX`, and with `rt2x00mmio` allocation of `queue_entry_priv_mmio`.

## Risks
Descriptor field masks are hardware ABI. A wrong mask or word index corrupts DMA ownership, buffer addresses, or RX status interpretation. `TX_QUEUE_REG_OFFSET` assumes contiguous queue registers; any chip exception must be handled elsewhere. Changes to descriptor sizes must be mirrored in queue initialization and skb descriptor accounting.

## Test Signals
Compile coverage for PCI and SoC builds, TX/RX descriptor dumps through debugfs, DMA API debugging, RX cipher/CRC flag tests, ring wraparound, and hardware queue register inspection after `rt2800mmio_init_queues()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800mmio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800pci.c

## Purpose
Implements the RT2800 PCI/PCIe bus driver. It binds PCI device IDs to the shared rt2x00/RT2800 stack, handles PCI EEPROM and firmware loading, sequences MCU sleep/wakeup requests, and installs the mac80211, rt2x00lib, and rt2800 operation tables for MMIO-backed devices.

## Important APIs, Types, And Functions
Key helpers are `rt2800pci_hwcrypt_disabled()`, `rt2800pci_mcu_status()`, EEPROM bit-bang callbacks for `eeprom_93cx6`, `rt2800pci_read_eeprom_pci()`, efuse/nvmem fallbacks, `rt2800pci_get_firmware_name()`, `rt2800pci_write_firmware()`, `rt2800pci_enable_radio()`, `rt2800pci_set_state()`, and `rt2800pci_set_device_state()`. The important objects are `rt2800pci_mac80211_ops`, `rt2800pci_rt2800_ops`, `rt2800pci_rt2x00_ops`, `rt2800pci_ops`, `rt2800pci_device_table`, and the final `pci_driver`.

## Control Flow
PCI probe calls `rt2x00pci_probe()` with `rt2800pci_ops`. Core probe then invokes RT2800/MMIO probe and queue setup. EEPROM read first tries nvmem, then efuse, then 93cx6 serial EEPROM based on `E2PROM_CSR_TYPE`. Firmware selection uses `rt3290.bin` for RT3290 and `rt2860.bin` otherwise, writes the image at `FIRMWARE_IMAGE_BASE`, toggles PBF system control, and clears mailbox registers. Radio-on first enables the MMIO radio path, clears mailbox state, sends MCU sleep and wake requests, and waits for matching mailbox CIDs. State changes route IRQ on/off to `rt2800mmio_toggle_irq()` and sleep/awake to MCU commands.

## State And Persistence
The module parameter `nohwcrypt` persists for the loaded module and disables hardware encryption. Firmware is cached by rt2x00 core in `rt2x00dev->fw`. EEPROM contents persist in `rt2x00dev->eeprom`; active hardware state is reset or replayed by MMIO/RT2800 init. The PCI device table is static module binding state.

## Dependencies And Integration Points
Depends on Linux PCI, `eeprom_93cx6`, rt2x00 PCI probe/remove/PM helpers, MMIO transport, RT2800 shared library, mac80211 callback implementations from rt2x00 core, and firmware files `rt2860.bin`/`rt3290.bin`. It exports module metadata and firmware requirements to the kernel module loader.

## Risks
MCU mailbox polling has a fixed 200-iteration busy wait and logs only after timeout; failures may leave power state ambiguous. EEPROM source precedence can hide broken efuse or nvmem content. Firmware write/reset sequencing is hardware-sensitive. The PCI device table is broad and conditional by Kconfig, so adding IDs without chipset support can probe unsupported hardware. Hardware crypto disable is global to the module, not per device.

## Test Signals
PCI/PCIe probe across listed chip IDs, EEPROM fallback paths, firmware load for RT3290 and non-RT3290, suspend/resume, rfkill polling, AP/STA operation, hardware crypto on/off via module parameter, tx status interrupt recovery, and `lspci` modalias autoload. Watch for MCU timeout errors and `ieee80211_register_hw()` failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800pci.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800pci.h

## Purpose
Provides RT2800 PCI-specific firmware constants and include guard. It documents the supported RT2800E/RT2800ED family at the header level and supplies firmware names and the firmware image base used by `rt2800pci.c`.

## Important APIs, Types, And Functions
Defines `FIRMWARE_RT2860` (`rt2860.bin`), `FIRMWARE_RT3290` (`rt3290.bin`), and `FIRMWARE_IMAGE_BASE` (`0x2000`). No functions or structures are declared.

## Control Flow
`rt2800pci_get_firmware_name()` chooses one of the firmware name macros, and `rt2800pci_write_firmware()` writes the selected image to `FIRMWARE_IMAGE_BASE`. Module metadata uses the same names to advertise firmware requirements.

## State And Persistence
No runtime state is defined. These constants become part of the firmware loading contract between kernel driver and userspace firmware storage.

## Dependencies And Integration Points
Consumed only by the PCI implementation. It integrates with the Linux firmware loader through module metadata and with RT2800 PBF/program-RAM write logic.

## Risks
Changing firmware names or image base breaks device boot. The header does not express firmware size; `rt2800_check_firmware()` and PCI write code must enforce length/version constraints.

## Test Signals
Successful `request_firmware()` for both filenames, firmware version logging, and PCI probe on RT3290 and non-RT3290 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800soc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800soc.c

## Purpose
Implements the platform/SoC RT2800 WiSoC driver. It reuses the MMIO RT2800 path for embedded Ralink wireless MACs, allocates platform-backed rt2x00 device state, reads EEPROM from nvmem or a fixed SoC flash window, and registers an OF-matched platform driver.

## Important APIs, Types, And Functions
Important helpers include `rt2800soc_hwcrypt_disabled()`, `rt2800soc_disable_radio()`, `rt2800soc_set_device_state()`, `rt2800soc_read_eeprom()`, stub firmware callbacks that warn if called, optional PM suspend/resume, the shared mac80211 ops table, RT2800/MMIO operation tables, `rt2x00soc_probe()`, `rt2800soc_probe()`, `rt2800soc_remove()`, `rt2880_wmac_match`, and `rt2800soc_driver`.

## Control Flow
Platform probe ioremaps the first memory resource, obtains IRQ and optional clock, allocates devm EEPROM/RF buffers, allocates `ieee80211_hw`, fills `rt2x00_dev` fields, sets chip interface to SOC, then calls `rt2x00lib_probe_dev()`. Radio-on uses `rt2800mmio_enable_radio()`. Radio-off disables shared RT2800 radio state, clears `PWR_PIN_CFG`, and for RT3883 preserves `TX_PIN_CFG_RFTR_EN`. Sleep/awake states are treated as unsupported no-ops. Remove calls `rt2x00lib_remove_dev()` and frees the hw object.

## State And Persistence
Platform-managed EEPROM and RF caches live for the device lifetime. EEPROM is loaded either from nvmem or from physical address `0x1F040000`, ioremapped for `EEPROM_SIZE`. The SoC does not persist firmware state through this file; firmware callbacks are stubs because these devices are expected to run without the PCI/USB firmware path.

## Dependencies And Integration Points
Depends on OF platform matching (`ralink,rt2880-wifi`), platform resources, optional clock framework, MMIO register helpers, RT2800 shared library, rt2x00 core probe/remove/suspend/resume, and mac80211 callbacks from common rt2x00 code.

## Risks
The fixed EEPROM mapping is SoC-layout-specific and risky outside expected platforms; nvmem should be preferred when available. Firmware callbacks warn if invoked, so capability flags must not require firmware for SoC devices. Power management only uninitializes/restores common state and treats hardware sleep as unsupported. Probe uses devm buffers but manually frees `ieee80211_hw`; error paths must keep ownership clear.

## Test Signals
Device tree probe with `ralink,rt2880-wifi`, IRQ delivery, nvmem EEPROM override, fallback EEPROM mapping, radio on/off, suspend/resume, AP/STA operation, RT3883 TX pin behavior, and no unexpected firmware callback warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800usb.c

## Purpose
Implements the RT2800 USB driver. It provides USB-specific register access binding, firmware upload/autorun detection, USB DMA setup, embedded TXINFO/RXINFO descriptor handling, asynchronous TX status polling, EEPROM/efuse selection, queue sizing, mac80211 operation wiring, and a large USB device ID table.

## Important APIs, Types, And Functions
Key functions include `rt2800usb_start_queue()`, `rt2800usb_stop_queue()`, `rt2800usb_tx_sta_fifo_read_completed()`, `rt2800usb_async_read_tx_status()`, `rt2800usb_tx_dma_done()`, `rt2800usb_tx_sta_fifo_timeout()`, `rt2800usb_autorun_detect()`, `rt2800usb_write_firmware()`, `rt2800usb_init_registers()`, `rt2800usb_enable_radio()`, `rt2800usb_set_device_state()`, `rt2800usb_get_txwi()`, `rt2800usb_write_tx_desc()`, `rt2800usb_get_tx_data_len()`, `rt2800usb_work_txdone()`, `rt2800usb_fill_rxdone()`, `rt2800usb_read_eeprom()`, and `rt2800usb_probe_hw()`. Static operation tables bind USB to rt2x00 and RT2800 abstractions.

## Control Flow
USB probe calls `rt2x00usb_probe()` with `rt2800usb_ops`. Firmware loading first checks AutoRun mode through a special vendor request, optionally clears `REQUIRE_FIRMWARE`, otherwise writes one 4 KiB half of `rt2870.bin` to `FIRMWARE_IMAGE_BASE`, then requests firmware execution via USB device mode. Radio-on wakes the device, waits briefly, configures `USB_DMA_CFG` bulk RX/TX and aggregation limits, then calls shared RT2800 enable. TX prep places a TXINFO descriptor at skb data, uses TXWI after TXINFO for normal data and at skb start for beacons, pads USB bulk packets, and starts asynchronous TX status reads after DMA completion. RX parses RXINFO, validates packet length, reads trailing RXD, strips descriptors, sets crypto/L2PAD/MY_BSS flags, trims skb, and delegates RXWI parsing.

## State And Persistence
`TX_STATUS_READING` in `rt2x00dev->flags` serializes asynchronous TX_STA_FIFO reads. `txstatus_fifo`, `txstatus_timer`, and `txdone_work` hold pending tx status across URB completions. Firmware and EEPROM are cached in common rt2x00 fields. Queue limits are USB-specific: RX 128, TX AC queues 16, beacon 8. The module parameter `nohwcrypt` is global for all devices bound to the module.

## Dependencies And Integration Points
Depends on `rt2x00usb` vendor requests, async register reads, USB queue management, RT2800 shared firmware/check/config/key logic, mac80211 callback glue, and the Linux USB driver core. The device table integrates many vendor/product IDs and conditional Kconfig chipset families.

## Risks
TX status polling has race windows between pending checks and clearing `TX_STATUS_READING`; the code rechecks but regressions can stall completions. RX length validation protects against malformed USB data, but descriptor placement at packet tail is fragile. Firmware AutoRun changes capability flags at runtime. USB bulk aggregation limit calculation assumes queue sizes and frame constants. The huge ID table increases risk of binding unsupported revisions. Hub-initiated LPM is disabled, indicating link power management can break devices.

## Test Signals
Probe many USB IDs, firmware and AutoRun paths, TX under busy medium with delayed status, RX malformed length handling, suspend/resume/reset_resume, hardware crypto on/off, AP beaconing, scan, high-throughput bulk transfers, and disconnect while TX status reads/timers are active. Look for TX status FIFO overrun, URB status warnings, and bad frame size logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800usb.h

## Purpose
Defines RT2800 USB firmware constants and USB-specific descriptor bitfields. It captures the TXINFO/RXINFO and trailing RXD layout used by `rt2800usb.c`.

## Important APIs, Types, And Functions
Defines `FIRMWARE_RT2870`, USB `FIRMWARE_IMAGE_BASE` (`0x3000`), `TXINFO_DESC_SIZE`, `RXINFO_DESC_SIZE`, `TXINFO_W0_*` fields for packet length, WIV, QSEL, bulk aggregation, and burst flags, `RXINFO_W0_USB_DMA_RX_PKT_LEN`, and `RXD_W0_*` fields for frame classification, CRC/cipher status, AMSDU/AMPDU, L2 padding, decryption, cipher algorithm, last AMSDU, PLCP RSSI, and PLCP signal.

## Control Flow
`rt2800usb_write_tx_desc()` writes TXINFO fields before submitting bulk URBs. `rt2800usb_fill_rxdone()` reads RXINFO at skb start, removes it, locates RXD after `rx_pkt_len`, decodes RX status flags, trims the packet, and passes RXWI to shared RT2800 logic. Firmware constants drive USB firmware upload and module metadata.

## State And Persistence
No direct runtime state is declared. Descriptor constants define the packet ABI between host USB buffers and device DMA engine.

## Dependencies And Integration Points
Depends on rt2x00 bitfield macros. It integrates with `rt2x00usb` queue code, RT2800 RXWI/TXWI parsing, mac80211 RX status flags, and Linux firmware loading.

## Risks
The TXINFO packet length excludes TXINFO itself and must match USB padding rules; incorrect values produce truncated or stuck bulk transfers. RXD is placed after variable-length packet data, so packet length validation is critical before reading. Firmware base differs from PCI and must not be shared.

## Test Signals
USB TX/RX descriptor dumps, RX size corruption tests, hardware crypto status tests, firmware upload using `rt2870.bin`, and bulk transfer stress with packet sizes at 4-byte boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00.h

## Purpose
Central rt2x00 driver header. It defines common driver identity, logging, timing/alignment helpers, chipset IDs, link quality and antenna state, per-vif and per-station private state, hardware mode descriptors, configuration wrappers, the `rt2x00lib_ops` and `rt2x00_ops` callback contracts, device state/capability flags, `struct rt2x00_dev`, and prototypes for queue, debug, interrupt-context, mac80211, probe, suspend, and resume entry points.

## Important APIs, Types, And Functions
Important structures are `rt2x00_chip`, `rf_channel`, `rt2x00_chan_survey`, `channel_info`, `antenna_setup`, `link_qual`, `link_ant`, `link`, `rt2x00_intf`, `hw_mode_spec`, `rt2x00lib_conf`, `rt2x00lib_erp`, `rt2x00lib_crypto`, `rt2x00intf_conf`, `rt2x00_sta`, `rt2x00lib_ops`, `rt2x00_ops`, and `rt2x00_dev`. Inline helpers cover RF/EEPROM access, chip matching, interface matching, capability checks, and TX queue lookup. Prototypes expose core mac80211 callbacks and lifecycle functions used by bus drivers.

## Control Flow
Bus-specific modules allocate/fill `rt2x00_dev`, set `rt2x00_ops`, and call `rt2x00lib_probe_dev()`. The core then uses `rt2x00_ops.lib` to probe hardware, initialize queues, control radio state, fill descriptors, configure device state, and parse RX/TX completions. mac80211 enters through the prototypes declared here; those common callbacks update `rt2x00_dev` state and delegate to chip-specific hooks.

## State And Persistence
`struct rt2x00_dev` is the persistent per-device root: hardware pointer, wiphy bands, debug/LED handles, flags, capability flags, IRQ/name, chip IDs, mode spec, antennas, CSR cache/base, mutexes, packet filter, interface counts, link tuner state, EEPROM and RF caches, RF/channel/power/retry/AID/beacon state, low-level statistics, workqueue, queues, firmware, tx status FIFO, tasklets, BAR tracking list, USB anchor/protocol errors, and optional SoC clock.

## Dependencies And Integration Points
Depends heavily on Linux mac80211, workqueues, firmware, LEDs, mutexes, kfifo, hrtimer, USB, clock, and local headers `rt2x00debug.h`, `rt2x00dump.h`, `rt2x00leds.h`, `rt2x00reg.h`, and `rt2x00queue.h`. It is included by nearly every rt2x00 source file and establishes the ABI between common code and transport/chip modules.

## Risks
This is a broad shared ABI: field ordering and flag semantics affect all buses. State flags are atomic bit operations but many adjacent counters are not, so callers must honor mac80211/core locking expectations. Some helpers use `BUG_ON` for invalid RF indexes. `TX_STATUS_READING` is noted as USB-specific but lives in shared flags. Incorrect capability flags can enable unavailable firmware, padding, tasklet, crypto, or watchdog paths.

## Test Signals
Build all rt2x00 variants, probe PCI/USB/SoC devices, run mac80211 interface lifecycle, suspend/resume, hardware restart, debugfs, rfkill, LED, hardware crypto, TX/RX queue and BAR handling. Static analysis should focus on callback table completeness and flag/counter races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00config.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00config.c

## Purpose
Implements common configuration translation from mac80211 structures to rt2x00 driver-specific configuration callbacks. It handles interface identity/synchronization, ERP/timing values, antenna diversity setup, channel/HT selection, power-save autowakeup scheduling, and common cached configuration fields.

## Important APIs, Types, And Functions
Exports `rt2x00lib_config_intf()`, `rt2x00lib_config_erp()`, `rt2x00lib_config_antenna()`, and `rt2x00lib_config()`. Private helper `rt2x00ht_center_channel()` maps HT40 center channel selection back to the hardware channel table. It fills `rt2x00intf_conf`, `rt2x00lib_erp`, and `rt2x00lib_conf` before calling `rt2x00dev->ops->lib` hooks.

## Control Flow
Interface config chooses TSF sync mode by nl80211 interface type, copies MAC/BSSID into 32-bit-aligned little-endian arrays, computes update flags, and delegates to chip code. ERP config calculates short preamble, CTS protection, slot/SIFS/PIFS/DIFS/EIFS, basic rates, beacon interval, AID, last beacon TSF, and HT opmode. Antenna config converts software diversity requests into concrete antennas, stops RX if radio is enabled, calls `config_ant`, resets link tuner, updates active antenna, and restarts RX. Main config reacts to channel and power-save changes, sets HT flags, fills RF/channel entries, calls chip `config`, updates cached band/frequency/power/retry flags, resets tuner on channel changes, and schedules autowakeup before DTIM when required.

## State And Persistence
Updates `rt2x00dev->aid`, `last_beacon`, `beacon_int`, `rf_channel`, `curr_band`, `curr_freq`, `tx_power`, `short_retry`, `long_retry`, and flags `CONFIG_HT_DISABLED`, `CONFIG_CHANNEL_HT40`, `CONFIG_POWERSAVING`, `CONFIG_MONITORING`. Antenna diversity state persists in `rt2x00dev->link.ant`.

## Dependencies And Integration Points
Called by mac80211 callbacks from `rt2x00mac_config()` and `bss_info_changed()`, by link tuning antenna changes, and by MMIO autowake. Depends on mac80211 channel definitions, `conf_is_ht*()` helpers, rt2x00 queue start/stop, workqueue scheduling, and chip-specific config hooks such as RT2800 config handlers.

## Risks
HT40 center-channel lookup warns and falls back if channel tables are inconsistent. Antenna changes stop RX around hardware programming, so failure or races can disrupt reception. Autowakeup timeout subtracts 15 jiffies-equivalent units without explicit underflow guard. MAC/BSSID clearing on NULL is intentional but can confuse multi-interface behavior if counts are stale. `conf_mutex` in link tuner protects some, not all, config interactions.

## Test Signals
Channel changes including HT20/HT40+/HT40-, AP/STA/mesh/adhoc interface configuration, antenna set/get and software diversity, power-save DTIM wake/sleep behavior, monitor mode, retry/power updates, and link tuner reset after channel/antenna changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00crypto.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00crypto.c

## Purpose
Provides common hardware-crypto helper routines for rt2x00. It maps mac80211 cipher IDs into rt2x00 cipher enums, annotates TX descriptors for hardware encryption, computes crypto overhead, saves/removes/reinserts TX IV data, and reconstructs stripped RX IV/ICV material when hardware provides it separately.

## Important APIs, Types, And Functions
Exports `rt2x00crypto_key_to_cipher()`, `rt2x00crypto_create_tx_descriptor()`, `rt2x00crypto_tx_overhead()`, `rt2x00crypto_tx_copy_iv()`, `rt2x00crypto_tx_remove_iv()`, `rt2x00crypto_tx_insert_iv()`, and `rt2x00crypto_rx_insert_iv()`. It uses `ieee80211_key_conf`, `skb_frame_desc`, `txentry_desc`, `rxdone_entry_desc`, and cipher enums.

## Control Flow
TX descriptor creation exits unless hardware crypto is enabled and mac80211 selected a hardware key. It sets encryption flags, pairwise flag, key index, IV offset/length, and whether hardware should generate IV/MMIC. TX overhead adds ICV and optionally IV/MMIC lengths when mac80211 does not generate them. TX remove/copy helpers preserve IV bytes in the skb descriptor, move the 802.11 header when stripping IV, and restore it before mac80211 TX status. RX insert chooses IV/ICV lengths by cipher, makes head/tail room while preserving or compensating L2 padding, copies IV and ICV from `rxdesc`, updates size, and clears `RX_FLAG_IV_STRIPPED`.

## State And Persistence
Crypto helpers mutate per-packet state only: `txentry_desc`, `skb_frame_desc->iv`, skb data pointers/lengths, and `rxdesc->size/flags`. They depend on persistent hardware crypto capability flags and key configuration installed through `rt2x00mac_set_key()`.

## Dependencies And Integration Points
Used by TX queue preparation and RX completion in rt2x00 core, and by debugfs crypto counters. Integrates with mac80211 key flags `GENERATE_IV`, `GENERATE_MMIC`, pairwise keys, and RT2800 key programming hooks.

## Risks
Header movement and skb push/pull operations are sensitive to headroom/tailroom assumptions established by queue code. IV length inference in `rt2x00crypto_tx_insert_iv()` derives from stored IV words and could fail for unexpected formats. RX AES ICV handling only fills 4 of 8 bytes because mac80211 strips it immediately. Unsupported ciphers map to `CIPHER_NONE`, forcing software paths.

## Test Signals
WEP40/WEP104/TKIP/CCMP TX and RX, pairwise and group keys, mac80211-generated versus hardware-generated IV/MMIC, MIC failure countermeasures, L2 padding plus crypto reconstruction, TX status skb restoration checks, and KASAN around skb manipulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00debug.c

## Purpose
Implements rt2x00 debugfs support. It creates per-device debugfs files for driver/chipset metadata, device and capability flags, hardware restart trigger, register read/write windows, queue statistics, crypto statistics, and a single-reader binary frame dump stream.

## Important APIs, Types, And Functions
Private state is held in `struct rt2x00debug_intf`, including debug callbacks, debugfs dentries, frame dump open flag, skb queue, waitqueue, crypto counters, metadata blobs, and register offsets. Exported functions are `rt2x00debug_update_crypto()`, `rt2x00debug_dump_frame()`, `rt2x00debug_register()`, and `rt2x00debug_deregister()`. Macro-generated file operations implement CSR/EEPROM/BBP/RF/RFCSR register access.

## Control Flow
Registration allocates `rt2x00debug_intf`, attaches it to `rt2x00dev`, creates a driver folder under the wiphy debugfs directory, writes static metadata blobs, exposes flags/restart files, creates register offset/value pairs for supported register classes, initializes frame dump queue/waitqueue, and exposes queue and crypto stats. Dumping frames checks whether the dump file is open, bounds the queue length to 20, copies a `rt2x00dump_hdr`, descriptor, and frame data into a new skb, queues it, and wakes readers. Reads block until a dump skb is available. Deregistration purges queues, removes debugfs recursively, frees blobs and state.

## State And Persistence
Debugfs state exists while registered and is not persistent across remove/suspend. Crypto counters accumulate by cipher while the debugfs interface lives. Frame dump has single-open state and queued copied skbs. Register offsets are mutable debugfs variables and persist until deregistration.

## Dependencies And Integration Points
Depends on `CONFIG_RT2X00_LIB_DEBUGFS`, Linux debugfs, poll/waitqueue/usercopy APIs, rt2x00 register access callbacks from `struct rt2x00debug`, `rt2x00dump.h` ABI, mac80211 wiphy debugfs root, and `ieee80211_restart_hw()` for restart injection.

## Risks
Debugfs register writes allow direct hardware mutation and can destabilize devices. `rt2x00debug_update_crypto()` assumes `debugfs_intf` exists when compiled in; call ordering must respect registration. Frame dump allocation is GFP_ATOMIC and may drop frames under pressure. Poll returns writable-style bits for readable data, which is unusual. Restart trigger is rate-limited globally by a static `last_reset`.

## Test Signals
Open/read queue dump with TX/RX traffic, verify binary `rt2x00dump_hdr` layout, read queue and crypto stats, read/write each supported register class, trigger restart with and without `CAPABILITY_RESTART_HW`, suspend/resume debugfs deregistration/registration, and run KASAN/usercopy checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00debug.h

## Purpose
Defines the debugfs register callback contract for rt2x00 chip drivers. It lets each hardware module describe readable/writable register spaces without hard-coding CSR, EEPROM, BBP, RF, or RFCSR access in generic debugfs code.

## Important APIs, Types, And Functions
`enum rt2x00debugfs_entry_flags` currently defines `RT2X00DEBUGFS_OFFSET`, meaning callbacks receive byte offsets rather than word indexes. `RT2X00DEBUGFS_REGISTER_ENTRY()` generates a per-register-class structure containing read/write callbacks, flags, base, word size, and word count. `struct rt2x00debug` groups owner module and register entries for CSR, EEPROM, BBP, RF, and RFCSR.

## Control Flow
Chip drivers populate a `struct rt2x00debug` and attach it to `rt2x00_ops.debugfs`. `rt2x00debug_register()` checks which read callbacks exist, creates offset/value debugfs files, and uses the callbacks to perform register access after validating requested word count.

## State And Persistence
This header declares metadata only. Runtime offset state and debugfs objects are owned by `rt2x00debug.c`; hardware register state is accessed through callbacks.

## Dependencies And Integration Points
Depends on `struct rt2x00_dev` and module ownership. Integrated with optional `CONFIG_RT2X00_LIB_DEBUGFS` support and chip-specific debug descriptors such as `rt2800_rt2x00debug`.

## Risks
Wrong word size/count/base exposes invalid hardware offsets. Missing module ownership can allow unload while debugfs files are open. Direct writes bypass normal driver locking unless callbacks implement it.

## Test Signals
Debugfs registration for each chip family, module get/put behavior while files are open, bounds checks for offsets, and safe CSR/EEPROM/BBP/RF/RFCSR read/write operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00dev.c

## Purpose
Implements the shared rt2x00 device lifecycle and interrupt-context data path glue. It enables/disables radio, schedules deferred interface work and powersave sleep, handles beacon/TBTT events, processes DMA start/done, converts TX/RX completions into mac80211 status, builds supported rates/channels, registers `ieee80211_hw`, initializes queues/work/tasklets/debug/LED/rfkill, and handles remove/suspend/resume.

## Important APIs, Types, And Functions
Exports `rt2x00lib_get_bssidx()`, `rt2x00lib_enable_radio()`, `rt2x00lib_disable_radio()`, beacon/TBTT/DMA/TX/RX completion helpers, `rt2x00_supported_rates`, `rt2x00lib_set_mac_address()`, `rt2x00lib_start()`, `rt2x00lib_stop()`, `rt2x00lib_probe_dev()`, `rt2x00lib_remove_dev()`, `rt2x00lib_suspend()`, and `rt2x00lib_resume()`. Important private helpers include BAR status matching, TX status filling, RX power-save/TIM parsing, RX signal-rate decoding, hardware mode setup, and common initialization/uninitialization.

## Control Flow
Probe initializes locks, workqueue, hrtimer, device-present flag, vif private size, address mask, hardware capabilities via chip `probe_hw`, queue allocation, mac80211 registration, link tuner, LEDs, debugfs, and rfkill. Start loads firmware, initializes queues/hardware, resets interface counters, enables radio, starts queues/tuner/watchdog, and marks started. Stop disables radio and clears counters. TX done unmaps DMA, restores skb headroom/L2 padding/IV, dumps debug frames, derives ACK/rate/AMPDU status, reports to mac80211, frees non-mac80211 skbs, clears entries, and unpauses queues. RX done allocates a replacement skb, unmaps the filled skb, asks chip code to fill `rxdone_entry_desc`, validates size, restores crypto or padding, trims, maps signal to rate index, checks TIM powersave and BAR/BA correlation, updates link/debug stats, fills `ieee80211_rx_status`, submits to mac80211, and requeues the entry.

## State And Persistence
Owns most persistent `rt2x00_dev` state: flags, counters, queue objects, txstatus FIFO, workqueue, BAR list, low-level stats, firmware pointer, channel/rate tables, debug/LED registrations, rfkill polling, and interface counts. Suspend clears `DEVICE_STATE_PRESENT`, uninitializes queues/hardware, suspends LEDs/debugfs, and best-effort sleeps device. Resume recreates debugfs/LED state and marks present; mac80211 drives reconfiguration.

## Dependencies And Integration Points
Integrates with mac80211 RX/TX APIs, rt2x00 queue layer, chip `rt2x00lib_ops`, firmware loader, debugfs, LEDs, rfkill, workqueue/tasklet/hrtimer/kfifo infrastructure, OF MAC address lookup, and RT2800 transport callbacks. Bus drivers call `rt2x00lib_probe_dev()` and `remove_dev()`.

## Risks
This file is concurrency-heavy: tasklets, workqueue, mac80211 callbacks, suspend/remove, and timer paths all inspect state flags. TX done must restore skb shape exactly for mac80211. RX done must never read corrupted descriptor sizes. BAR status matching uses RCU plus spinlock and can misattribute BA if tuple matching is incomplete. Probe/remove unwind spans many subsystems and must tolerate partial initialization. Resume relies on mac80211 reconfiguration after only marking device present.

## Test Signals
Full probe/remove fault injection, firmware load failures, TX/RX status under load, BAR/BA aggregation, AP beacon buffering, powersave TIM sleep/wake, rfkill, restart_hw, suspend/resume, debugfs/LED registration errors, queue threshold wakeups, malformed RX sizes, and lockdep/KASAN/RCU diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00dump.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00dump.h

## Purpose
Defines the userspace-visible binary frame dump ABI used by rt2x00 debugfs. It documents the dump stream format and provides stable type and header definitions shared between kernel and userspace tools.

## Important APIs, Types, And Functions
`enum rt2x00_dump_type` identifies RX done, TX queued, TX done, and beacon dump frames. `struct rt2x00dump_hdr` contains version, header/descriptor/data lengths, RT/RF/revision IDs, frame type, queue and entry indexes, and second/usecond timestamp fields. `DUMP_HEADER_VERSION` is currently 3.

## Control Flow
`rt2x00debug_dump_frame()` prepends `rt2x00dump_hdr` to copied descriptor and frame bytes before queueing to the debugfs dump file. Userspace reads records as `[header][hardware descriptor][802.11 frame]` and uses length fields to advance.

## State And Persistence
The header has no runtime state. ABI persistence is explicit: new fields must be appended so older userspace can locate descriptor and data using `header_length`.

## Dependencies And Integration Points
Used by `rt2x00debug.c` and userspace dump readers. Types use fixed-endian Linux integer annotations to keep on-disk/read-stream format stable.

## Risks
Changing existing fields or version semantics breaks userspace tools. Timestamp precision is microsecond derived from `ktime_get_ts64()`. Descriptor format remains hardware-specific, so consumers need chip/queue context.

## Test Signals
Read frame dump from debugfs, validate header lengths/endian fields, parse all dump types, and run old userspace readers against newer headers with appended fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00firmware.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00firmware.c

## Purpose
Implements common firmware request, validation, upload, version reporting, and release for rt2x00 drivers whose capability flags require firmware.

## Important APIs, Types, And Functions
Private `rt2x00lib_request_firmware()` asks chip code for a firmware filename, calls `request_firmware()`, validates non-empty data, logs version bytes from the end of the image, stores `wiphy->fw_version`, and dispatches chip `check_firmware()`. Exported `rt2x00lib_load_firmware()` caches and uploads firmware through chip `load_firmware()`. `rt2x00lib_free_firmware()` releases the cached image.

## Control Flow
`rt2x00lib_start()` calls `rt2x00lib_load_firmware()`. If `REQUIRE_FIRMWARE` is clear, the load path returns immediately. Otherwise it requests firmware once and reuses `rt2x00dev->fw` on later starts, validates chip-specific status codes (`FW_OK`, bad CRC/length/version), uploads through `ops->lib->load_firmware`, then resets association LED state because firmware upload can disturb LEDs.

## State And Persistence
The cached firmware pointer persists in `rt2x00dev->fw` until `rt2x00lib_free_firmware()` during device removal. The wiphy firmware version string persists for userspace until unregister.

## Dependencies And Integration Points
Depends on Linux firmware loader, wiphy device association, chip-specific `get_firmware_name`, `check_firmware`, and `load_firmware` callbacks, capability flag `REQUIRE_FIRMWARE`, and LED association helper.

## Risks
Version extraction assumes firmware has at least four bytes and stores bytes at `size - 4` and `size - 3`. Firmware status values must match chip check callback contract. If firmware upload succeeds but later radio init fails, cached firmware remains and later retries may skip request but still upload. SoC stubs must not be reached with `REQUIRE_FIRMWARE` set.

## Test Signals
Missing firmware, zero-length firmware, bad CRC/length/version from chip callbacks, successful upload for PCI/USB, repeated start/stop using cached firmware, removal release, wiphy `fw_version`, and LED association reset after upload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00leds.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00leds.c

## Purpose
Implements common LED class integration for rt2x00 radio, association, activity, and link-quality LEDs. It maps driver state and RSSI to LED brightness and handles registration, unregister, suspend, and resume.

## Important APIs, Types, And Functions
Exports `rt2x00leds_led_quality()`, `rt2x00led_led_activity()`, `rt2x00leds_led_assoc()`, `rt2x00leds_led_radio()`, `rt2x00leds_register()`, `rt2x00leds_unregister()`, `rt2x00leds_suspend()`, and `rt2x00leds_resume()`. Private helpers register/unregister individual `struct rt2x00_led` instances and perform simple full/off brightness changes.

## Control Flow
Quality LED updates add `rt2x00dev->rssi_offset`, bucket RSSI into six levels, and set brightness to a nonzero scaled value. Activity, association, and radio helpers set full/off brightness if the LED type matches and is registered. Registration builds names from driver name and phy name, registers initialized LED objects, and sets a default radio blink period if supported. Failure unwinds all LEDs. Suspend calls `led_classdev_suspend()` and turns LEDs off. Resume calls `led_classdev_resume()` and turns LEDs off again to clear hardware state.

## State And Persistence
LED registration state lives in `rt2x00_dev` members `led_radio`, `led_assoc`, and `led_qual`, with `LED_INITIALIZED` and `LED_REGISTERED` flags. Brightness is cached in `led_classdev.brightness`. LED state is not persistent across unregister/remove.

## Dependencies And Integration Points
Depends on `CONFIG_RT2X00_LIB_LEDS`, Linux LED class, wiphy device naming, chip code that initializes LED objects and brightness callbacks, link tuner RSSI updates, radio enable/disable paths, and firmware load LED reset.

## Risks
Brightness callbacks are chip-specific and may access hardware; unregister avoids setting off when LED is suspended but other paths assume access is safe. The registration name buffer is 36 bytes, so long driver/phy names can be truncated. Quality brightness never emits `LED_OFF` by design to avoid chip divisions, which may surprise users expecting zero for weak RSSI.

## Test Signals
LED class entries appear with expected names, radio and association state changes toggle LEDs, link quality changes brightness buckets, default blink is applied, suspend/resume leaves LEDs off, registration failure unwinds cleanly, and remove does not touch inaccessible hardware while suspended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00leds.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00leds.h

## Purpose
Defines the small rt2x00 LED data model shared by LED implementation and chip-specific initializers.

## Important APIs, Types, And Functions
`enum led_type` identifies radio, association, activity, and quality LEDs. `struct rt2x00_led` contains the parent `rt2x00_dev`, embedded `led_classdev`, type, and flags. Flags are `LED_INITIALIZED` and `LED_REGISTERED`.

## Control Flow
Chip code initializes `struct rt2x00_led` fields and sets `LED_INITIALIZED`; `rt2x00leds_register()` registers initialized LEDs and sets `LED_REGISTERED`. Runtime helpers check type and registered flag before calling brightness callbacks.

## State And Persistence
The structures are embedded in `rt2x00_dev` and persist for the device lifetime. Registration flags track LED class ownership; brightness state lives inside the embedded class device.

## Dependencies And Integration Points
Depends on Linux LED class and `struct rt2x00_dev`. Used by `rt2x00.h` and `rt2x00leds.c`, with optional compilation through `CONFIG_RT2X00_LIB_LEDS`.

## Risks
Flags are plain integers, not atomic; LED registration should remain in lifecycle paths. A chip initializer must provide valid `brightness_set` callbacks before marking initialized.

## Test Signals
Compile with and without LED support, verify chip LED initialization, registration/unregistration flag transitions, and safe brightness changes during radio/link state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00leds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00lib.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00lib.h

## Purpose
Declares the common rt2x00 library API used across configuration, queues, link tuning, firmware, debugfs, crypto, rfkill, and LED support. It also defines shared rate metadata and timing intervals for link tuning/watchdog.

## Important APIs, Types, And Functions
Defines intervals `WATCHDOG_INTERVAL`, `LINK_TUNE_INTERVAL`, `AGC_SECONDS`, `VCO_SECONDS`, `struct rt2x00_rate`, rate flags, `rt2x00_supported_rates`, `rt2x00_get_rate()`, `RATE_MCS()`, and `rt2x00_get_rate_mcs()`. It declares radio/start/stop/config handlers, queue allocation/alignment/TX/beacon APIs, link stats/tuner/watchdog APIs, firmware load/free, debugfs register/deregister/update, crypto helpers or stubs, rfkill polling inline helpers, and LED helpers or stubs.

## Control Flow
Common and bus-specific modules include this header to call shared services without depending on optional feature implementations. Compile-time feature flags select real functions or no-op stubs for firmware, debugfs, crypto, and LEDs. Queue and link declarations are used throughout rt2x00 TX/RX and lifecycle code.

## State And Persistence
No runtime storage is defined except through external `rt2x00_supported_rates`. The declarations describe operations over persistent state in `rt2x00_dev`, queues, link structures, firmware pointer, debugfs interface, and LED objects.

## Dependencies And Integration Points
Depends on `rt2x00.h` types, mac80211 SKBs/configuration, queue structures, and optional kernel configs. It is the common internal API surface between `rt2x00dev.c`, `rt2x00config.c`, `rt2x00queue.c`, `rt2x00link.c`, `rt2x00firmware.c`, `rt2x00debug.c`, `rt2x00crypto.c`, and `rt2x00leds.c`.

## Risks
Stubbed optional features must preserve semantics expected by callers; for example no-op crypto changes skb handling assumptions only when hardware crypto is disabled. Public queue and beacon APIs have locking expectations documented in comments; misuse can deadlock or race. Rate helper indexes assume mac80211 hw values are within the 12-entry table.

## Test Signals
Build matrix with firmware/debugfs/crypto/LED configs enabled and disabled, queue/beacon update locking, link tuner/watchdog scheduling, rate mapping for all supported rates, and rfkill polling behavior for hardware button capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00link.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00link.c

## Purpose
Implements common rt2x00 link-quality tracking, software antenna diversity, periodic link tuning, gain/VCO calibration scheduling, LED quality updates, and watchdog scheduling.

## Important APIs, Types, And Functions
Exports `rt2x00link_update_stats()`, `rt2x00link_start_tuner()`, `rt2x00link_stop_tuner()`, `rt2x00link_reset_tuner()`, `rt2x00link_start_watchdog()`, `rt2x00link_stop_watchdog()`, and `rt2x00link_register()`. Private helpers manage EWMA RSSI, antenna RSSI history, antenna sample/evaluation transitions, link quality reset, station-mode tuning, and delayed work callbacks.

## Control Flow
RX completion calls `rt2x00link_update_stats()` for STA interfaces; it increments RX success and updates global and antenna RSSI EWMA only for beacons from the associated BSS. Starting the tuner skips monitor-only and scanning states, resets tuner state, and queues delayed work. Each tuner tick exits if radio is off or scanning, locks `conf_mutex`, asks chip code for link stats, updates FCS error counts and RSSI fallback, calls chip `link_tuner()` if supported, updates quality LED, evaluates antenna diversity, runs gain calibration every four seconds and VCO calibration every ten seconds when supported, then reschedules. Watchdog work calls chip `watchdog()` at the configured interval while radio is enabled.

## State And Persistence
Uses `rt2x00dev->link.count`, `link.qual`, `link.ant`, EWMA RSSI state, delayed work objects, watchdog interval, and low-level stats. Antenna diversity persists current active antenna, history RSSI, and sampling mode flags. Reset preserves `vgc_level_reg` while clearing measurement counters.

## Dependencies And Integration Points
Depends on mac80211 delayed work scheduling, rt2x00 config antenna path, chip-specific `link_stats`, `reset_tuner`, `link_tuner`, `gain_calibration`, `vco_calibration`, and `watchdog` callbacks, LED quality helper, and RX descriptor `MY_BSS`/RSSI flags.

## Risks
Tuning races with channel/antenna config are mitigated by `conf_mutex`, but start/stop/scanning/radio flags still require careful ordering. Antenna diversity changes call back into config and reset quality counters, so repeated RSSI oscillation can cause churn. DEFAULT_RSSI forces maximum sensitivity when samples are missing, which may increase false CCA. Watchdog runs on mac80211 delayed work and can schedule recovery paths; callbacks must avoid deadlocks.

## Test Signals
STA association with stable and changing RSSI, software antenna diversity switching, scan start/complete suppressing tuner, channel/antenna changes resetting tuner, gain/VCO calibration cadence, quality LED updates, watchdog-triggered recovery, and low-level FCS/TX/RX statistic updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00link.c -->
