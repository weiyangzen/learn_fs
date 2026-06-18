# subset-b-004966 Research

Grouped research for RSI and Silicon Labs WFx wireless driver files under the ceph-client source tree. Each source file section preserves the source path in its title and is wrapped with deterministic markers for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_mgmt.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_mgmt.h

Purpose: Defines the Redpine/RSI WLAN firmware management ABI and the public management/data helpers used by the RSI mac80211 core. It is a dense contract header for descriptor formats, command frame IDs, rates, channel/radio settings, VAP/peer/key operations, power-save requests, WoWLAN, background scan, EEPROM access, and firmware feature frames.

Important APIs and types: Key constants include headroom/buffer sizes, standard and hardware rate encodings, descriptor flags, receive message types, rx filter bits, power-save flags, WoWLAN flags, aggregation limits, and scan limits. Important enums include `opmode`, `vap_status`, `peer_type`, `sta_notify_events`, and `cmd_frame_type`. Important packed structures are `rsi_cmd_desc`, boot parameter frames, peer notification, aggregation parameters, BB/RF programming, channel config, VAP capabilities, antenna selection, dynamic rate update, key programming, auto-rate, radio capabilities, common device config, EEPROM read, power-save request, WoWLAN request, background scan config/probe, and 9116 feature enable. Inline helpers decode/encode firmware descriptors: `rsi_get_queueno()`, `rsi_get_length()`, `rsi_get_extended_desc()`, `rsi_get_rssi()`, `rsi_get_channel()`, and `rsi_set_len_qno()`.

Control flow and integration: The implementation files use these definitions to build command SKBs for management queue transmission, parse firmware receive descriptors, report RX/TX status to mac80211, configure VAPs and peers during association/AP setup, update rates and radio parameters, install encryption keys, and request power-save or wake-on-wireless behavior. The public prototypes connect this ABI to firmware-ready handling, management packet receive, channel setting, aggregation, station notify, BSS status, QoS processing, TX data/mgmt paths, antenna selection, background scan, and WoWLAN.

State and persistence: No storage is owned by the header, but the packed structures encode persistent firmware state: per-VAP identity, peer/link state, key table contents, auto-rate table, RF/channel mode, rx filtering, GPIO usage, power-save intervals, background scan parameters, and feature enablement. Fields are explicitly little-endian where firmware expects LE wire format.

Dependencies: Includes `rsi_boot_params.h`, `rsi_main.h`, Linux sort and mac80211-facing constants. It depends on firmware descriptor layout, queue numbering, `FRAME_DESC_SZ`, `MAX_HW_QUEUES`, and background scan/channel constants from adjacent RSI headers.

Risks and test signals: The high-risk surface is ABI drift: packed layout, descriptor bit positions, endian conversion, and hardware rate mappings must match firmware. Tests should cover descriptor length/queue decoding, card-ready parsing, VAP add/delete/update, AP/STA/P2P modes, key install for WEP/TKIP/CCMP, aggregation start/stop, channel/radio updates, rx filter flags, EEPROM reads, background scan, WoWLAN request/wakeup reason, and 9116 feature enable frames.

Test signals: Source read size: 758 lines, 21583 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_mgmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_ps.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_ps.h

Purpose: Declares RSI power-save state, default low-power parameters, and power-save control entry points used by the RSI driver.

Important APIs and types: `enum ps_state` tracks `PS_NONE`, enable/disable request in flight, and enabled state. `struct ps_sleep_params` is the packed firmware request payload for enable/type/connected-sleep, listen interval beacon count, wakeup type, and sleep duration. `struct rsi_ps_info` is driver-side policy state for enablement, thresholds, hysteresis, monitor/listen intervals, DTIM settings, and deep-sleep wake period. APIs include `str_psstate()`, `rsi_enable_ps()`, `rsi_disable_ps()`, `rsi_handle_ps_confirm()`, `rsi_default_ps_params()`, and `rsi_conf_uapsd()`.

Control flow and integration: mac80211 power-save or U-APSD changes flow into `rsi_enable_ps()`/`rsi_disable_ps()`, which send `rsi_request_ps` frames defined in `rsi_mgmt.h`. Firmware confirmations are decoded at `PS_CONFIRM_INDEX` by `rsi_handle_ps_confirm()` and move the driver's PS state machine forward.

State and persistence: The header models transient request state and longer-lived PS policy in `rsi_ps_info`. Firmware state persists until explicit disable or reconfiguration and interacts with listen/DTIM intervals and U-APSD access categories.

Dependencies: Uses `struct rsi_hw`, `struct ieee80211_vif`, and `ps_sleep_params` embedded in the management command ABI.

Risks and test signals: Risks include stuck enable/disable request states, mismatch between mac80211 PS state and firmware confirmations, invalid DTIM/listen interval values, and U-APSD masking errors. Tests should exercise default parameter initialization, PS enable/disable confirmation paths, failed firmware confirms, U-APSD queue configuration, and suspend/resume interaction.

Test signals: Source read size: 63 lines, 1900 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_ps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_sdio.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_sdio.h

Purpose: Defines the RSI SDIO transport ABI, interrupt status decoding, device-private state, and SDIO helper prototypes.

Important APIs and types: `enum sdio_interrupt_type` maps firmware/SDIO interrupt causes to buffer availability, firmware assert, MSDU pending, and unknown status. Register constants identify function registers, firmware status, read/write FIFO controls, master access windows, wakeup register, interrupt clear, high-speed mode, and TA reset/hold/release addresses. `RSI_GET_SDIO_INTERRUPT_TYPE()` derives a typed interrupt from raw status bits. `struct receive_info` accumulates buffer-full/semi-full/management-full flags and interrupt counters. `struct rsi_91x_sdiodev` stores the SDIO function, IRQ/RX thread state, block size, previous descriptor, buffer status, aligned packet buffer, and write failure flag.

Control flow and integration: The SDIO implementation uses this header to initialize slave registers, read/write single or multiple registers, switch master access high words, acknowledge interrupts, determine event timeouts, check firmware buffer status before TX, and run `rsi_sdio_rx_thread()` to fetch pending frames.

State and persistence: Persistent transport state includes current buffer-full status, next read delay, high-speed/clock settings, card capability, TX block size, previous descriptor cache, and interrupt counters. Firmware-visible state lives in the function registers and TA control registers.

Dependencies: Depends on Linux MMC/SDIO APIs and RSI core types from `rsi_main.h`. It is coupled to RSI queue status behavior and firmware interrupt bit assignments.

Risks and test signals: Risks include stale buffer-status flags blocking TX, incorrect interrupt classification, unacknowledged function interrupts, master-access window mistakes for high addresses, and DMA/alignment assumptions for `pktbuffer`. Tests should cover interrupt status decoding, buffer full/semi-full recovery, firmware assert indication, register multi-write/read alignment, high-speed enablement, RX pending handling, and queue status timeouts.

Test signals: Source read size: 138 lines, 4842 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_sdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_usb.h

Purpose: Defines the RSI USB transport ABI, device IDs, endpoint constants, USB-private state, and small transport-specific inline helpers.

Important APIs and types: Constants define vendor/product IDs for 9113/9116, internal readiness/status/watchdog registers, vendor register read/write requests, TX headroom, bulk endpoint limits, WLAN/BT endpoint IDs, buffer sizes, and maximum RX packet size. `struct rx_usb_ctrl_block` tracks one RX URB, backing data, SKB, and endpoint. `struct rsi_91x_usbdev` stores the USB device/interface, endpoint selection, RX thread, RX URB control blocks, TX buffer, bulk endpoint descriptors, TX block size, write failure flag, and RX queue. USB-specific inline functions always report queue-not-full and infinite event timeout. `rsi_usb_rx_thread()` is the receive worker entry point.

Control flow and integration: The USB bus code uses the declared IDs and endpoint arrays during probe, URB setup, register access, and RX/TX scheduling. Unlike SDIO, `rsi_usb_check_queue_status()` does not gate TX on firmware queue status, so higher layers can enqueue without polling a buffer-status register.

