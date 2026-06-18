# Research: subset-b-004980

Grouped source research for NFC drivers under `sources/distributed-fs/ceph-client/drivers/nfc`. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/fw_dnld.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/fw_dnld.c

Purpose: Implements the Marvell NCI firmware downloader, including bootrom reset handling, logical connection setup, helper upload, firmware upload, and final boot command sequencing.

Important APIs and functions: Public entry points are `nfcmrvl_fw_dnld_init()`, `nfcmrvl_fw_dnld_deinit()`, `nfcmrvl_fw_dnld_start()`, `nfcmrvl_fw_dnld_abort()`, and `nfcmrvl_fw_dnld_recv_frame()`. Internal state handlers include `process_state_reset()`, `process_state_init()`, `process_state_set_ref_clock()`, `process_state_set_hi_config()`, `process_state_open_lc()`, `process_state_fw_dnld()`, `process_state_close_lc()`, and `process_state_boot()`.

Control flow: `nfcmrvl_fw_dnld_start()` requests the firmware image, validates the Marvell magic and PHY id, chooses helper or firmware config, programs bootrom transport settings, arms a timeout, resets the chip, and waits for CORE_RESET notification. Receive frames are queued to a single-thread workqueue. The worker matches exact NCI response patterns, configures reference clock and host-interface parameters, opens the proprietary firmware-download logical connection, exchanges helper commands, ACK/NACKs, data chunks, and credits, closes the logical connection, and sends the proprietary boot command. If a helper was loaded, the state machine returns to reset for the real firmware image.

State and persistence: State lives in `priv->fw_dnld`: firmware pointer, parsed header/config, state/substate, current file offset, chunk length, RX queue/workqueue, and timeout timer. It also manipulates `ndev->cmd_cnt` and `ndev->cmd_timer` to coexist with NCI command serialization. There is no durable persistence; the firmware file is released at completion or failure.

Dependencies and integration points: Depends on Linux firmware loading, NCI command/frame helpers, `nfcmrvl_private`, bus `nci_update_config()` callbacks, reset/halt helpers, raw NFC socket tracing, and `nfc_fw_download_done()`.

Risks: Response matching is byte-exact and brittle to bootrom revisions. Chunk length/complement validation protects protocol integrity, but firmware offsets are trusted after header validation. Timer/workqueue cleanup must race safely with unregister. Failure halts the chip, which affects later recovery. Test signals include valid helper+firmware paths, firmware-without-helper, bad magic/PHY, malformed NCI responses, bad length complement NACK, credit sequencing, timeout, abort during unregister, and per-PHY config updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/fw_dnld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/fw_dnld.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/fw_dnld.h

Purpose: Defines the firmware-image ABI and runtime state used by the Marvell firmware downloader.

Important APIs and types: Constants include `NFCMRVL_FW_MAGIC`, proprietary boot command ids, logical connection ids, helper packet formats, and retry flags. Packed structs describe per-PHY boot settings: `nfcmrvl_fw_uart_config`, `nfcmrvl_fw_i2c_config`, `nfcmrvl_fw_spi_config`, `nfcmrvl_fw_binary_config`, and the top-level `nfcmrvl_fw` header. `struct nfcmrvl_fw_dnld` stores the active firmware download session. Function prototypes expose init/deinit/start/abort and frame receive hooks to `main.c`.

Control flow: The header has no executable flow, but it fixes the data contract consumed by `fw_dnld.c`: a firmware blob starts with `struct nfcmrvl_fw`, then offsets select bootrom, helper, and firmware payload/config regions.

State and persistence: Runtime state includes firmware name, `struct firmware` ownership, parsed header/config pointers, state/substate, offset/chunk tracking, a single-thread RX workqueue, SKB queue, and timer. The packed firmware header is a persistent on-disk ABI.

Dependencies and integration points: Includes workqueue types and forward-declares `struct nfcmrvl_private`; it is included by `nfcmrvl.h`, so most Marvell transport files see the downloader state.

Risks: Packed layout and endianness must match firmware-generation tooling. `union` members expose typed config views over raw bytes, so bad offsets or wrong PHY ids produce unsafe transport settings. Test signals are compile coverage of all PHY builds plus firmware-download tests for UART/I2C/SPI binary configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/fw_dnld.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/i2c.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/i2c.c

Purpose: Implements the Marvell NCI-over-I2C transport, wiring I2C probe/remove, IRQ-driven reads, writes, device-tree parsing, and common Marvell NCI registration.

Important APIs and functions: `struct nfcmrvl_i2c_drv_data` stores the I2C client, device, and common private pointer. Key helpers are `nfcmrvl_i2c_read()`, `nfcmrvl_i2c_int_irq_thread_fn()`, `nfcmrvl_i2c_nci_send()`, `nfcmrvl_i2c_parse_dt()`, `nfcmrvl_i2c_probe()`, and `nfcmrvl_i2c_remove()`. `i2c_ops` implements `nfcmrvl_if_ops`.

Control flow: Probe verifies `I2C_FUNC_I2C`, allocates transport state, finds platform data or OF properties, requests the IRQ, registers the common NCI device as `NFCMRVL_PHY_I2C`, and enables firmware download support. The threaded IRQ reads an NCI control header followed by payload, then passes the SKB to `nfcmrvl_nci_recv_frame()`. Send writes the entire SKB with a standby retry on `-EREMOTEIO`.

State and persistence: Tracks `NFCMRVL_PHY_ERROR` in common flags after fatal remote I/O and stores IRQ polarity/number in platform data. No durable persistence exists.

Dependencies and integration points: Uses Linux I2C, OF IRQ parsing, NCI header sizing, common Marvell registration, and the firmware downloader through `support_fw_dnld`.