State and persistence: Persistent bus state is held in URBs, endpoint maps, `rx_q`, `tx_buffer`, and write failure state. Firmware readiness and watchdog control are accessed through vendor register requests using the constants here.

Dependencies: Depends on Linux USB APIs, `rsi_main.h`, and `rsi_common.h`. Integration is with the RSI common TX/RX and thread abstractions.

Risks and test signals: Risks include endpoint discovery mismatches, URB lifetime and RX queue ordering, max packet size violations, vendor register access failure, and lack of queue-status backpressure compared with SDIO. Tests should cover probe for both product IDs, bulk endpoint parsing, RX URB refill, register read/write, watchdog disable request, TX headroom handling, disconnect while RX thread is active, and write-failure recovery.

Test signals: Source read size: 85 lines, 2487 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/Kconfig

Purpose: Adds the Silicon Labs wireless vendor menu to Kconfig and gates the nested WFx driver options.

Important APIs and types: `config WLAN_VENDOR_SILABS` is a boolean menu selector defaulting to `y`. When enabled, it sources `drivers/net/wireless/silabs/wfx/Kconfig`.

Control flow and integration: Kernel configuration uses this file only at config time. Selecting the vendor does not build code by itself; it exposes the WFx driver prompt beneath the wireless vendor subtree.

State and persistence: The only persistent state is the generated kernel `.config` value for `WLAN_VENDOR_SILABS`.

Dependencies: Integrated from the parent wireless Kconfig hierarchy and delegates the real driver dependencies to `wfx/Kconfig`.

Risks and test signals: Risks are minimal but include hiding WFx options if the vendor menu is disabled. Test with menuconfig/allmodconfig fragments that toggle `WLAN_VENDOR_SILABS` and confirm `CONFIG_WFX` visibility.

Test signals: Source read size: 18 lines, 537 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/Makefile

Purpose: Connects the Silicon Labs wireless vendor directory to Kbuild.

Important APIs and types: `obj-$(CONFIG_WFX) += wfx/` descends into the WFx subdirectory when `CONFIG_WFX` is enabled.

Control flow and integration: Build recursion is controlled entirely by `CONFIG_WFX`; actual object composition is in `silabs/wfx/Makefile`.

State and persistence: No runtime state. The built module/object set is persisted only in build artifacts.

Dependencies: Depends on `CONFIG_WFX` from `wfx/Kconfig`.

Risks and test signals: Build tests should verify `CONFIG_WFX=n` omits the directory and `CONFIG_WFX=m/y` descends correctly without duplicate objects.

Test signals: Source read size: 3 lines, 67 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/Kconfig

Purpose: Defines the WFx driver Kconfig symbol for Silicon Labs WF200-family 802.11 chips.

Important APIs and types: `config WFX` is a tristate requiring `MAC80211`, either SPI or MMC support, and `MMC || !MMC` to prevent built-in WFx when MMC is modular. Help text notes SPI/SDIO bus support and Device Tree requirement for SDIO because reliable SDIO vendor IDs are not available.

Control flow and integration: The symbol controls compilation of the aggregate `wfx.o` object and conditional inclusion of SPI/SDIO bus objects. It also controls module availability for both bus drivers registered by `main.c`.

State and persistence: Persistent state is the `.config` choice `n/m/y`, which determines driver registration and module production.

Dependencies: Depends on mac80211 and bus subsystems. SPI and MMC dependencies map to `bus_spi.c` and `bus_sdio.c`.

Risks and test signals: Risks include invalid built-in/modular combinations with MMC, missing bus support, and user confusion when SDIO devices are not declared in Device Tree. Test build matrices for `WFX=m/y`, `SPI=y/m/n`, and `MMC=y/m/n`.

Test signals: Source read size: 13 lines, 506 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/Makefile

Purpose: Builds the Silicon Labs WFx aggregate driver object and selects bus-specific source files.

Important APIs and types: `wfx-y` lists core objects: bottom half, HW I/O, firmware loader, HIF MIB/TX/RX, queues, data TX/RX, scan, station callbacks, key handling, main probe, and debugfs/trace helpers. `wfx-$(CONFIG_SPI)` adds `bus_spi.o`; `wfx-$(subst m,y,$(CONFIG_MMC))` adds `bus_sdio.o` even when MMC is modular. `CFLAGS_debug.o = -I$(src)` supports local tracepoint include generation.

Control flow and integration: Kbuild links the listed objects into `wfx.o`, then `obj-$(CONFIG_WFX) += wfx.o` emits a built-in or module. Conditional bus objects provide the external `wfx_spi_driver` and `wfx_sdio_driver` symbols used by `main.c`.

State and persistence: No runtime state, but object inclusion decides which bus registration paths exist.

Dependencies: Depends on `CONFIG_WFX`, `CONFIG_SPI`, and `CONFIG_MMC`; also relies on `debug.c` defining tracepoints with local include paths.

Risks and test signals: Risks include unresolved bus driver symbols if Makefile conditions drift from `main.c` registration checks. Build tests should cover SPI-only, SDIO-only, both buses, module and built-in combinations, and tracepoint compilation.

Test signals: Source read size: 25 lines, 434 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bh.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bh.c

Purpose: Implements the WFx interrupt bottom half, serializing host-to-chip command/data transmission and chip-to-host message reception on a high-priority workqueue.

Important APIs and functions: `wfx_bh_register()` initializes work/completions/waitqueue; `wfx_bh_unregister()` flushes work. `wfx_bh_request_rx()` reads the control register on IRQ, saves `hif.ctrl_reg`, completes `ctrl_ready`, and queues work. `wfx_bh_request_tx()` queues work for pending commands or data. `wfx_bh_poll_irq()` polls control state during early boot. Internals include `device_wakeup()`, `device_release()`, `rx_helper()`, `bh_work_rx()`, `tx_helper()`, `bh_work_tx()`, `ack_sdio_data()`, and `bh_work()`.

Control flow and integration: The worker wakes the chip via optional GPIO, loops through up to 32 TX messages and 32 RX messages until both drain, acknowledges SDIO data after RX, and releases the chip when no TX buffers are in use. TX prioritizes synchronous `hif_cmd` requests over queued data frames, tracks firmware input-buffer credits in `hif.tx_buffers_used`, and assigns HIF sequence numbers. RX sizes come from `CTRL_NEXT_LEN_MASK` in the control register or piggyback trailer; messages are validated, confirmations decrement TX credits, sequence numbers are checked, and SKBs are handed to `wfx_handle_rx()`.

State and persistence: Uses `wdev->hif.ctrl_ready`, atomic `ctrl_reg`, TX/RX sequence counters, `tx_buffers_used`, `tx_buffers_empty`, workqueue state, optional wakeup GPIO, and firmware-advertised input-buffer count/size. This state is transient but data-path critical.

Dependencies: Depends on HWIO register access, bus `align_size()`, mac80211 SKBs, HIF command IDs, `wfx_tx_queues_get()`, and `wfx_handle_rx()`.

Risks and test signals: Risks include lost IRQ/control-register races, piggyback length mismatch, TX credit underflow, wakeup GPIO timeout, command/data starvation, and SDIO error bits left uncleared. Test IRQ RX, polled startup RX, command confirm, multi-TX confirm credit release, queued data TX, firmware sleep/wake races, malformed length handling, and flush/unregister while work is pending.

Test signals: Source read size: 324 lines, 8840 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bh.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bh.h

Purpose: Declares the WFx bottom-half state and request entry points.

Important APIs and types: `struct wfx_hif` stores bottom-half work, control-register readiness completion, TX sequence number, RX sequence number, atomic control register snapshot, TX buffer usage, and waitqueue for empty firmware TX buffers. Exported functions are `wfx_bh_register()`, `wfx_bh_unregister()`, `wfx_bh_request_rx()`, `wfx_bh_request_tx()`, and `wfx_bh_poll_irq()`.

Control flow and integration: Bus IRQ handlers call `wfx_bh_request_rx()`, TX producers call `wfx_bh_request_tx()`, early firmware startup may use `wfx_bh_poll_irq()`, and common probe/release bracket the lifecycle with register/unregister.

State and persistence: The header exposes the transient per-device HIF transport state embedded in `struct wfx_dev`.

Dependencies: Depends on Linux workqueue, completion, waitqueue, and atomic APIs.

Risks and test signals: Tests should verify initialization before IRQ subscription, flushing during release, waitqueue wakeups when TX credits reach zero, and sequence/credit state reset across probe failure paths.

Test signals: Source read size: 34 lines, 758 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bus.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bus.h

Purpose: Defines the WFx common bus abstraction used by the core driver to share SDIO and SPI implementations.

Important APIs and types: Register IDs cover config, control, in/out queue, AHB/SRAM data ports, base address, generic read/write, and frame-out registers. `struct wfx_hwbus_ops` supplies `copy_from_io`, `copy_to_io`, IRQ subscribe/unsubscribe, bus lock/unlock, transfer alignment, and wakeup enable hooks. It declares external `wfx_sdio_driver` and `wfx_spi_driver`.

Control flow and integration: `wfx_init_common()` stores these ops in `wdev`; HWIO, firmware loading, BH, and PM paths call them without knowing the physical bus. `main.c` registers the external SPI/SDIO drivers depending on Kconfig.

State and persistence: The abstraction itself has no state; bus-private state is passed as `hwbus_priv`.

Dependencies: Includes Linux SDIO and SPI type declarations because both bus driver symbols are declared here.

Risks and test signals: Risks include bus ops with incompatible locking/alignment semantics and missing driver symbols in build variants. Test both bus paths for identical register/data semantics, IRQ subscribe/unsubscribe lifecycle, and wakeup enable behavior.

Test signals: Source read size: 37 lines, 1078 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bus_sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bus_sdio.c

Purpose: Implements the WFx SDIO bus driver and maps SDIO register/IRQ/PM operations into `wfx_hwbus_ops`.

Important APIs and functions: `wfx_sdio_copy_from_io()` and `wfx_sdio_copy_to_io()` access SDIO register IDs shifted by two and use queue-mode buffer IDs for `WFX_REG_IN_OUT_QUEUE`. `wfx_sdio_irq_subscribe()` supports both SDIO function IRQ and out-of-band DT IRQ; `wfx_sdio_irq_unsubscribe()` tears them down. Probe validates function 1, matches DT platform data, enables the function, sets 64-byte block size, initializes common WFx state, and calls `wfx_probe()`. PM callbacks keep power and enable IRQ wake for WoWLAN-capable devices.

Control flow and integration: On IRQ, the handler calls `wfx_bh_request_rx()`. Probe stores `struct wfx_sdio_priv` as SDIO drvdata, passes `wfx_sdio_hwbus_ops` to `wfx_init_common()`, then lets common probe load firmware and register mac80211. Remove calls `wfx_release()` and disables the SDIO function.

State and persistence: `struct wfx_sdio_priv` tracks function pointer, core device, TX/RX queue buffer IDs, and optional OF IRQ. Queue buffer IDs wrap independently across RX modulo 4 and TX modulo 32.

Dependencies: Depends on Linux MMC/SDIO, OF IRQ parsing, device PM, WFx HWIO/BH/main, and Device Tree compatible data selecting firmware/PDS names.

Risks and test signals: Risks include wrong function number, missing DT compatible, out-of-band IRQ cleanup calling both free IRQ and `sdio_release_irq()`, queue buffer ID wrap bugs, alignment assumptions, and suspend without wake capability. Tests should cover DT compatibles, SDIO-only IRQ and external IRQ, PM keep-power/wake flags, block-size behavior, probe failure cleanup, and remove while BH work may be active.

Test signals: Source read size: 326 lines, 7985 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bus_sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bus_spi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bus_spi.c

Purpose: Implements the WFx SPI bus driver and maps SPI transfers, reset GPIO, IRQ, alignment, and PM wakeup into `wfx_hwbus_ops`.

Important APIs and functions: `wfx_spi_copy_from_io()` and `wfx_spi_copy_to_io()` build 16-bit register/length words with read/write markers, optionally byte-swap for 8-bit SPI or big-endian CPUs, and issue `spi_sync()`. IRQ subscription uses a threaded IRQ and calls `wfx_bh_request_rx()`. Probe sets default 16 bits/word, loads platform data from SPI ID, obtains optional reset GPIO, toggles reset, initializes common WFx state, and calls `wfx_probe()`. PM callbacks enable/disable IRQ wake.

Control flow and integration: SPI has no explicit bus lock beyond empty lock/unlock ops; HWIO serializes through the call path and SPI core transfers. Common probe handles firmware loading, IRQ subscription through these ops, and mac80211 registration.

State and persistence: `struct wfx_spi_priv` stores the SPI device, WFx core pointer, optional reset GPIO, and `need_swab` byte-order mode. Platform data provides firmware/PDS names and rising-clock preference.

Dependencies: Depends on Linux SPI, GPIO, IRQ, PM, OF/device IDs, and WFx common code. Compatible strings are matched for OF, while dynamic binding uses stripped modalias IDs.

Risks and test signals: Risks include in-place byte swapping of `const` TX buffers for config writes, unsupported bits-per-word, excessive SPI clock, missing reset GPIO, IRQ trigger mismatch, and byte-order mistakes. Tests should cover 8-bit and 16-bit controllers, big-endian builds, reset GPIO present/absent, IRQ wake suspend/resume, all compatible IDs, and firmware boot over SPI.

Test signals: Source read size: 321 lines, 8377 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bus_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_rx.c

Purpose: Converts firmware RX indications into mac80211 RX status and delivers data frames to the stack.

Important APIs and functions: `wfx_rx_cb()` is the exported RX data callback. `wfx_rx_handle_ba()` intercepts firmware-offloaded ADDBA/DELBA action frames to start/stop mac80211 RX BA reordering for API 3.6+ firmware.

Control flow and integration: HIF RX dispatch strips the HIF and RX indication headers before calling `wfx_rx_cb()`. The callback maps firmware status to MIC/decrypt/drop handling, validates minimum frame size, fills band/frequency/rate/RSSI/decryption status, handles BA action frames locally, and otherwise calls `ieee80211_rx_irqsafe()`.

State and persistence: It updates no persistent driver state except mac80211 BA session state through offload callbacks. RX status is transient in the SKB control block.

Dependencies: Depends on WFx HIF RX indication format, `wfx_api_older_than()`, mac80211 RX APIs, and `struct wfx_vif`.

Risks and test signals: Risks include wrong rate-index conversion, missing RSSI handling, dropping action frames too broadly, malformed SKB length, and decrypt/MIC flag mismatches. Tests should cover successful RX, MIC failure reporting, nonzero firmware status drops, legacy and API 3.6 BA behavior, encrypted frames, no-RSSI frames, and invalid short frames.

Test signals: Source read size: 93 lines, 2530 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_rx.h

Purpose: Declares the WFx RX data callback used by the HIF indication dispatcher.

Important APIs and types: Forward declarations for `struct wfx_vif`, `struct sk_buff`, and `struct wfx_hif_ind_rx`; exported function `wfx_rx_cb()`.

Control flow and integration: `hif_rx.c` calls `wfx_rx_cb()` when handling `HIF_IND_ID_RX`, after mapping the HIF interface to a vif and pulling protocol headers from the SKB.

State and persistence: No state is declared here.

Dependencies: Depends on HIF RX indication definitions from `hif_api_cmd.h` at implementation sites and mac80211 SKB semantics.

Risks and test signals: Build tests should confirm the callback signature stays aligned with `hif_rx.c` and `data_rx.c`; runtime tests should exercise RX indications for existing and missing vifs.

Test signals: Source read size: 17 lines, 380 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_tx.c

Purpose: Implements WFx mac80211 TX preparation, firmware TX policy caching, SKB queue insertion, TX confirmation processing, and flush/drop behavior.