Risks: Header `plen` is trusted for allocation and second read. Partial sends become `-EREMOTEIO`; fatal receive errors block future traffic until open/reset clears the common PHY error flag. Test signals include DT/platform probe, rising/falling IRQ selection, standby retry, bad payload length, fatal I2C error, firmware download over I2C, and remove while interrupts are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/main.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/main.c

Purpose: Provides the common Marvell NFC NCI driver core shared by USB, UART, I2C, and SPI transports.

Important APIs and functions: Exports `nfcmrvl_nci_register_dev()`, `nfcmrvl_nci_unregister_dev()`, `nfcmrvl_nci_recv_frame()`, `nfcmrvl_chip_reset()`, `nfcmrvl_chip_halt()`, and `nfcmrvl_parse_dt()`. Internal NCI ops are `nfcmrvl_nci_open()`, `nfcmrvl_nci_close()`, `nfcmrvl_nci_send()`, `nfcmrvl_nci_setup()`, and `nfcmrvl_nci_fw_download()`.

Control flow: Transport drivers call register with PHY id, driver data, low-level ops, device, and platform data. The core allocates an `nci_dev` with PHY-specific headroom/tailroom, initializes firmware download support, registers with the NCI core, and halts the chip. Open sets the running bit, clears prior PHY errors, and delegates to transport open. Send optionally wraps NCI packets in an HCI mux header, then delegates to transport send. Receive strips HCI mux packets, routes frames to firmware download while a download is active, or delivers to `nci_recv_frame()` only when running.

State and persistence: `struct nfcmrvl_private` owns flags, platform config, `nci_dev`, firmware download context, PHY identity, transport context, and ops. No persistent state beyond runtime device registration.

Dependencies and integration points: Integrates with Linux GPIO descriptors, DT parsing, NCI core, NFC firmware download API, and transport-specific `nfcmrvl_if_ops`.

Risks: HCI mux framing assumptions must match hardware; non-NFC mux packets are silently discarded. Register/unregister must abort firmware download before destroying workqueue state. Reset GPIO polarity is assumed by the binding. Test signals include open/close idempotence, muxed and unmuxed RX/TX, firmware-download routing, setup config command, reset/halt GPIO behavior, and all transport probe/remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/nfcmrvl.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/nfcmrvl.h

Purpose: Central header for the Marvell NFC NCI driver, defining common state, platform data, transport operations, constants, and exported core functions.

Important APIs and types: Defines flags `NFCMRVL_NCI_RUNNING` and `NFCMRVL_PHY_ERROR`; coexistence/configuration ids; HCI mux constants; `enum nfcmrvl_phy`; `struct nfcmrvl_platform_data`; `struct nfcmrvl_private`; and `struct nfcmrvl_if_ops`. It declares common registration, receive, reset/halt, and DT parsing functions.

Control flow: The header establishes the transport/core split. Bus drivers fill `nfcmrvl_if_ops` and call `nfcmrvl_nci_register_dev()`. The common core later calls the same ops for open, close, send, and firmware-download transport reconfiguration.

State and persistence: `nfcmrvl_private` is the per-device runtime anchor. It persists only for the device lifetime and contains platform configuration, NCI parent, firmware download context, and PHY-private data.

Dependencies and integration points: Includes `fw_dnld.h`, depends on NFC/NCI types through users, and is consumed by all Marvell bus modules.

Risks: The header couples all transports to the firmware downloader layout. Missing or wrong `nci_update_config()` behavior can break post-firmware bus speeds. Flag bit meanings must remain synchronized with transport error handling. Test signals include building USB/UART/I2C/SPI modules and exercising common function prototypes from each transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/nfcmrvl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/spi.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/spi.c

Purpose: Implements the Marvell NCI-over-SPI transport using the kernel NCI SPI helper and an interrupt-driven slave handshake.

Important APIs and functions: `struct nfcmrvl_spi_drv_data` stores SPI device, `nci_spi`, completion, flags, and common private pointer. Key functions are `nfcmrvl_spi_int_irq_thread_fn()`, `nfcmrvl_spi_nci_send()`, `nfcmrvl_spi_nci_update_config()`, `nfcmrvl_spi_parse_dt()`, `nfcmrvl_spi_probe()`, and `nfcmrvl_spi_remove()`.

Control flow: Probe parses platform data or DT IRQ, requests a falling-edge threaded IRQ, registers the common Marvell NCI device as SPI, enables firmware download, allocates the `nci_spi` helper, and initializes handshake completion. Send sets `SPI_WAIT_HANDSHAKE`, appends a dummy byte required by the controller DMA behavior, and calls `nci_spi_send()` with the completion. The IRQ either completes the send handshake or reads an SPI packet and forwards it to the common receiver.

State and persistence: Runtime state includes `SPI_WAIT_HANDSHAKE`, `handshake_completion`, transport speed in `nci_spi->xfer_speed_hz`, and common private flags. No durable persistence exists.

Dependencies and integration points: Depends on Linux SPI, OF IRQ parsing, `net/nfc/nci_spi.h` helpers via included NCI headers, common Marvell core, and firmware config values from `nfcmrvl_fw_spi_config`.

Risks: IRQ semantics are overloaded between handshake completion and RX notification. The dummy byte affects frame tailroom and must match controller expectations. `nci_spi` allocation result is not checked before later use. Test signals include handshake IRQ ordering, RX IRQ path, firmware speed update, DT IRQ parsing, dummy-byte framing, and probe/remove fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/uart.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/uart.c

Purpose: Implements Marvell NFC over the kernel NCI UART framework, including DT/module-parameter configuration, firmware-download speed updates, and optional BREAK-based wake/sleep control.