Important APIs and functions: `wfx_tx()` is the mac80211 TX callback. Helpers include `wfx_tx_policy_init()`, `wfx_tx_policy_upload_work()`, `wfx_skb_tx_priv()`, `wfx_skb_txreq()`, `wfx_skb_wvif()`, `wfx_tx_confirm_cb()`, and `wfx_flush()`. Internal policy-cache functions build packed firmware retry-rate policies, find/reuse/free policy slots, upload missing policies, and stop/wake mac80211 queues when cache slots are exhausted.

Control flow and integration: TX chooses a vif, drops BA action frames handled by firmware, fixes retry rates into firmware-compatible descending policies, reserves tailroom for ICV/MIC, pushes HIF/TX headers into the SKB, assigns interface/packet ID/peer link/retry policy/queue/frame format flags, enqueues to normal/CAB/offchannel queue, and requests BH TX. Confirmations find the pending SKB by packet ID, fill mac80211 retry/status information from firmware ack counts/rate/status, trim reserved crypto tailroom, set ACK/noack/filtered flags, release retry-policy usage, and report status.

State and persistence: Uses per-vif `tx_policy_cache`, per-SKB `wfx_tx_priv` in `rate_driver_data`, `wdev->packet_id`, `wdev->tx_pending`, queue pending counters, and `after_dtim_tx_allowed`. Policy entries persist across frames until reset/interface removal.

Dependencies: Depends on mac80211 TX control/status APIs, HIF TX request/confirm ABI, queue helpers, station link IDs, key tailroom flags, BH scheduling, and MIB policy upload.

Risks and test signals: Risks include SKB headroom/alignment errors, retry-policy cache exhaustion deadlocks, packet ID lookup failures, stale vif IDs after interface removal, incorrect firmware/Linux queue inversion, offchannel interface ID misuse, and requeue/DTIM handling. Tests should cover data/mgmt TX, offchannel TX, CAB after DTIM, encrypted TKIP/CCMP tailroom, multi-rate retries, policy upload races, unknown packet IDs, failed TX statuses, flush with drop, and frozen-chip pending drop.

Test signals: Source read size: 594 lines, 17979 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_tx.h

Purpose: Declares WFx TX private SKB state, firmware TX retry-policy cache structures, and TX/flush/status helper APIs.

Important APIs and types: `struct wfx_tx_policy` holds packed firmware rates, list link, upload flag, and usage count. `struct wfx_tx_policy_cache` owns 15 policy slots, a lock, and used/free lists. `struct wfx_tx_priv` stores ICV size, vif ID, and transmit timestamp in `ieee80211_tx_info.rate_driver_data`. Exports include policy init/upload work, mac80211 `wfx_tx()`/`wfx_flush()`, confirmation callback, and SKB accessors.

Control flow and integration: `data_tx.c` stores per-frame private state in `wfx_tx_priv`, queue code records transmit timestamps, and confirmation/flush code uses the accessors to recover HIF request and vif state.

State and persistence: The cache is persistent per vif; SKB private data is transient per frame.

Dependencies: Depends on Linux list/spinlock/workqueue, mac80211 TX structures, and HIF TX MIB constants for policy count/invalid ID.

Risks and test signals: Tests should assert `wfx_tx_priv` fits in `rate_driver_data`, policy slot accounting wakes queues correctly, and callers do not touch `tx_info->control` after it is repurposed.

Test signals: Source read size: 53 lines, 1360 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/debug.c

Purpose: Implements WFx trace name helpers and debugfs interfaces for counters, RX stats, TX power loop information, PDS upload, and raw HIF command injection.

Important APIs and functions: `wfx_get_hif_name()`, `wfx_get_mib_name()`, and `wfx_get_reg_name()` map numeric IDs to trace strings. Debugfs show/write handlers include `wfx_counters_show()`, `wfx_rx_stats_show()`, `wfx_tx_power_loop_show()`, `wfx_send_pds_write()`, and `wfx_send_hif_msg_*()`. `wfx_debug_init()` creates debugfs files under the wiphy debugfs directory.

Control flow and integration: Counter reads iterate each vif and call `wfx_hif_get_counters_table()`. RX stats and TX power loop show functions read data last populated by generic HIF indications under locks. PDS write copies user data and calls `wfx_send_pds()`. Raw HIF write parses hex user input into a request, sends it with `wfx_cmd_send()`, and exposes the reply through read.

State and persistence: Debugfs raw HIF sessions allocate `struct dbgfs_hif_msg` per open file. RX stats and TX power loop state persist in `wdev` and are updated asynchronously by firmware generic indications.

Dependencies: Depends on debugfs/seq_file/usercopy, WFx HIF/MIB/debug name tables, mac80211 wiphy debugfs, and generated trace headers.

Risks and test signals: Risks include unsafe debugfs raw command injection, user buffer parsing/size errors, stale stats, and missing vif handling. Tests should cover debugfs file creation, counter reads on zero/two vifs, PDS write validation, raw HIF write/read with malformed and valid hex, and locking around async stats updates.

Test signals: Source read size: 331 lines, 8801 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/debug.h

Purpose: Declares WFx debug and trace-name helper APIs.

Important APIs and types: Exports `wfx_get_hif_name()`, `wfx_get_mib_name()`, `wfx_get_reg_name()`, and `wfx_debug_init()`.

Control flow and integration: HIF command error logging uses HIF/MIB names, tracepoints use register names, and common probe calls `wfx_debug_init()` after successful `ieee80211_register_hw()`.

State and persistence: No state is declared; debugfs state is implementation-private in `debug.c`.

Dependencies: Depends on `struct wfx_dev` and debugfs availability through implementation includes.

Risks and test signals: Build and runtime tests should verify debugfs initialization failure unwinds mac80211 registration and name helpers return fallback strings for unknown IDs.

Test signals: Source read size: 19 lines, 419 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/fwio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/fwio.c

Purpose: Implements secure firmware loading and early hardware initialization for WF200 devices.

Important APIs and functions: `wfx_init_device()` configures direct access/byte order/reset, validates config register/device ID, initializes IGPR values, wakes the WLAN CPU, releases reset, loads firmware, and enables data IRQs. Firmware helpers include `get_firmware()`, `wait_ncp_status()`, `upload_firmware()`, `load_firmware_secure()`, `wfx_sram_write_dma_safe()`, `print_boot_status()`, and `init_gpr()`.

Control flow and integration: Probe calls this before normal IRQ subscription. Secure loading handshakes through DCA SRAM registers: host ready, read bootloader/PTE keyset, load matching `*.sec` firmware, write signature/hash/version/image size, stream 1 KiB blocks into the download FIFO with PUT/GET flow control, wait for authentication, and signal jump. After boot, common probe polls for the startup HIF indication.

State and persistence: Stores `wdev->keyset` from firmware metadata. Firmware image state is pushed into device SRAM/DCA registers; GPR config persists in chip until reset.

Dependencies: Depends on Linux firmware loader, hex parsing, HWIO SRAM/AHB/register helpers, PDS/firmware filenames from platform data, and WF200 boot ROM DCA status constants.

Risks and test signals: Risks include incompatible keyset selection, vmalloc firmware data used for DMA without bounce, FIFO flow-control timeout, firmware size misalignment, boot-status ambiguity, byte-order/direct-access mistakes, and development hardware wake timeout. Tests should cover keyset-specific and fallback firmware names, corrupted KEYSET header, wrong keyset, DMA bounce path, DCA timeouts, auth fail errors, SPI/SDIO boot, and startup indication after load.

Test signals: Source read size: 389 lines, 11444 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/fwio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/fwio.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/fwio.h

Purpose: Declares the firmware-device initialization entry point.

Important APIs and types: Exports `int wfx_init_device(struct wfx_dev *wdev)`.

Control flow and integration: Called by `wfx_probe()` after bottom-half registration and before polling for the firmware startup indication.

State and persistence: The implementation initializes chip registers, loads firmware, and fills `wdev->keyset`; the header itself owns no state.

Dependencies: Depends on `struct wfx_dev` from WFx private data.

Risks and test signals: Tests should cover callers handling negative errors and ensuring BH polling is active before waiting for firmware-ready indications.

Test signals: Source read size: 15 lines, 272 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/fwio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_api_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_api_cmd.h

Purpose: Defines the WF200 host-interface command ABI for request, confirmation, and indication messages used by command TX/RX, data TX/RX, scanning, association, keys, AP start, and link mapping.

Important APIs and types: Request/confirmation IDs cover reset, read/write MIB, scan start/stop, TX, join, PM mode, BSS params, add/remove key, EDCA, AP start, beacon transmit, update IE, and map link. Indication IDs cover RX, scan complete, join complete, PM complete, suspend/resume TX, and events. Packed structures define each command body, TX request/confirm and multi-confirm format, RX indication metadata, scan channel/SSID list, join/start payloads, PM/BSS/EDCA settings, key material variants for WEP/TKIP/AES/WAPI/IGTK, event indications, and link IDs.

Control flow and integration: `hif_tx.c` allocates and fills these request structures; `hif_rx.c` validates confirmations and indications against IDs and dispatches them; `data_tx.c` writes `wfx_hif_req_tx` directly into SKBs; `key.c` fills `wfx_hif_req_add_key`; `scan.c` uses scan complete counts.

State and persistence: The ABI encodes firmware-persistent state such as key table entries, peer link map, BSS join/start configuration, PM mode, EDCA queue parameters, template updates, retry policy references, and per-packet TX status.

Dependencies: Depends on `hif_api_general.h`, Linux Ethernet/mac80211 constants, and firmware layout compatibility with packed LE fields and C bitfields.

Risks and test signals: Risks include C bitfield layout portability, endian mistakes, flexible-array size calculations, packet ID uniqueness assumptions, firmware API version changes, and key material ordering. Tests should validate structure sizes/offsets where possible, command/confirm ID matching, scan list bounds, key type fills, TX status parsing, RX metadata mapping, link ID limits, and event handling.

Test signals: Source read size: 553 lines, 13650 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_api_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_api_general.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_api_general.h

Purpose: Defines the general WF200 HIF message header, common request/confirmation/indication IDs, status codes, rate indexes, startup capabilities, generic indications, error/exception payloads, and secure-link state values.

Important APIs and types: `struct wfx_hif_msg` is the common wire header with length, ID, interface, sequence number, encryption bits, and body. General IDs include configuration, GPIO control, secure-link commands, rollback/PTA commands, shutdown, startup/wakeup/generic/error/exception indications. Status macros encode firmware return values. `enum wfx_hif_api_rate_index` maps 802.11b/g/n rates. `struct wfx_hif_ind_startup` carries hardware ID, OPN/UID, input buffer count/size, link/interface counts, MAC addresses, API/firmware versions, secure-link mode, region/channel data, supported rates, and label. Generic indication payloads carry RX test stats and TX power loop info.

Control flow and integration: BH reads/writes messages using this header and sequence counters. Common probe waits for startup indication and copies it into `wdev->hw_caps`. HIF TX uses status values for command return handling. Debugfs and generic indication handlers expose stats/power-loop data. Probe rejects unsupported firmware API and enforced secure-link mode.

State and persistence: Startup capabilities persist in `wdev->hw_caps` and drive buffer credits, max frame size, API compatibility, MAC addresses, regulatory flags, TDLS availability, and operational mode decisions.

Dependencies: Depends on Linux types and Ethernet address length. Included by command and MIB ABI headers.

Risks and test signals: Risks include interpreting little-endian status constants, unsupported encrypted HIF messages, sequence mismatch, startup layout changes, and secure-link modes not implemented by this driver. Tests should cover startup parsing, API major/minor gating, buffer size/count use, firmware error/exception indications, generic stats update, shutdown no-reply behavior, and unknown status reporting.

Test signals: Source read size: 252 lines, 7617 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_api_general.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_api_mib.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_api_mib.h

Purpose: Defines WF200 MIB IDs and packed MIB payloads used to configure global and per-interface firmware behavior.

Important APIs and types: MIB IDs cover global power/multi-message settings, data filtering, ARP/NS tables, RX/beacon filters, counters/statistics, MAC address, WEP default key, RTS/slot/TX power, protection, template frames, beacon wakeup, RCPI/RSSI thresholds, block-ack policy, association mode, U-APSD, TX retry policy, PMF, keep-alive, inactivity, and beacon stats. Structures include global operational power mode, multi-message setting, ARP IPv4 table, RX filter, beacon filter table/enable, legacy and extended counters, MAC address, template frame, beacon wake period, RSSI threshold, block-ack policy, association mode, U-APSD info, retry policy, PMF policy, and keep-alive period.

Control flow and integration: `hif_tx_mib.c` wraps these structures in read/write MIB commands for station/AP setup, power management, beacon filtering, debug counters, template upload, queue policy, ARP filtering, and operational power mode after probe.

State and persistence: MIB writes configure firmware state that persists until reset, interface removal, or explicit overwrite. Counter MIB reads expose firmware-maintained statistics.

Dependencies: Depends on `hif_api_general.h`, firmware MIB numbering, packed LE layout, and HIF command read/write MIB wrappers.

Risks and test signals: Risks include MIB ID mismatch, variable-length table sizing, older firmware counter-table compatibility, byte-order conversion for signed values, and invalid bounds for wake intervals/policy indexes. Tests should cover every MIB wrapper, legacy vs extended counters, beacon filter programming, template frame size limit, RSSI threshold conversion, U-APSD bits, block-ack policy in combo mode, and ARP filter updates.

Test signals: Source read size: 346 lines, 9573 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_api_mib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_rx.c

Purpose: Dispatches WFx HIF confirmations and indications received from firmware.

Important APIs and functions: `wfx_handle_rx()` is the public dispatcher. Confirmation handlers include generic command confirmation, single TX confirm, and multi-TX confirm. Indication handlers process startup, wakeup, RX, event, PM complete, scan complete, join complete, suspend/resume TX, generic stats, asynchronous errors, and exceptions.

Control flow and integration: BH passes each complete SKB to `wfx_handle_rx()`. RX data indications are handed to `wfx_hif_receive_indication()` and then `wfx_rx_cb()`. If a synchronous command lock is held and the ID matches `hif_cmd.buf_send`, generic confirmation copies the reply/status and completes `hif_cmd.done`. Otherwise the dispatcher searches the static handler table. Error and exception indications log payloads and freeze the chip.

State and persistence: Updates `wdev->hw_caps`, completes `firmware_ready`, completes per-vif `set_pm_mode_complete` and `scan_complete`, updates RX stats and TX power loop info under locks, schedules/cancels beacon loss work, and sets `chip_frozen` on firmware fatal errors.

Dependencies: Depends on scan, BH, station, data RX/TX callbacks, HIF command/general layouts, SKB lifetime rules, and mac80211 notifications.

Risks and test signals: Risks include unexpected confirmation while no command is pending, command/reply ID mismatch, reply buffer length mismatch, indications for missing vifs, error/exception recovery freezing TX, and SKB lifetime differences for RX data vs other messages. Tests should cover all handler IDs, multi-TX confirm, startup completion, PM/scan completions, BSS lost/regained, generic stats updates, firmware error/exception, unknown indications, and mismatched command confirmations.

Test signals: Source read size: 391 lines, 11976 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_rx.h

Purpose: Declares the HIF RX dispatcher entry point.

Important APIs and types: Exports `void wfx_handle_rx(struct wfx_dev *wdev, struct sk_buff *skb)`.

Control flow and integration: `bh.c` calls this after validating a received HIF message and putting the firmware length into the SKB. The dispatcher owns SKB lifetime after the call.

State and persistence: No state is declared here; implementation updates command completions, stats, scan/PM state, and mac80211 callbacks.

Dependencies: Depends on `struct wfx_dev`, SKB ownership, and HIF message layout.

Risks and test signals: Test callers must not free SKBs after handing them to `wfx_handle_rx()` and should cover RX data indications separately because they retain SKB ownership until `wfx_rx_cb()`.

Test signals: Source read size: 17 lines, 407 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx.c

Purpose: Implements host-to-firmware HIF request construction, synchronous command sending, and high-level request helpers for configuration, reset, scan, join, keys, EDCA, PM, AP start, beacon transmit, link mapping, and IE update.