Important APIs and functions: Transport callbacks are `nfcmrvl_uart_nci_send()` and `nfcmrvl_uart_nci_update_config()`. NCI UART callbacks are `nfcmrvl_nci_uart_open()`, `nfcmrvl_nci_uart_close()`, `nfcmrvl_nci_uart_recv()`, `nfcmrvl_nci_uart_tx_start()`, and `nfcmrvl_nci_uart_tx_done()`. Module params are `hci_muxed`, `flow_control`, and `break_control`.

Control flow: UART open searches a child DT node compatible with Marvell NFC UART, falls back to module parameters, registers the common NCI device, and binds `nu->drv_data`/`nu->ndev`. Sends delegate to the selected NCI UART low-level send operation. Firmware-download config changes call `nci_uart_set_config()` with the firmware-provided baud rate and flow-control setting. TX start clears BREAK to wake the controller; TX done asserts BREAK for deep-sleep wake support, except during firmware download.

State and persistence: Per-device state is common `nfcmrvl_private`; global module parameters provide fallback runtime configuration. BREAK state is physical line state, not durable persistence.

Dependencies and integration points: Depends on NCI UART registration, TTY `break_ctl`, DT child-node parsing, GPIO descriptor lookup for reset, and common Marvell core.

Risks: DT is discovered through the serial device parent, so platform layout matters. BREAK control assumes TTY ops support it. Firmware-download baud updates must occur at the correct boot stage. Test signals include DT and module-param configuration, HCI mux mode, firmware baud switch, BREAK wake/sleep, receive routing, and close during firmware download.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/usb.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/usb.c

Purpose: Implements Marvell NFC over USB bulk endpoints with runtime PM, continuous bulk RX URBs, transmit URB anchoring, and suspend/resume deferral.

Important APIs and functions: `struct nfcmrvl_usb_drv_data` owns USB device/interface, anchors, endpoints, suspend counters, TX count, and common private pointer. Important functions include `nfcmrvl_submit_bulk_urb()`, `nfcmrvl_bulk_complete()`, `nfcmrvl_usb_nci_open()`, `nfcmrvl_usb_nci_close()`, `nfcmrvl_usb_nci_send()`, `nfcmrvl_suspend()`, `nfcmrvl_resume()`, `nfcmrvl_probe()`, and `nfcmrvl_disconnect()`.

Control flow: Probe finds bulk endpoints, initializes anchors/work/spinlock, registers the common NCI device as USB, and disables firmware download support. Open enables runtime PM remote wake, submits bulk RX URBs, and marks bulk running. RX completion wraps received bytes in an NCI SKB, forwards to common receive, and resubmits while running. Send fills a bulk URB over the TX endpoint; if suspending, it anchors the URB in `deferred` and schedules a wake. Resume resubmits RX URBs and plays deferred TX URBs.

State and persistence: Runtime state includes USB anchors (`tx_anchor`, `bulk_anchor`, `deferred`), flags `NFCMRVL_USB_BULK_RUNNING` and `NFCMRVL_USB_SUSPENDING`, `tx_in_flight`, `suspend_count`, and remote wake setting. No durable persistence.

Dependencies and integration points: Uses Linux USB core, runtime PM/autosuspend, common Marvell NCI core, and USB device id matching for vendor-specific interface class/subclass/protocol.

Risks: Completion checks `NFCMRVL_NCI_RUNNING` against USB flags instead of common private flags, a likely bug that can suppress RX handling. Deferred URB ownership across suspend/resume is delicate. Firmware download is intentionally unsupported on USB. Test signals include open/close, RX resubmit loop, TX during autosuspend, resume deferred TX, disconnect with anchored URBs, PM busy return with TX in flight, and soft-unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcsim.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/nfcsim.c

Purpose: Provides a software NFC digital simulator made of two virtual NFC devices connected by paired in-memory links.

Important APIs and functions: Main types are `struct nfcsim` and `struct nfcsim_link`. Link helpers allocate/free links, store SKBs, wake receivers, cancel receives, shut down, and wait for matching frames. Digital ops are `nfcsim_in_configure_hw()`, `nfcsim_in_send_cmd()`, `nfcsim_tg_configure_hw()`, `nfcsim_tg_send_cmd()`, `nfcsim_tg_listen()`, `nfcsim_abort_cmd()`, and `nfcsim_switch_rf()`.

Control flow: Module init creates two links, initializes debugfs, and registers two `nfc_digital_dev` instances with opposite link directions. Sending schedules receive work for the local command and, unless `dropframe` is set, stores the outgoing SKB on the peer link and wakes it after a random 3-10 ms delay. Receive work waits for a frame with matching RF technology and opposite mode, then invokes the digital completion callback. Target listen is modeled as a send with no SKB.

State and persistence: Each device tracks up/down state, initiator/target mode, RF tech, receive timeout, completion callback/context, and debugfs `dropframe`. Each link stores one pending SKB, mode/tech metadata, waitqueue condition, and shutdown flag. Debugfs state is runtime-only.

Dependencies and integration points: Integrates with NFC digital core, debugfs, workqueues, waitqueues, random delay generation, and module init/exit.

Risks: Each link stores only one SKB, so concurrent sends overwrite old pending frames. The wait condition is a simple byte reset after receive, so cancellation and timeout ordering matter. Test signals include two-device DEP exchange, initiator/target mode mismatch, timeout, abort, RF off during receive, debugfs frame drop, module unload during pending work, and shutdown error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nfcsim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/Kconfig

Purpose: Declares build configuration for the generic NXP NCI core driver and its I2C transport.