Important APIs and functions: `wfx_init_hif_cmd()` initializes command serialization. `wfx_cmd_send()` is the central synchronous/asynchronous send path. Public wrappers include `wfx_hif_shutdown()`, `wfx_hif_configuration()`, `wfx_hif_reset()`, `wfx_hif_read_mib()`, `wfx_hif_write_mib()`, `wfx_hif_scan_uniq()`, `wfx_hif_scan()`, `wfx_hif_stop_scan()`, `wfx_hif_join()`, `wfx_hif_set_bss_params()`, `wfx_hif_add_key()`, `wfx_hif_remove_key()`, `wfx_hif_set_edca_queue_params()`, `wfx_hif_set_pm()`, `wfx_hif_start()`, `wfx_hif_beacon_transmit()`, `wfx_hif_map_link()`, and `wfx_hif_update_ie_beacon()`.

Control flow and integration: Each wrapper allocates a `wfx_hif_msg`, fills the common header with `wfx_fill_header()`, populates a packed command body, calls `wfx_cmd_send()`, then frees the request. `wfx_cmd_send()` serializes with `hif_cmd.lock`, publishes `buf_send`/reply buffer, completes `hif_cmd.ready` for BH TX, optionally polls IRQ during boot, waits for `hif_cmd.done`, logs slow/missing replies, freezes the chip on timeout, and formats HIF/MIB names for diagnostics.

State and persistence: Uses `wdev->hif_cmd` lock/completions/buffers/return code and `wdev->chip_frozen`. Firmware state changed by wrappers includes PDS configuration, reset, scan state, BSS/join state, key table, EDCA/PM/AP/link/IE state.

Dependencies: Depends on BH scheduling, HWIO control for shutdown fallback, HIF command/general layouts, mac80211 channel/BSS/scan/queue types, debug name helpers, and station API-version checks.

Risks and test signals: Risks include command timeout deadlocks, no-reply shutdown ordering, reply buffer size mismatch returning `-EIO`, MIB read copying variable lengths, API-version-specific add-key interface ID, old queue ID mapping, scan bounds, and signed/unsigned status handling. Tests should cover command serialization, boot polling, timeout/freeze path, all request wrappers, scan passive/active timing, join without BSS/SSID, EDCA queue mapping for old/new APIs, PM idle conversion, and shutdown during release.

Test signals: Source read size: 537 lines, 15924 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx.h

Purpose: Declares HIF command serialization state and high-level WFx request helper APIs.

Important APIs and types: `struct wfx_hif_cmd` contains a mutex, ready/done completions, outgoing buffer pointer, incoming reply pointer/length, and return code. Exports `wfx_init_hif_cmd()`, `wfx_cmd_send()`, MIB read/write, start/reset/join/map-link/key/PM/BSS/EDCA/beacon/scan/configuration/shutdown helpers.

Control flow and integration: Common probe initializes this state in `wfx_init_common()`. BH consumes `hif_cmd.ready` before data queues, and HIF RX completes `done` on matching confirmations.

State and persistence: The struct is transient per synchronous command and persists as a per-device serialization object.

Dependencies: Depends on Linux mutex/completion, HIF message type, and mac80211/cfg80211 forward declarations.

Risks and test signals: Tests should verify commands cannot overlap, no-reply commands flush the BH workqueue, and callers respect reply buffer sizes for MIB reads.

Test signals: Source read size: 62 lines, 2527 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx_mib.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx_mib.c

Purpose: Implements typed wrappers around HIF read/write MIB commands for WFx firmware configuration.

Important APIs and functions: Wrappers include output power, beacon wakeup period, RCPI/RSSI thresholds, counters table, MAC address, RX filter, beacon filter table/control, global operational power mode, template frame upload, PMF policy, block-ack policy, association mode, TX retry policy, keep-alive, ARP IPv4 filter, multi-TX confirmation enable, U-APSD information, ERP protection, slot time, WEP default key ID, and RTS threshold.

Control flow and integration: Station/AP/scan/data/debug paths call these helpers rather than constructing raw MIB payloads. Each helper fills a specific packed MIB structure, handles local conversions and bounds, and calls `wfx_hif_write_mib()` or `wfx_hif_read_mib()`. Older firmware uses the shorter counters table and leaves extended fields initialized to `0xFF`.

State and persistence: Each write persists in firmware until interface reset/removal or global shutdown. Counter reads and generic stats expose firmware-maintained state but do not mutate driver state by themselves.

Dependencies: Depends on HIF MIB ABI, HIF TX command wrappers, mac80211 SKBs/templates, WFx API-version helper, and Ethernet address helpers.

Risks and test signals: Risks include wrong RSSI-to-RCPI conversion, wake interval bounds, template SKB headroom manipulation, flexible-array allocation sizes, old firmware counters compatibility, U-APSD bit mapping, and policy index limits. Tests should exercise each wrapper, invalid wake periods, template frames at/over 700 bytes, counters on old/new APIs, beacon filter table lengths, ARP filter clearing, and multi-TX confirmation enable.

Test signals: Source read size: 307 lines, 8953 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx_mib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx_mib.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx_mib.h

Purpose: Declares high-level MIB helper APIs used by station, scan, debug, data TX policy, and probe code.

Important APIs and types: Exports setters/getters for output power, beacon wake period, RSSI threshold, counters, MAC address, RX/beacon filters, operational power mode, template frame, PMF, block-ack policy, association mode, TX retry policy, keep-alive, ARP IPv4 filters, multi-TX confirmations, U-APSD, ERP protection, slot time, WEP default key, and RTS threshold.

Control flow and integration: These helpers abstract `wfx_hif_read_mib()`/`wfx_hif_write_mib()` so mac80211 callbacks can update firmware with typed arguments.

State and persistence: No state is declared; firmware MIB state is persistent after writes.

Dependencies: Depends on `hif_api_mib.h`, SKBs for template upload, and `struct wfx_vif`/`wfx_dev`.

Risks and test signals: Build tests should keep prototypes synchronized with implementation; runtime tests should validate the mac80211 callbacks call the correct helper for each changed flag.

Test signals: Source read size: 48 lines, 2300 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx_mib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hwio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hwio.c

Purpose: Implements low-level WFx register, data-queue, SRAM, and AHB I/O using the selected bus operations.

Important APIs and functions: Public helpers include `wfx_data_read()`, `wfx_data_write()`, SRAM/AHB buffer and register read/write, config/control register read/write/write_bits, and IGPR read/write. Internal helpers perform 32-bit register I/O, masked read-modify-write, indirect SRAM/AHB access through base address and prefetch bits, and locked tracing variants.

Control flow and integration: Firmware boot uses SRAM/AHB access for DCA/FIFO/GPR/register setup. BH uses data queue and control/config register access. Common probe and shutdown use config/control operations. All public helpers lock/unlock through `hwbus_ops`, perform endian conversion for 32-bit values, and trace accesses.

State and persistence: The code does not own driver state beyond transient buffers, but it mutates chip config/control/base/IGPR/SRAM/AHB registers and relies on bus-level serialization.

Dependencies: Depends on `wfx_hwbus_ops`, bus register IDs, chip config/control bit definitions, tracepoints, kmalloc-backed DMA-safe temporary buffers, and firmware register semantics.

Risks and test signals: Risks include stack/vmalloc buffers passed to DMA-capable bus ops, unaligned buffers, indirect prefetch timeout, masked writes with invalid values, lock/unlock imbalance, returning undefined values after failed reads, and register endian errors. Tests should cover config/control reads/writes, write_bits, data queue alignment, SRAM/AHB buffer and register access, prefetch timeout path, IGPR access, and injected bus errors on SPI/SDIO.

Test signals: Source read size: 332 lines, 8438 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hwio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hwio.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hwio.h

Purpose: Declares WFx low-level I/O APIs and register bit definitions for config, control, and IGPR access.

Important APIs and types: Exports data queue read/write, SRAM/AHB buffer and register helpers, config/control register helpers, and IGPR read/write. Defines config error bits, byte order/direct-access/prefetch/reset/IRQ/clock/device ID bits, control next-length/wakeup/ready bits, and IGPR field masks.

Control flow and integration: BH uses data/control/config helpers; firmware loading uses SRAM/IGPR/config/control helpers; bus drivers supply the backend operations.

State and persistence: Header constants describe device register state. Callers must provide DMA-safe kmalloc buffers for data and indirect I/O.

Dependencies: Depends on Linux types and WFx bus abstraction at implementation sites.

Risks and test signals: Risks include misuse of stack buffers, confusing SPI/SDIO-specific config error bits, and incorrect `CTRL_NEXT_LEN_MASK` handling. Tests should enable DMA debugging, validate register bit masks, and exercise both bus backends.

Test signals: Source read size: 78 lines, 3402 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hwio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/key.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/key.c

Purpose: Implements mac80211 key install/remove for WFx firmware key table entries.

Important APIs and functions: `wfx_set_key()` is the mac80211 callback. Internals allocate/free key table indexes with `wfx_alloc_key()`/`wfx_free_key()` and fill firmware key payloads for WEP pair/group, TKIP pair/group, CCMP pair/group, SMS4/WAPI pair/group, and AES-CMAC/IGTK group keys.

Control flow and integration: On `SET_KEY`, it allocates a firmware key index, reads initial RX sequence, fills `wfx_hif_req_add_key`, sends `wfx_hif_add_key()`, sets mac80211 flags for IV/tailroom handling, stores `hw_key_idx`, and returns success. On `DISABLE_KEY`, it frees the index and sends `wfx_hif_remove_key()`. The path is serialized by `wdev->conf_mutex`.

State and persistence: `wdev->key_map` tracks allocated firmware key slots. Firmware key entries persist until removed/reset. mac80211 `key->hw_key_idx` persists the slot mapping.

Dependencies: Depends on mac80211 key flags/sequences/cipher IDs, HIF key ABI, Ethernet helpers, and `memreverse()` for PN/IPN ordering.

Risks and test signals: Risks include key slot leaks on command failure, pairwise key without station, TKIP MIC key direction differences in AP vs STA, sequence counter endian/reversal, unsupported ciphers, and removing invalid indexes. Tests should cover all supported ciphers, group/pairwise paths, AP/STA TKIP group MIC selection, AES-CMAC MMIE generation, slot exhaustion, add-key failure rollback, and disable-key consistency.

Test signals: Source read size: 227 lines, 7619 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/key.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/key.h

Purpose: Declares the WFx mac80211 key callback.

Important APIs and types: Exports `wfx_set_key(struct ieee80211_hw *, enum set_key_cmd, struct ieee80211_vif *, struct ieee80211_sta *, struct ieee80211_key_conf *)`.

Control flow and integration: `main.c` installs this callback in `ieee80211_ops`; `key.c` implements firmware key-table programming and removal.

State and persistence: No state is declared here; implementation uses `wdev->key_map` and `key->hw_key_idx`.

Dependencies: Depends on mac80211 key abstractions.

Risks and test signals: Build tests should keep signature aligned with current mac80211 API; runtime tests should cover both SET_KEY and DISABLE_KEY callbacks.

Test signals: Source read size: 19 lines, 438 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/main.c

Purpose: Implements common WFx device allocation/probe/release, mac80211 capability registration, firmware/PDS startup, bus-driver registration, and module init/exit.

Important APIs and functions: `wfx_init_common()` allocates `ieee80211_hw`, sets hardware/wiphy capabilities, copies platform data, gets wakeup GPIO, initializes locks/completions/work/queues/HIF command state, and attaches devm cleanup. `wfx_probe()` creates the BH workqueue, loads firmware via `wfx_init_device()`, waits for startup, validates API/secure-link mode, applies regulatory hints, uploads PDS, subscribes IRQs, enables multi-TX confirmations and power mode, selects MAC addresses, registers mac80211, and initializes debugfs. `wfx_release()` unregisters hw, sends shutdown, unsubscribes IRQ, flushes BH, and destroys the workqueue. Module init/exit register/unregister SPI and SDIO drivers depending on Kconfig.

Control flow and integration: Bus probe calls `wfx_init_common()` then `wfx_probe()`. Early boot disables wakeup GPIO use and uses polled IRQ until firmware startup indication arrives. After PDS and IRQ setup, the driver switches to quiescent or doze power mode and exposes the device to mac80211. Release reverses registration and sends a no-reply shutdown.

State and persistence: Initializes persistent `wfx_dev` state: platform data, bus ops/private pointer, vif array, addresses, firmware caps, keyset, locks, queues, work items, stats locks, key map, packet ID, and BH workqueue. Firmware caps and MAC addresses drive later runtime behavior.

Dependencies: Depends on mac80211/cfg80211, OF MAC/PDS properties, firmware loader, GPIO, SPI/SDIO driver symbols, WFx FWIO/BH/HIF/MIB/debug/key/scan/sta/data modules, and firmware startup indication.

Risks and test signals: Risks include probe failure unwind ordering, wakeup GPIO races during boot, PDS absence or corruption, unsupported firmware API, enforced secure-link rejection, IRQ misconfiguration, MAC address fallback/randomization, TDLS feature gating, and bus-driver symbol availability. Tests should cover successful SPI/SDIO probe, firmware timeout, PDS missing vs invalid, API/secure-link rejection, IRQ subscribe failure, mac80211 registration failure, debugfs failure unwind, release path, and module init rollback if second bus registration fails.

Test signals: Source read size: 525 lines, 15880 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/main.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/main.h

Purpose: Declares common WFx platform data and common probe/lifecycle helper APIs.

Important APIs and types: `struct wfx_platform_data` carries firmware base name, PDS file name, wakeup GPIO, and rising-clock preference. Exports `wfx_init_common()`, `wfx_probe()`, `wfx_release()`, `wfx_api_older_than()`, and `wfx_send_pds()`.

Control flow and integration: SPI/SDIO bus drivers supply platform data and bus ops to `wfx_init_common()`, then call `wfx_probe()`. `wfx_release()` is used during bus remove. API-version checks gate firmware compatibility in BH, data RX, station, and HIF paths. Debugfs can call `wfx_send_pds()` to upload PDS chunks.

State and persistence: Platform data persists inside `wdev->pdata`, including optional DT-overridden PDS file and wakeup GPIO.

Dependencies: Depends on Linux device/GPIO APIs, WFx HIF general startup definitions, and bus abstraction.

Risks and test signals: Tests should cover platform data copying, DT PDS override, optional wakeup GPIO handling, API comparison boundary cases, and PDS chunk validation.

Test signals: Source read size: 41 lines, 1148 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/queue.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/queue.c

Purpose: Implements WFx software queues between mac80211 TX and the BH firmware TX path, including TX locks, flushes, weighted queue selection, pending-frame lookup, and drop diagnostics.

Important APIs and functions: `wfx_tx_lock()`, `wfx_tx_unlock()`, `wfx_tx_flush()`, and `wfx_tx_lock_flush()` provide global TX gating. Queue APIs initialize/check/drop/enqueue per-vif queues and select the next HIF message with `wfx_tx_queues_get()`. Pending helpers manage `wdev->tx_pending`, locate confirms by packet ID, drop pending frames on frozen chip, dump old frames, and compute firmware delay.

Control flow and integration: `data_tx.c` enqueues SKBs into normal/CAB/offchannel queues; BH calls `wfx_tx_queues_get()` when firmware credits are available. Queue selection sorts all vif/AC queues by pending weight, prioritizes offchannel frames, blocks normal/CAB during scan as needed, allows CAB only after DTIM, and then normal traffic. Pending SKBs move to `tx_pending` when handed to firmware and are removed by TX confirmations.

State and persistence: Per-vif queues store normal/CAB/offchannel SKB heads and `pending_frames` counts. Global `tx_lock`, `tx_pending`, `tx_dequeue`, `hif.tx_buffers_empty`, `chip_frozen`, and `after_dtim_tx_allowed` coordinate flow control.

Dependencies: Depends on mac80211 queue mapping, SKB queues, atomics, scan lock, BH TX request, data TX SKB accessors, and station/vif iteration.