Important entries: `NFC_NXP_NCI` is a tristate depending on `NFC_NCI` and builds the generic NCI core for NXP chips such as PN547, PN548, and PN7150 families. `NFC_NXP_NCI_I2C` is a tristate depending on `NFC_NXP_NCI && I2C` and builds the I2C transport module.

Control flow: This file contributes no runtime flow; it controls which modules and dependencies Kbuild exposes.

State and persistence: Kconfig selections persist only in kernel build configuration. No runtime state.

Dependencies and integration points: Integrates with the kernel NFC NCI stack and I2C subsystem. The help text warns that this kernel NCI driver is not for NXP libnfc userspace stacks.

Risks: The I2C option depends on the core instead of selecting it, so users must enable both or rely on menu dependency visibility. Test signals include `m`, `y`, and disabled builds for both symbols, dependency pruning when `NFC_NCI` or `I2C` is unavailable, and module name verification for `nxp_nci` and `nxp_nci_i2c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/Makefile

Purpose: Defines Kbuild object composition for the NXP NCI core and I2C transport modules.

Important definitions: `nxp-nci-objs = core.o firmware.o` combines generic registration and firmware download support into `nxp-nci`. `nxp-nci_i2c-objs = i2c.o` builds the I2C transport. `obj-$(CONFIG_NFC_NXP_NCI)` and `obj-$(CONFIG_NFC_NXP_NCI_I2C)` attach those modules to their Kconfig symbols.

Control flow: No runtime flow; Kbuild links objects according to selected config.

State and persistence: Build artifacts are generated by Kbuild; no source-level persistent state.

Dependencies and integration points: Must stay aligned with `Kconfig` names and C exports/imports: `i2c.c` calls exported `nxp_nci_probe()`/`nxp_nci_remove()` and firmware helpers live in the core object.

Risks: Renaming objects or symbols without updating this file breaks module builds. Test signals are allmodconfig/module builds and link checks for `nxp_nci_fw_download`, `nxp_nci_probe`, and `nxp_nci_i2c_driver`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/core.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/core.c

Purpose: Implements the generic NXP NCI core driver that registers an NCI device over a transport-provided PHY interface.

Important APIs and functions: Exports `nxp_nci_probe()` and `nxp_nci_remove()`. NCI ops are `nxp_nci_open()`, `nxp_nci_close()`, `nxp_nci_send()`, and firmware download through `nxp_nci_fw_download()`. Proprietary NCI notification handlers log RF PLL unlock and TXLDO errors via `nxp_nci_core_ops`.

Control flow: Probe allocates `nxp_nci_info`, stores PHY id/ops/max payload, initializes firmware work/completion and mutex, forces cold mode through `set_mode()`, allocates/registers an NCI device, and returns it to the PHY driver. Open transitions cold to NCI mode under `info_lock`; close returns to cold. Send validates mode and `write` callback, delegates SKB ownership to the PHY write path, and consumes or frees SKBs appropriately. Remove completes any active firmware worker, cancels work, returns hardware to cold, unregisters, and frees the NCI device.

State and persistence: `nxp_nci_info` stores current mode, max payload, PHY ops, mutex, NCI device pointer, and firmware worker state. No durable persistence exists.

Dependencies and integration points: Integrates with NCI core allocation/registration, Linux NFC firmware download API, transport `nxp_nci_phy_ops`, and firmware code in `firmware.c`.

Risks: `nxp_nci_open()` sets mode to NCI even if `set_mode()` fails after being called, preserving the returned error but leaving state optimistic. Send mode checks prevent firmware and cold writes through normal NCI path. Test signals include mode transitions, send without write op, send while cold/FW, proprietary RF notifications, firmware download dispatch, remove during FW mode, and probe unwind after NCI register failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/firmware.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/firmware.c

Purpose: Implements NXP NCI firmware download framing, CRC, command-response handling, asynchronous work progression, and firmware completion.

Important APIs and functions: Public functions are `nxp_nci_fw_download()`, `nxp_nci_fw_work()`, `nxp_nci_fw_recv_frame()`, and `nxp_nci_fw_work_complete()`. Helpers include `nxp_nci_fw_crc()`, `nxp_nci_fw_send_chunk()`, `nxp_nci_fw_send()`, `nxp_nci_fw_read_status()`, and `nxp_nci_fw_check_crc()`.

Control flow: Download validates transport support and firmware name, requests the firmware, switches the PHY to firmware mode, initializes pointers/counters, and schedules work. The worker sends one firmware frame at a time, splitting it into payload-size chunks with a big-endian length header, chunk flag, and custom CRC. Non-reset commands wait up to 30 seconds for `cmd_completion`, which is completed by IRQ-side `nxp_nci_fw_recv_frame()`. On response, CRC and status are decoded, then the worker advances to the next chunk/frame or completes the download.

State and persistence: `nxp_nci_fw_info` stores firmware name/pointer, remaining size, current data pointer, frame size, written bytes, work item, completion, and command result. Firmware contents are transient and released at completion.

Dependencies and integration points: Uses request_firmware, NCI SKB allocation, unaligned big-endian helpers, PHY `set_mode()`/`write()`, and `nfc_fw_download_done()`.

Risks: Firmware frame sizes are trusted after checking against remaining firmware size. Completion can be interrupted or time out. Status mapping is device-specific and some statuses become non-obvious Linux errors. Test signals include reset frame behavior, multi-chunk frames, CRC mismatch, status error mapping, timeout, interrupted wait, write failure, remove during download, and max-payload boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/i2c.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/i2c.c

Purpose: Implements the I2C physical layer for the NXP NCI core driver, including GPIO mode switching, IRQ-driven NCI/FW reads, and I2C writes.

Important APIs and functions: `struct nxp_nci_i2c_phy` stores I2C client, NCI device, enable/firmware GPIOs, and hard fault. PHY ops are `nxp_nci_i2c_set_mode()` and `nxp_nci_i2c_write()`. Read paths are `nxp_nci_i2c_nci_read()` and `nxp_nci_i2c_fw_read()`. Probe/remove are `nxp_nci_i2c_probe()` and `nxp_nci_i2c_remove()`.

Control flow: Probe verifies I2C functionality, maps ACPI GPIO names, gets enable and optional firmware GPIOs, calls `nxp_nci_probe()` with max payload 32, and requests a threaded IRQ. Mode switching drives firmware and enable GPIOs and clears hard fault when returning cold. IRQ handling locks the common `info_lock`, selects NCI or firmware read format based on current mode, marks fatal `-EREMOTEIO` as hard fault, and dispatches to `nci_recv_frame()` or `nxp_nci_fw_recv_frame()`.

State and persistence: Runtime state includes GPIO output values, `hard_fault`, and the common mode in `nxp_nci_info`. No durable persistence.

Dependencies and integration points: Integrates with Linux I2C, GPIO consumer API, ACPI/OF matching, NCI core, and NXP firmware download callbacks.

Risks: IRQ reads use header-provided lengths; malformed payload lengths become protocol errors. A hard fault blocks writes until cold mode reset. Remove calls `nxp_nci_remove()` before `free_irq()`, so IRQ serialization relies on normal teardown ordering. Test signals include GPIO mode transitions, optional firmware GPIO absence, NCI read with zero/nonzero payload, FW read framing, hard fault propagation, I2C standby retry, and ACPI/OF/id-table probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/nxp-nci.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/nxp-nci.h

Purpose: Shared private header for the NXP NCI core, firmware downloader, and transport drivers.

Important APIs and types: Defines firmware framing constants `NXP_NCI_FW_HDR_LEN`, `NXP_NCI_FW_CRC_LEN`, and `NXP_NCI_FW_FRAME_LEN_MASK`; `enum nxp_nci_mode`; `struct nxp_nci_phy_ops`; `struct nxp_nci_fw_info`; and `struct nxp_nci_info`. Declares firmware and probe/remove functions used across `core.c`, `firmware.c`, and `i2c.c`.

Control flow: No executable flow. The mode enum controls transport behavior: cold, normal NCI, and firmware download. The PHY ops provide the only hardware-specific hooks used by core and firmware code.

State and persistence: `nxp_nci_info` is the per-device runtime anchor, and `nxp_nci_fw_info` holds active firmware-download progress. No durable state is defined here.

Dependencies and integration points: Includes completion, firmware, NFC, and NCI core headers. It is local to the NXP NCI driver folder.

Risks: Max payload, frame mask, and CRC length assumptions must match transport/device firmware mode. Mode transitions depend on all users holding `info_lock` consistently. Test signals include compile coverage across core/firmware/I2C, firmware state progression, and mode-dependent IRQ read dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/nxp-nci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn533/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nfc/pn533/Kconfig

Purpose: Declares build configuration for the PN533/PN532 NFC core and USB, I2C, and UART transports.

Important entries: `NFC_PN533` is the hidden core tristate. `NFC_PN533_USB` depends on USB and selects the core. `NFC_PN533_I2C` depends on I2C and selects the core. `NFC_PN532_UART` depends on `SERIAL_DEV_BUS` and selects the core.

Control flow: No runtime flow; configuration determines which modules are built and which transport frontends expose menus.

State and persistence: Build configuration only.

Dependencies and integration points: Integrates with USB, I2C, serdev, and the common NFC device stack. The UART option is named PN532 because it targets PN532-style UART transport while sharing PN533 core.

Risks: The core has no prompt, so it is enabled only by selected transports. Missing NFC core dependency may be inherited from parent menu; build tests should catch invalid standalone selections. Test signals include module and built-in builds for each transport, dependency hiding without USB/I2C/SERIAL_DEV_BUS, and module names `pn533_usb`, `pn533_i2c`, and `pn532_uart`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn533/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn533/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nfc/pn533/Makefile

Purpose: Defines Kbuild object composition for PN533 core and transport modules.

Important definitions: `pn533_usb-objs = usb.o`, `pn533_i2c-objs = i2c.o`, and `pn532_uart-objs = uart.o` map transport modules. `obj-$(CONFIG_NFC_PN533)` builds `pn533.o`; transport objects are controlled by their matching Kconfig symbols.

Control flow: No runtime flow; Kbuild links source files into modules.

State and persistence: Build artifacts only.

Dependencies and integration points: Must stay aligned with exports from `pn533.c` and imports from transport files such as `pn53x_common_init()`, `pn533_finalize_setup()`, and `pn533_recv_frame()`.

Risks: Object/module name drift breaks module loading or Kconfig help text. Test signals include allmodconfig builds and link checks for each transport against the core symbol exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn533/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn533/i2c.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/pn533/i2c.c

Purpose: Implements the PN532/PN533 I2C transport frontend for the shared PN533 core.

Important APIs and functions: `struct pn533_i2c_phy` stores I2C client, common `pn533` pointer, abort flag, and hard fault. PHY ops are `pn533_i2c_send_frame()`, `pn533_i2c_send_ack()`, and `pn533_i2c_abort_cmd()`. IRQ/read/probe functions are `pn533_i2c_read()`, `pn533_i2c_irq_thread_fn()`, `pn533_i2c_probe()`, and `pn533_i2c_remove()`.

Control flow: Probe checks I2C support, allocates PHY state, initializes common PN533 as a PN532 request/ACK/response device, allocates an NFC device with no Type B protocols, requests a shared falling IRQ, finalizes setup by querying/configuring the chip, and registers NFC. Send writes the fully framed SKB with a standby retry. IRQ reads a maximum-size frame prefixed by a READY byte, trims to the parsed PN533 frame size, and passes it to `pn533_recv_frame()` unless the command was locally aborted. Abort sends a PN533 ACK and completes the current command with `-ENOENT`.

State and persistence: Runtime state includes `aborted`, `hard_fault`, and the common PN533 command queues/work. No durable persistence.

Dependencies and integration points: Uses Linux I2C/IRQ, OF match aliases for `nxp,pn532`, and shared PN533 frame parsing/command completion.

Risks: The read path pulls a fixed maximum frame and relies on READY plus frame-size parsing. Fatal I2C errors set hard fault permanently. Aborted frames are dropped to avoid completing cancelled commands. Test signals include READY bit absent, standby retry, abort while command pending, hard fault, IRQ sharing, setup failure unwind, and device-tree compatible coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn533/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn533/pn533.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/pn533/pn533.c

Purpose: Implements the shared PN533/PN532 NFC core: frame construction/validation, command queueing, polling, activation, DEP links, initiator and target data exchange, setup, and NFC device registration.

Important APIs and functions: Exports `pn53x_common_init()`, `pn533_finalize_setup()`, `pn53x_common_clean()`, `pn533_recv_frame()`, `pn532_i2c_nfc_alloc()`, `pn53x_register_nfc()`, `pn53x_unregister_nfc()`, `pn533_rx_frame_is_ack()`, and `pn533_rx_frame_is_cmd_response()`. Major internal subsystems include standard frame ops, async command queue workers, target parsers for Type A/F/Jewel/B, polling workers, DEP link helpers, MI fragmentation handlers, and setup helpers.

Control flow: Transports allocate a `struct pn533` with PHY and frame ops. Commands are framed, sent immediately or queued under `cmd_lock`, completed by `pn533_recv_frame()`, and finalized in an ordered workqueue. Polling builds a modulation list or PN532 autopoll request, alternates reader/listen modes, handles NFC-DEP active polling, reports targets, and stops on valid discovery. Activation, DEP link-up, transceive, and target-mode send/receive issue PN533 commands and use response queues plus fragment queues for multi-information chaining.

State and persistence: `struct pn533` owns NFC device pointer, command queue/current command, workqueue/work items, polling/listen state, target protocol state, general bytes, response and fragment SKB queues, PHY ops, and frame ops. No durable persistence exists.

Dependencies and integration points: Integrates with Linux NFC core ops, target-mode APIs, DEP APIs, random bytes, SKBs, transport-specific PHY callbacks, and PN533/PN532/PaSoRi/ACR122 variants.

Risks: Command serialization and direct async commands can race if completion/work ordering is wrong. Frame length/checksum parsing is security-sensitive. Fragment queues must be purged on errors. Poll/listen timers and aborts can complete commands with `-ENOENT`. Test signals include firmware-version/setup, standard/extended frame validation, queued commands, polling all modulations, autopoll, DEP active/passive links, large transceive fragmentation, target mode activation/data, abort/stop poll, PaSoRi Felica path, and cleanup with queued commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn533/pn533.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn533/pn533.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/pn533/pn533.h

Purpose: Shared private interface for PN533 core and transport drivers, defining device variants, frame ABI, runtime state, callbacks, and exported core functions.

Important APIs and types: Defines device types `PN533_DEVICE_*`, supported protocol masks, standard/extended frame constants, PN533 command codes, return/MI bits, poll modulation ids, packed frame structs, `struct pn533`, `struct pn533_cmd`, `struct pn533_frame_ops`, and `struct pn533_phy_ops`. It declares common init/setup/cleanup, receive, NFC registration, and frame helper exports.

Control flow: No executable flow, but it defines the call contract: transports provide `pn533_phy_ops`; the core provides framed command orchestration and NFC ops; optional frame ops allow ACR122 CCID/APDU framing instead of native PN533 frames.

State and persistence: `struct pn533` is the full runtime state for a chip instance, including workers, queues, polling target state, and PHY integration. No durable state.

Dependencies and integration points: Includes NFC core types and is consumed by USB/I2C/UART transports plus `pn533.c`.

Risks: Header exposes a large mutable core struct to transports, increasing coupling. Frame header/tail lengths must match transport allocations. Command response checks depend on current `dev->cmd`. Test signals include compile coverage of all transports, ACR122 alternate frame ops, and NFC allocation headroom/tailroom correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn533/pn533.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn533/uart.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/pn533/uart.c

Purpose: Implements the PN532 UART/serdev transport for the shared PN533 core.

Important APIs and functions: `struct pn532_uart_phy` stores serdev, receive SKB, common PN533 pointer, wakeup state, command timeout timer, and current TX buffer. PHY ops are `pn532_uart_send_frame()`, `pn532_uart_send_ack()`, `pn532_uart_abort_cmd()`, `pn532_dev_up()`, and `pn532_dev_down()`. Receive parsing is handled by `pn532_uart_rx_is_frame()` and `pn532_receive_buf()`.

Control flow: Probe allocates PHY state and RX buffer, opens serdev, sets 115200 baud/no flow control, initializes common PN533 as a PN532 autopoll request/ACK/response device, finalizes setup, closes serdev for idle power, and registers NFC. `dev_up` opens serdev and sends a final wakeup; `dev_down` closes it and marks future sends to wake. Send may prepend a wakeup sequence, writes the framed SKB, and arms a short timeout that resends the current buffer. Receive accumulates bytes until it finds a PN533 frame or ACK/error frame, then passes the SKB to `pn533_recv_frame()`.

State and persistence: Runtime state includes `recv_skb`, `send_wakeup`, `cmd_timeout`, and `cur_out_buf`. No durable persistence.

Dependencies and integration points: Uses serdev bus, OF compatible `nxp,pn532`, common PN533 core, and NFC registration.

Risks: The resend timer reuses `cur_out_buf`, so lifetime depends on PN533 command completion not freeing it before timeout handling. Frame scanning tolerates garbage but can discard accumulated data when tailroom fills. Wakeup state intentionally has no mutex. Test signals include wakeup sequence, timeout resend, malformed leading bytes, ACK/error/extended frame detection, serdev open/close, remove with active timer, and autopoll behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn533/uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn533/usb.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/pn533/usb.c

Purpose: Implements PN533 USB transport, including native PN533 devices, Sony PaSoRi, and ACS ACR122U CCID-wrapped devices.

Important APIs and functions: `struct pn533_usb_phy` stores USB device/interface, IN/OUT/ACK URBs, ACK buffer, and common PN533 pointer. Native flow uses `pn533_usb_send_frame()`, `pn533_recv_ack()`, `pn533_recv_response()`, `pn533_usb_send_ack()`, and `pn533_usb_abort_cmd()`. ACR122 support defines CCID/APDU frame structs and `pn533_acr122_frame_ops`, plus `pn533_acr122_poweron_rdr()`.

Control flow: Probe allocates URBs/buffer, finds bulk endpoints, initializes URBs, selects protocols/frame ops based on USB id, powers on ACR122 readers when needed, initializes common PN533, finalizes setup, and registers NFC. Sending submits the OUT URB synchronously via completion, then submits IN URB for ACK or direct response based on protocol type. ACK completion validates ACK before requesting the response. Response completion wraps actual bytes in an SKB and calls `pn533_recv_frame()`.

State and persistence: Runtime state is URB ownership, ACK buffer, common PN533 command state, and device variant. No durable persistence.

Dependencies and integration points: Uses Linux USB core, PN533 common core, NFC registration, and alternate frame ops for ACR122 CCID escape framing.

Risks: ACR122 cannot safely abort commands, so stop-poll semantics differ. URB context is temporarily swapped for synchronous OUT/power-on completions. IN buffer sizing assumes max standard/extended frame length. Test signals include each USB id variant, native ACK/response path, req/resp-only ACR122 path, invalid ACK, URB cancellation/disconnect, ACR122 power-on, alternate frame validation, and setup failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn533/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn544/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nfc/pn544/Kconfig

Purpose: Declares build configuration for the PN544 HCI core and its I2C and MEI transports.

Important entries: `NFC_PN544` is the hidden core tristate and selects `CRC_CCITT`. `NFC_PN544_I2C` depends on `NFC_HCI && I2C && NFC_SHDLC` and selects the core. `NFC_PN544_MEI` depends on `NFC_HCI && NFC_MEI_PHY` and selects the core.

Control flow: No runtime flow; it gates module build and dependency availability.

State and persistence: Build configuration only.

Dependencies and integration points: Ties PN544 to the NFC HCI stack, SHDLC LLC for I2C, MEI NFC PHY for Intel MEI transport, and CRC-CCITT for I2C framing/firmware checks.

Risks: The hidden core is selected only by transports. I2C depends on SHDLC because its LLC framing uses that layer; MEI uses LLC NOP from its transport. Test signals include dependency-disabled builds, module builds for `pn544_i2c` and `pn544_mei`, and CRC dependency presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn544/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn544/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nfc/pn544/Makefile

Purpose: Defines Kbuild object composition for PN544 HCI core and transport modules.

Important definitions: `pn544_i2c-objs = i2c.o`, `pn544_mei-objs = mei.o`, `obj-$(CONFIG_NFC_PN544) += pn544.o`, and transport object selections follow `CONFIG_NFC_PN544_I2C` and `CONFIG_NFC_PN544_MEI`.

Control flow: No runtime flow; Kbuild controls object linking.

State and persistence: Build outputs only.

Dependencies and integration points: Must remain aligned with `Kconfig` and exports from `pn544.c`, especially `pn544_hci_probe()` and `pn544_hci_remove()` used by I2C and MEI modules.

Risks: Symbol/object naming drift breaks module linking. Test signals include allmodconfig builds and separate module link checks for I2C and MEI transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn544/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn544/i2c.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/pn544/i2c.c

Purpose: Implements the PN544 HCI-over-I2C transport, SHDLC-style length/CRC framing, GPIO power/mode control, IRQ RX dispatch, and I2C firmware download for C2/C3 hardware variants.

Important APIs and functions: `struct pn544_i2c_phy` stores I2C client, HCI device, enable/firmware GPIOs, polarity, hardware variant, firmware worker state, firmware pointers/counters, powered/run mode, and hard fault. PHY ops are `pn544_hci_i2c_write()`, `pn544_hci_i2c_enable()`, and `pn544_hci_i2c_disable()`. Firmware helpers include `pn544_hci_i2c_fw_download()`, `pn544_hci_i2c_fw_work()`, `pn544_hci_i2c_fw_write_cmd()`, `pn544_hci_i2c_fw_check_cmd()`, and secure-write helpers.

Control flow: Probe maps ACPI GPIOs, gets enable/firmware GPIOs, detects enable polarity by trying reset commands, requests a rising IRQ, and calls `pn544_hci_probe()` with SHDLC LLC and firmware-download callback. HCI writes push a length byte and CRC, retry standby `-EREMOTEIO`, then restore the SKB. IRQ dispatch reads firmware status in FW mode or validates length/CRC and sends HCI frames to `nfc_hci_recv_frame()` in HCI mode. Firmware download schedules a worker that enters FW mode, requests firmware, writes/checks legacy C2 blobs or secure C3 frames/chunks, and completes through `nfc_fw_download_done()`.

State and persistence: Runtime state includes GPIO power/run mode, hard fault, firmware progress fields, work state, and HCI device pointer. Firmware file contents are transient.

Dependencies and integration points: Uses I2C, GPIO, ACPI/OF matching, CRC-CCITT, NFC HCI/LLC SHDLC, firmware API, and PN544 core probe/remove.

Risks: CRC/length recovery flushes the bus based on assumptions about one frame per interrupt. Polarity auto-detect can fail and falls back active high. Firmware worker mixes IRQ-completed statuses and scheduled work; remove must complete in-progress downloads. Test signals include polarity detection, HCI CRC error flush, standby retry, hard fault, FW C2 write/check sequence, FW C3 secure chunking/reset, IRQ mode switch, and remove during download.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn544/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn544/mei.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/pn544/mei.c

Purpose: Provides the PN544 transport shim for Intel Management Engine Interface NFC devices.

Important APIs and functions: `pn544_mei_probe()` allocates an `nfc_mei_phy`, then calls `pn544_hci_probe()` with `mei_phy_ops`, LLC NOP, MEI NFC header size, and MEI max payload. `pn544_mei_remove()` removes the HCI device and frees the MEI PHY. `pn544_mei_tbl` matches the PN544 MEI client UUID and version.

Control flow: MEI bus probe creates the generic MEI NFC PHY and registers the PN544 HCI core. Remove reverses that order.

State and persistence: State is stored in the allocated `nfc_mei_phy`, including `hdev`. No durable persistence.

Dependencies and integration points: Depends on the MEI client bus, `../mei_phy.h`, NFC HCI, NFC LLC, and PN544 core exports. Firmware download callback is NULL, so firmware download is unsupported over this transport.

Risks: Probe failure must free the MEI PHY after PN544 registration failure. The transport relies on MEI PHY for enable/disable/write semantics and framing headroom. Test signals include MEI id matching, probe/remove, failure after `nfc_mei_phy_alloc()`, HCI open/close over MEI, and firmware download returning unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn544/mei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn544/pn544.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/pn544/pn544.c

Purpose: Implements the PN544 HCI NFC core, including HCI device registration, hardware setup, polling, DEP, custom transceive paths, target-mode events, firmware-download delegation, and secure element management.

Important APIs and functions: Exports `pn544_hci_probe()` and `pn544_hci_remove()`. HCI ops include `pn544_hci_open()`, `pn544_hci_close()`, `pn544_hci_ready()`, `pn544_hci_xmit()`, `pn544_hci_start_poll()`, DEP link up/down, target discovery completion, `pn544_hci_im_transceive()`, `pn544_hci_tm_send()`, presence check, event handling, firmware download, SE discovery, and SE enable/disable.

Control flow: Probe allocates `pn544_hci_info`, defines static HCI gates, allocates/registers an NFC HCI device with supplied LLC/PHY parameters, and stores client data. Open enables the PHY from cold to ready; close disables it. Ready writes a long table of proprietary system-management registers, configures whitelist/notifications, disables auto activation, resets reader operations, and reads full software version. Start poll configures polling-loop phases, general bytes, NFC-DEP initiator/target gates, and reader-requested events. Event handlers translate PN544 activation/deactivation/data events into NFC HCI/core target-mode notifications.

State and persistence: `pn544_hci_info` stores PHY ops/id, HCI device, state, lock, async callback state, and optional firmware callback. HCI session id is fixed as `ID544HCI`; no other durable driver state.

Dependencies and integration points: Uses NFC HCI core, HCI LLC, NFC target/DEP/SE APIs, transport PHY ops from I2C/MEI, and optional transport firmware download.

Risks: Register programming is magic-value heavy and hardware-revision sensitive. Fixed session id may collide for multiple identical chips. Custom MIFARE auth byte reordering and Felica response stripping are protocol-specific. SE enable writes proprietary registers. Test signals include HCI ready programming, polling protocol combinations, DEP initiator/target, MIFARE/Felica/Jewel/NFCIP transceive, target events, presence checks, firmware unsupported/supported paths, SE discover/enable/disable, and multi-device session behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn544/pn544.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn544/pn544.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/pn544/pn544.h

Purpose: Shared public-private header for PN544 transport modules and the PN544 HCI core.

Important APIs and types: Defines `DRIVER_DESC`, run modes `PN544_HCI_MODE` and `PN544_FW_MODE`, firmware download callback type `fw_download_t`, and core lifecycle functions `pn544_hci_probe()` and `pn544_hci_remove()`.

Control flow: The header defines the transport-to-core contract. I2C and MEI transports call `pn544_hci_probe()` with PHY ops, LLC name, headroom/tailroom/payload limits, optional firmware download callback, and output HCI device pointer. They call `pn544_hci_remove()` at teardown.

State and persistence: Header owns no runtime state. Its constants influence transport mode switching and firmware download selection.

Dependencies and integration points: Includes NFC HCI types. I2C passes SHDLC LLC plus firmware callback; MEI passes LLC NOP and no firmware callback.

Risks: `fw_download_t` includes `hw_variant`, tying firmware transport behavior to HCI software-version decoding. Headroom/tailroom arguments must match transport framing. Test signals include compile coverage of I2C/MEI transports, firmware callback invocation on I2C, and unsupported firmware download on MEI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/pn544/pn544.h -->