Risks and test signals: Risks include pending counter imbalance, TX lock underflow, flush timeout freezing the chip, CAB starvation, scan/offchannel ordering, packet ID lookup while list unlocked, and queue weight fairness. Tests should cover multi-vif AC scheduling, scan lock blocking normal traffic, CAB after DTIM, offchannel priority, flush with and without drop, pending confirm lookup, frozen-chip drop, and queue-empty assertions on interface removal.

Test signals: Source read size: 322 lines, 8842 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/queue.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/queue.h

Purpose: Declares WFx TX queue structures and queue/pending/flush helper APIs.

Important APIs and types: `struct wfx_queue` contains normal, CAB, and offchannel SKB queues plus pending-frame count and scheduling priority. Exports TX lock/flush helpers, queue init/check/has_cab/put/get/drop helpers, pending lookup/drop/delay/dump helpers, and queue-empty check.

Control flow and integration: Data TX, station AP TIM handling, BH TX, and flush/remove paths use these APIs to move SKBs from mac80211 to firmware and back to status reporting.

State and persistence: Per-vif queue state persists for the lifetime of an interface; pending state persists until firmware confirmation or frozen-chip cleanup.

Dependencies: Depends on SKB queues, atomics, and HIF message forward declarations from adjacent headers.

Risks and test signals: Tests should verify queue lifecycle on add/remove interface, pending count accuracy, CAB detection, and frozen-device cleanup contracts.

Test signals: Source read size: 45 lines, 1488 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/scan.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/scan.c

Purpose: Implements hardware scan and remain-on-channel support by programming firmware scan requests and converting scan-complete indications into mac80211 callbacks.

Important APIs and functions: `wfx_hw_scan()`, `wfx_cancel_hw_scan()`, `wfx_scan_complete()`, `wfx_remain_on_channel()`, and `wfx_cancel_remain_on_channel()` are mac80211-facing. Work functions `wfx_hw_scan_work()` and `wfx_remain_on_channel_work()` perform serialized scan execution. Helpers update the probe request template and send channel batches with compatible power/NO_IR properties.

Control flow and integration: `wfx_hw_scan()` records the request and schedules work to avoid completing before callback return. Work locks `conf_mutex` and `scan_lock`, aborts an in-progress join via reset, uploads probe template, chunks channels, locks/flushed TX, starts firmware scan, waits for `scan_complete`, stops scan on timeout/cancel, restores output power if needed, unlocks TX, then calls `ieee80211_scan_completed()`. Remain-on-channel hijacks a one-channel scan, notifies ready/expired, and resumes TX.

State and persistence: Per-vif `scan_req`, `scan_complete`, `scan_nb_chan_done`, `scan_abort`, remain-on-channel channel/duration, and work items store scan state. Firmware scan state persists until scan complete or stop.

Dependencies: Depends on HIF scan/stop/template/output-power helpers, station reset/join state, TX lock/flush, mac80211/cfg80211 scan and ROC APIs, and `scan_lock` blocking TX queues.

Risks and test signals: Risks include scan work racing with cancel, firmware scan not stopping, channel batching logic errors, join abort side effects, lock ordering with config/scan locks, and ROC support only for API 3.10+. Tests should cover active/passive scans, multiple SSIDs and IE lengths, cancellation, timeout recovery, join-in-progress abort, output power restore, ROC success/cancel/timeout, and unsupported old API.

Test signals: Source read size: 209 lines, 5964 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/scan.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/scan.h

Purpose: Declares WFx scan and remain-on-channel mac80211 callbacks plus scan-completion helper.

Important APIs and types: Exports `wfx_hw_scan()`, `wfx_cancel_hw_scan()`, `wfx_scan_complete()`, `wfx_remain_on_channel()`, `wfx_cancel_remain_on_channel()`, and their work functions.

Control flow and integration: `main.c` wires these into `ieee80211_ops`; `hif_rx.c` calls `wfx_scan_complete()` on firmware scan-complete indications.

State and persistence: State is stored in `struct wfx_vif` fields declared in `wfx.h`.

Dependencies: Depends on mac80211 scan/ROC types and WFx vif private data.

Risks and test signals: Build tests should keep callback signatures current with mac80211; runtime tests should ensure completion is delivered for normal scan, abort, and ROC.

Test signals: Source read size: 28 lines, 886 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/scan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/sta.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/sta.c

Purpose: Implements the WFx mac80211 station/AP/IBSS/interface/configuration callbacks and firmware state coordination for BSS, PM, filters, beaconing, TIM, link IDs, channel contexts, WoWLAN, and thermal suspend/resume events.

Important APIs and functions: Public callbacks include start/stop, add/remove interface, configure filter, conf_tx, set RTS/default key, BSS info changed, sta_add/remove, start/stop AP, join/leave IBSS, set_tim, ampdu_action, channel context assign/unassign, suspend/resume/set_wakeup, and update PM. Firmware callback helpers include cooling timeout, hot-device suspend, multicast suspend/resume, RSSI report, and reset.

Control flow and integration: Interface add initializes per-vif work/completions/queues/policies, assigns a vif slot, sets MAC address, and adjusts block-ack policy depending on combo mode. BSS changes trigger join/reset/finalize, beacon wake/filter changes, ARP filters, template uploads, beacon enable, keepalive, ERP/slot/RSSI/TX power/PS updates. AP start uploads beacon/probe templates, starts firmware BSS, and configures MFP from RSN IE. Station add maps TDLS/AP peers to firmware link IDs when needed. Reset locks/flushed TX, sends HIF reset, resets policies, restores BA policy, clears join state, cancels beacon loss, and updates PM on all vifs.

State and persistence: Maintains `wdev->vif[]`, per-vif `id`, `channel`, `link_id_map`, `after_dtim_tx_allowed`, `join_in_progress`, PM completion, beacon loss/TIM/scan/ROC work, U-APSD mask, queues, and TX policies. Firmware-persistent state includes MAC address, BSS/join/start state, beacon/probe templates, filters, PM mode, BA policy, MFP, ARP filters, and link map.

Dependencies: Depends on mac80211/cfg80211 APIs, HIF request and MIB helpers, queue/TX flush, scan locks, key handling, debug/common state, and API-version helpers.

Risks and test signals: Risks include lock ordering with `conf_mutex`/`scan_lock`/TX lock, reset during scan/join, link ID exhaustion/leaks, combo-mode BA disablement, PM timeout waits, beacon filter hiding needed beacons, TIM update with malformed beacon, MFP RSN IE parsing bounds, WoWLAN limited validation, and thermal suspend freezing TX. Tests should cover STA join/assoc/disassoc, IBSS, AP start/stop/templates/TIM, add/remove station including TDLS, two-vif combo mode, PS/U-APSD changes, RSSI CQM, beacon loss/regain, ARP filter limits, channel context assign/unassign, suspend/resume wakeup, and interface removal with clean queues.

Test signals: Source read size: 841 lines, 23585 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/sta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/sta.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/sta.h

Purpose: Declares WFx mac80211 callback functions, station-private data, and firmware event helper APIs.

Important APIs and types: `struct wfx_sta_priv` stores firmware link ID and vif ID for each mac80211 station. Prototypes cover lifecycle/config/filter/interface/AP/IBSS/TX queue/BSS/station/TIM/AMPDU/channel-context/PM callbacks, plus hardware-event helpers for cooling, hot-device suspend, multicast suspend/resume, RSSI report, PM update, and reset.

Control flow and integration: `main.c` wires most functions into `ieee80211_ops`; `hif_rx.c` calls event helpers for RSSI, BSS lost, PM completion, and suspend/resume indications; data TX uses station private link IDs.

State and persistence: Per-station private state persists while mac80211 station objects live and maps firmware link IDs back to vifs.

Dependencies: Depends on mac80211 types and WFx device/vif private structures.

Risks and test signals: Build tests should catch mac80211 signature changes. Runtime tests should validate station private initialization/removal, link ID reuse, and helper calls for firmware indications.

Test signals: Source read size: 73 lines, 3343 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/sta.h -->
