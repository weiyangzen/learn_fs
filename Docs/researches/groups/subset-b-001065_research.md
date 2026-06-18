# subset-b-001065 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_sdio.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_sdio.c

## Purpose
Implements the Marvell Bluetooth-over-SDIO transport driver. It binds supported Marvell SDIO Bluetooth functions, downloads helper/firmware images, moves HCI/vendor packets between the Bluetooth core and SDIO CMD53 ports, handles card interrupts, supports suspend/resume host-sleep behavior, parses optional wakeup device-tree data, and exposes firmware coredumps for chips that support them.

## Important APIs, Types, And Functions
- `btmrvl_sdio_probe`/`btmrvl_sdio_remove` own SDIO device lifetime and connect this transport to the common `btmrvl` core through `btmrvl_add_card`, `btmrvl_register_hdev`, and callback pointers.
- `btmrvl_sdio_register_dev` enables the SDIO function, claims the SDIO IRQ, sets block size, discovers the I/O port, and configures read-to-clear interrupt behavior for newer chips.
- `btmrvl_sdio_download_helper`, `btmrvl_sdio_download_fw_w_helper`, and `btmrvl_sdio_download_fw` implement firmware boot, including helper transfer, firmware transfer, CRC retry signaling, and multi-function "winner" coordination through firmware status registers.
- `btmrvl_sdio_card_to_host`, `btmrvl_sdio_host_to_card`, `btmrvl_sdio_interrupt`, and `btmrvl_sdio_process_int_status` implement receive, transmit, interrupt capture, and deferred interrupt processing.
- `btmrvl_sdio_suspend`/`btmrvl_sdio_resume` integrate host sleep, MMC keep-power, HCI suspend/resume, and optional wake IRQ handling.
- `btmrvl_sdio_coredump` and `btmrvl_sdio_rdwr_firmware` implement firmware memory dump handshakes via SDIO debug registers and `dev_coredumpv`.

## Control Flow
Module init registers `bt_mrvl_sdio`; probe allocates `btmrvl_sdio_card`, copies device-specific firmware/register metadata from the SDIO ID table, enables and configures the SDIO function, disables interrupts during firmware boot, downloads firmware if the ready signature is absent, enables interrupts, parses wake IRQ data, and registers the HCI device through common Marvell code. TX from the Bluetooth core is routed through `hw_host_to_card`, which aligns/pads the packet and writes to `card->ioport`; RX starts in the SDIO IRQ handler, which snapshots and clears host interrupt status, ORs it into global `sdio_ireg`, then schedules common interrupt handling. The deferred path claims the SDIO host, marks TX ready on download-complete interrupts, and reads one SDIO packet on upload interrupts. Firmware download polls card-ready bits, sends helper chunks with a 4-byte SDIO length header, sends firmware blocks sized by the helper-provided length, and waits for `FIRMWARE_READY`.

## State And Persistence
Per-device state is in `struct btmrvl_sdio_card`: SDIO function, I/O port, firmware names, register map, firmware-download block size, RX unit shift, wake IRQ config, and common `btmrvl_private`. Static `user_rmmod` distinguishes module unload from card removal, and static `sdio_ireg` accumulates interrupt status across IRQ and worker contexts under `priv->driver_lock`. Firmware and helper blobs are transient `request_firmware` resources. Suspend state persists in the common adapter flags `is_suspending`, `is_suspended`, and `hs_state`. Firmware dump memory is staged in `mem_type_mapping_tbl` buffers until handed to devcoredump.

## Dependencies And Integration Points
Depends on Linux SDIO/MMC APIs, firmware loading, device tree IRQ parsing, wakeup PM APIs, Bluetooth HCI core, `devcoredump`, and the Marvell common driver in `btmrvl_drv.h`. It integrates with SDIO IDs for SD8688/8787/8797/8887/8897/8977/8987/8997 devices, HCI statistics, module firmware declarations, MMC keep-power suspend, and common Marvell event filtering via `btmrvl_check_evtpkt` and `btmrvl_process_event`.

## Risks And Edge Cases
The interrupt accumulator is global, so assumptions about one active card matter. Firmware download has several hardware-sensitive timeout paths: zero helper lengths, CRC retry bits, CMD53 write failures, and another SDIO function downloading firmware first. Packet length validation must reject malformed SDIO headers before allocating or passing frames upward. Suspend must undo wake IRQ enablement correctly when the wake IRQ fired and disabled itself. Coredump sizing and register loops trust device-provided memory counts/sizes and need defensive allocation/error handling.

## Test Signals
Useful signals include successful probe with firmware already ready and with full helper/firmware download, TX retry after transient CMD53 failures, RX of HCI event/ACL/SCO/vendor packets with valid and invalid SDIO lengths, read-to-clear and write-to-clear interrupt chips, module unload sending shutdown while surprise removal does not, suspend with and without host-sleep activation, wake IRQ resume behavior, and devcoredump output on supported 8897/89xx hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_sdio.h -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_sdio.h

## Purpose
Defines the Marvell SDIO transport contract used by `btmrvl_sdio.c`: packet framing constants, firmware-transfer limits, register bit masks, card register maps, per-card runtime state, device table metadata, and DMA alignment helpers.

## Important APIs, Types, And Functions
- `SDIO_HEADER_LEN`, `SDIO_BLOCK_SIZE`, `ALLOC_BUF_SIZE`, `MAX_POLL_TRIES`, and `MAX_WRITE_IOMEM_RETRY` define transport sizing, polling, and retry policy.
- Register bits such as `HOST_POWER_UP`, `HOST_CMD53_FIN`, `HIM_ENABLE`, `UP_LD_HOST_INT_STATUS`, `DN_LD_HOST_INT_STATUS`, `DN_LD_CARD_RDY`, `CARD_IO_READY`, and `FIRMWARE_READY` encode the SDIO/firmware handshake.
- `struct btmrvl_sdio_card_reg` describes chip-specific register offsets and interrupt/coredump capabilities.
- `struct btmrvl_sdio_card` stores live per-function state: SDIO function, I/O port, firmware names, register map, feature flags, RX unit, common Marvell private pointer, and wakeup config.
- `struct btmrvl_sdio_device` is the immutable SDIO ID table payload copied into a card at probe.
- `ALIGN_SZ` and `ALIGN_ADDR` support 8-byte DMA-safe SDIO buffers.

## Control Flow
This header has no executable flow, but it drives the flow in the C file. Probe selects a `btmrvl_sdio_device`, which points at a `btmrvl_sdio_card_reg`. Register offsets are then used for function enablement, firmware status checks, firmware block transfer, interrupt masking/clearing, data port I/O, and optional firmware dump reads. Buffer constants determine allocation size and block rounding for RX, TX, and firmware download.

## State And Persistence
The header separates immutable hardware descriptions from mutable runtime state. Register maps and device descriptors are static const data; `btmrvl_sdio_card` persists for the SDIO function lifetime and references common driver state through `priv`. Wake configuration persists only when device tree parsing supplies an IRQ.

## Dependencies And Integration Points
Requires Bluetooth HCI size definitions and kernel bit/alignment helpers through the including C file. It is tightly coupled to `btmrvl_sdio.c` and common Marvell structures from `btmrvl_drv.h`; no public cross-driver API is exposed.

## Risks And Edge Cases
Incorrect register offsets or feature flags can corrupt firmware download, interrupt clearing, or coredump behavior for a whole chip family. `ALLOC_BUF_SIZE` must remain large enough for maximum HCI frames plus SDIO headers and block rounding. Alignment helpers operate on integer-cast addresses, so callers must allocate enough slack before aligning.

## Test Signals
Build coverage should catch structure/member drift against `btmrvl_sdio.c`. Runtime signals are indirect: correct I/O port discovery, RX unit reads, interrupt clearing mode selection, firmware ready polling, and coredump register ranges across every SDIO device-table entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_sdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmtk.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btmtk.c

## Purpose
Provides shared MediaTek Bluetooth support used by USB and other transports: firmware filename selection, WMT firmware download helpers, BD address setting, reset queuing, devcoredump registration/processing, USB WMT command synchronization, USB subsystem reset, diagnostic ACL handling, ISO-over-interrupt support, and USB setup/shutdown flows.

## Important APIs, Types, And Functions
- `btmtk_fw_get_filename`, `btmtk_setup_firmware`, and `btmtk_setup_firmware_79xx` select and download MediaTek patch firmware formats.
- `btmtk_set_bdaddr`, `btmtk_reset_sync`, `btmtk_register_coredump`, and `btmtk_process_coredump` are exported helper APIs for transport drivers.
- USB-only helpers under `CONFIG_BT_HCIBTUSB_MTK` include `btmtk_usb_hci_wmt_sync`, `btmtk_usb_subsys_reset`, `btmtk_usb_recv_acl`, `alloc_mtk_intr_urb`, `btmtk_usb_setup`, `btmtk_usb_suspend`, `btmtk_usb_resume`, and `btmtk_usb_shutdown`.
- Internal firmware structs `btmtk_patch_header`, `btmtk_global_desc`, and `btmtk_section_map` parse MT79xx ROM patch section maps.

## Control Flow
Generic firmware setup requests a firmware blob, optionally powers on data RAM, slices firmware into 250-byte WMT patch-download commands, and resets/enables the function. MT79xx setup parses a header/global descriptor/section maps, skips non-Bluetooth MT6639 sections, sends section metadata, then streams each selected section with first/middle/last flags. USB setup reads chip IDs and firmware version/flavor registers, resolves the firmware name, registers coredump support, downloads firmware, enables the Bluetooth protocol over WMT, enables Microsoft/AOSP capabilities for newer chips, optionally initializes the ISO interrupt interface, and logs setup duration. USB WMT sync sends opcode `0xfc6f`, polls a vendor control endpoint for the WMT event, waits on `BTMTK_TX_WAIT_VND_EVT`, validates the returned op, and maps event flags/status words into shared WMT status constants.

## State And Persistence
Shared persistent state lives in `struct btmtk_data` attached to the HCI device: driver name, flags, device ID, reset callback, coredump info, USB device/interface pointers, control URB anchor, WMT event clone, ISO endpoint/interface state, ISO RX reassembly skb, and ISO spinlock. Coredump state records firmware version, packet count, and devcoredump state until completion/timeout triggers a reset. Firmware blobs are transient and released after download.

## Dependencies And Integration Points
Depends on Bluetooth HCI sync command APIs, firmware loading, USB control/interrupt URBs, runtime PM, unaligned helpers, devcoredump, and exported declarations in `btmtk.h`. It integrates with `btusb` for MediaTek USB devices, with in-kernel devcoredump, with HCI diagnostic receive for firmware dump/log ACL handles, and with HCI capability setters such as `hci_set_msft_opcode` and `hci_set_aosp_capable`.

## Risks And Edge Cases
WMT synchronization is sensitive to event cloning and flag clearing; missed wakeups or stale `evt_skb` can stall initialization. Firmware section parsing trusts little-endian offsets/sizes and must not stream non-Bluetooth MT6639 sections. USB control URB resubmission loops can fail during disconnect/suspend and must free setup packets correctly. `alloc_mtk_intr_urb` leaks the allocated URB on the `btmtk_isopkt_pad` error path because it returns without freeing it. ISO RX reassembly must guard tailroom against malformed ISO lengths.

## Test Signals
Test with supported device IDs including MT7663, MT7922, MT7925, MT7961, MT7902, and MT6639 zero-CHIPID VID/PID fallback; firmware present/missing; WMT timeout/wrong-op responses; coredump ACL stream ending with the terminator; USB subsystem reset polling; ISO interrupt endpoint setup, suspend/resume URB restart, and malformed ISO packet lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmtk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmtk.h -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btmtk.h

## Purpose
Defines shared MediaTek Bluetooth constants, WMT packet layouts, firmware names, register addresses, coredump/USB state structures, and exported helper prototypes used by MediaTek USB, SDIO, and UART transports.

## Important APIs, Types, And Functions
- Firmware macros name legacy and MT79xx patch files, including MT7622, MT7663, MT7668, MT7922, MT7902, MT7961, MT7925, and MT7927/MT6639 paths.
- WMT constants and packet structs (`btmtk_wmt_hdr`, `btmtk_hci_wmt_cmd`, `btmtk_hci_wmt_evt`, `btmtk_hci_wmt_evt_funcc`, `btmtk_hci_wmt_evt_reg`, `btmtk_hci_wmt_params`) define the vendor command protocol shared by transports.
- Register and reset macros define MT7921/CONNV3 reset, pinmux, download-status, UDMA, and USB endpoint reset addresses.
- `struct btmtk_data` is the USB-side private state used by `btmtk.c`.
- Exported APIs include firmware setup, filename generation, BD address setting, reset synchronization, coredump registration/processing, USB setup/suspend/resume/shutdown, subsystem reset, ACL diagnostic receive, and ISO interrupt URB allocation.

## Control Flow
The header supplies compile-time dispatch through `#if IS_ENABLED(CONFIG_BT_MTK)`: real prototypes are visible when MediaTek support is enabled, while inline stubs return `-EOPNOTSUPP` or no-op otherwise. Transport drivers construct `btmtk_hci_wmt_params` and pass a transport-specific `wmt_cmd_sync_func_t` to the shared firmware helpers.

## State And Persistence
Most state definitions are protocol-level and immutable. Persistent runtime state is represented by `struct btmtk_data`, including flags, device ID, reset callback, coredump metadata, USB handles, WMT event skb, ISO endpoints, anchor, partial ISO skb, and ISO RX spinlock. The coredump struct persists the active state and packet count across received dump fragments.

## Dependencies And Integration Points
Depends on Bluetooth HCI types, USB types for USB-only helpers, firmware naming consumed by module firmware declarations, and MediaTek transport drivers that share the WMT ABI. The stub section lets non-MediaTek builds compile callers without linking `btmtk.c`.

## Risks And Edge Cases
Protocol struct packing and endian annotations must match firmware exactly. Flag enum values are bit positions used with `set_bit`, not masks. Firmware filename macros are part of userspace firmware ABI. Stubs returning `-EOPNOTSUPP` must be acceptable to callers when the feature is compiled out.

## Test Signals
Build with `CONFIG_BT_MTK=y/m` and disabled to exercise both prototypes and stubs. Runtime test signals are correct WMT header lengths, status interpretation for function control and patch download, coredump metadata population, USB ISO state initialization, and firmware file lookup using the defined names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmtk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmtksdio.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btmtksdio.c

## Purpose
Implements the MediaTek Bluetooth-over-SDIO HCI transport. It binds MT7663/MT7668/MT7921/MT7902 SDIO functions, manages SDIO ownership and runtime PM, downloads firmware through shared WMT helpers, frames HCI packets with a MediaTek SDIO header, processes interrupt-driven TX/RX, supports wakeup and reset behavior, and configures SCO offload for MT7921-class devices.

## Important APIs, Types, And Functions
- `struct btmtksdio_data` describes per-chip firmware, chip ID, low-power mailbox support, and runtime PM support; `struct btmtksdio_dev` stores live HCI/SDIO state.
- `mtk_hci_wmt_sync` is the SDIO implementation of the shared MediaTek WMT sync callback.
- `btmtksdio_open`/`close` enable the SDIO function, claim IRQs, configure interrupt registers, and transfer ownership between driver and firmware.
- `btmtksdio_txrx_work`, `btmtksdio_interrupt`, `btmtksdio_tx_packet`, and `btmtksdio_rx_packet` implement interrupt-bottom-half TX/RX.
- `mt76xx_setup`, `mt79xx_setup`, and `btmtksdio_setup` drive firmware download, function enablement, runtime PM, SCO, reset pin setup, and HCI quirks.
- PM callbacks `btmtksdio_runtime_suspend`/`resume` and system suspend/resume transfer ownership and mark BT wake state.

## Control Flow
Probe allocates `btmtksdio_dev`, initializes work/queues, allocates an HCI device, wires HCI callbacks, registers the device, normalizes runtime PM state, initializes wakeup, and optionally obtains a reset GPIO. Open enables the SDIO function, claims driver ownership, disables/masks interrupts, claims the SDIO IRQ, sets block size, configures synchronous interrupts and write-one-clear status, enables RX/TX interrupt sources, and enables interrupts. IRQ disables further interrupts and schedules `txrx_work`; the worker gets runtime PM, claims the SDIO host, acknowledges current interrupt status, services mailbox/ownership/TX-ready/RX-done bits, sends one queued skb when hardware is ready, reads complete SDIO packets, then re-enables interrupts. Setup sets TX-ready, performs chip-specific firmware flow, configures SCO/pinmux/reset for MT7921/MT7902, and enables autosuspend policy.

## State And Persistence
Persistent state includes `tx_state` bits for WMT waits, TX readiness, function enabled, patch enabled, reset active, and BT wake; the skb TX queue; an event clone for WMT waiters; optional reset GPIO; chip metadata; and runtime PM state on `bdev->dev`. Firmware-loaded state is represented by `BTMTKSDIO_PATCH_ENABLED` and by controller state after WMT function enablement. No host-side firmware image is retained after setup.

## Dependencies And Integration Points
Depends on SDIO/MMC APIs, PM runtime, GPIO/device tree, HCI core, shared MediaTek helpers in `btmtk.h`, H4 packet metadata, and Bluetooth codec offload hooks. Integrates with SDIO device IDs, system wakeup, HCI non-persistent setup, Microsoft/AOSP vendor capabilities, and eSCO codec offload callbacks.

## Risks And Edge Cases
`btmtksdio_txrx_work` uses `time_is_before_jiffies(txrx_timeout)` in its loop condition, which appears inverted for a "run until timeout" pattern and may affect drain behavior. WMT event parsing assumes `bdev->evt_skb` is present and large enough after the wait. Runtime PM and ownership transitions must not be called recursively while the SDIO host is already claimed; some paths call ownership helpers after claiming the host. Reset handling must restore firmware ownership when reset occurs while the function is closed. Packet padding removal depends on accurate H4 header metadata and SDIO length fields.

## Test Signals
Exercise probe/open/setup/close/remove for each SDIO ID, MT76xx and MT79xx firmware paths, WMT timeouts/wrong events, TX FIFO overflow, RX packet length/type/padding errors, runtime suspend/resume ownership polling, system wakeup interrupt behavior, reset GPIO path on MT7921, SCO codec offload config for CVSD/mSBC, and autosuspend enabled/disabled module parameter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmtksdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmtkuart.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btmtkuart.c

## Purpose
Implements MediaTek Bluetooth over serdev UART. It supports built-in SoC and standalone UART chips, handles STP-wrapped H:4 framing, performs WMT firmware setup via shared MediaTek helpers, manages baudrate changes for standalone devices, controls regulators/clocks/GPIO boot sequencing, and registers an HCI UART device.

## Important APIs, Types, And Functions
- `struct btmtkuart_data` distinguishes standalone hardware and firmware name; `struct btmtkuart_dev` holds serdev, power resources, pinctrl states, TX/RX queues, STP parser state, and embedded `hci_uart`.
- `mtk_hci_wmt_sync` sends WMT commands over HCI opcode `0xfc6f` and waits for cloned WMT events.
- `mtk_stp_split`, `btmtkuart_recv`, and `btmtkuart_recv_event` parse STP packets into H4 frames and wake WMT waiters.
- `btmtkuart_send_frame`, `btmtkuart_tx_work`, and `btmtkuart_tx_wakeup` wrap outgoing HCI frames with H4 type plus STP header/trailer and drain the serdev TX queue.
- `btmtkuart_parse_dt`, `btmtkuart_probe`, `btmtkuart_open`, `btmtkuart_setup`, and `btmtkuart_remove` manage resources, HCI lifecycle, firmware, and hardware bring-up.

## Control Flow
Probe reads compatible data, installs serdev callbacks, parses device-tree resources, initializes work/queues, allocates an HCI device, and for standalone chips enables oscillator/regulator, asserts boot/reset sequencing, switches pinctrl to runtime, and marks wakeup required. Open opens serdev, selects initial baudrate/flow control for standalone devices, resets STP parser state, enables runtime PM, and prepares the reference clock. RX bytes enter `btmtkuart_receive_buf`, which calls `btmtkuart_recv`; STP splitting accumulates six bytes of STP metadata, validates prefix/length, feeds H4 payload slices into `h4_recv_buf`, and handles fragmented H4 over multiple STP packets. Setup optionally sends WMT wakeup, changes baudrate, queries/downloads firmware, enables the Bluetooth function, and applies low-power settings. TX prepends H4 type, adds STP header/trailer, queues the skb, and work writes partial buffers until drained.

## State And Persistence
Persistent per-device state includes desired/current baudrates, regulator/clock/GPIO/pinctrl handles, TX state bits, TX queue, partial RX skb, cloned WMT event skb, STP cursor/remaining length, and firmware metadata. Runtime PM is enabled for open lifetime and disabled on close. Standalone hardware remains powered from probe until remove.

## Dependencies And Integration Points
Depends on serdev, runtime PM, clocks, regulators, GPIO, pinctrl, device tree match data, HCI core, H4 receive helpers, and shared MediaTek firmware/WMT helpers. Integrates with `hci_register_dev`, HCI non-persistent setup, BD address helper `btmtk_set_bdaddr`, and module OF compatibles for MT7622, MT7663U, and MT7668U.

## Risks And Edge Cases
STP resynchronization is heuristic: malformed prefix or length resets cursor to 2 and may discard/realign bytes incorrectly. `btmtkuart_setup` ignores the return value from `btmtkuart_change_baudrate`, so firmware setup may continue after a failed standalone speed switch. WMT event parsing assumes a cloned skb exists and contains the expected event. Partial serdev writes must preserve packet type/statistics and requeue correctly. Power sequencing differs sharply between standalone and built-in devices, making device-tree resource validation important.

## Test Signals
Test built-in MT7622 and standalone MT7663/MT7668 flows, regulator/clock/reset/boot GPIO sequencing, STP fragmentation and malformed STP headers, WMT command timeout and wrong-op response, baudrate switch and dummy byte activation, firmware already downloaded and fresh download paths, TX partial write requeueing, flush cleanup, and remove-time power disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmtkuart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btnxpuart.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btnxpuart.c

## Purpose
Implements NXP Bluetooth over serdev UART. It handles H:4 traffic plus NXP bootloader packet types, firmware download for V1 and V3 bootloaders, helper firmware for selected chips, baudrate/timeout bootloader commands, power-save and wakeup control, independent reset, firmware dump collection, BD address programming, and HCI device registration for NXP UART Bluetooth controllers.

## Important APIs, Types, And Functions
- `struct btnxpuart_dev` is the main runtime object: serdev/HCI handles, TX/RX queues, firmware offsets, wait queues, baudrates, bootloader parameter state, power-save state, firmware metadata, reset control, and embedded `hci_uart`.
- Power-save functions `ps_setup`, `ps_init`, `ps_control`, `send_ps_cmd`, `send_wakeup_method_cmd`, `ps_start_timer`, and `ps_cleanup` manage sleep/wake methods, GPIO/RTS/DTR/break signaling, timers, and vendor commands.
- Firmware functions `nxp_download_firmware`, `nxp_request_firmware`, `nxp_recv_fw_req_v1`, `nxp_recv_fw_req_v3`, `nxp_recv_chip_ver_v1`, `nxp_recv_chip_ver_v3`, `nxp_fw_change_baudrate`, and `nxp_fw_change_timeout` implement bootloader negotiation and streaming.
- HCI callbacks `nxp_setup`, `nxp_post_init`, `nxp_enqueue`, `btnxpuart_open`/`close`/`flush`, `nxp_shutdown`, `nxp_reset`, `nxp_hw_err`, and `nxp_set_bdaddr` expose the transport to the Bluetooth core.
- Coredump functions `nxp_coredump`, `nxp_process_fw_dump`, and `nxp_coredump_notify` integrate NXP dump ACL frames with devcoredump and uevents.

## Control Flow
Probe allocates the device, reads match data and baudrate properties, initializes CRC8, enables regulator/reset, allocates/registers an HCI UART device, starts in firmware-downloading state, sets local BD address quirk if present, initializes power-save resources, and registers devcoredump. Setup checks for a boot signature at primary baud; if present, firmware download waits on bootloader request packets received through `h4_recv_buf`. V1 bootloaders request lengths with complement checks and may require helper firmware before the main image; V3 bootloaders send chip/version and offset/error/CRC requests, receive ACK/NAK/CRC responses, and account for injected timeout/baudrate command bytes through `fw_v3_offset_correction`. After firmware is ready, setup emits a uevent, restores firmware-init baudrate, and initializes power-save defaults; post-init changes operational baudrate and sends wakeup/power-save commands. Normal TX queues H4-framed packets, wakes from power save if needed, and writes via serdev work. RX routes standard HCI frames upward and bootloader pseudo-packets to firmware handlers.

## State And Persistence
Firmware download state persists in offsets, expected lengths, previous sent length, currently requested firmware name/blob, helper-downloaded flag, baudrate/timeout state machines, `BTNXPUART_FW_DOWNLOADING`, `BTNXPUART_CHECK_BOOT_SIGNATURE`, and wait queues. Power-save state persists in `ps_data`: target/current mode, sleep state, wake methods/GPIOs, intervals, IRQ, work, timer, and mutex. Coredump/independent-reset state uses tx_state bits. The controller firmware persists baudrate and power-save settings until reset or driver removal, so remove attempts to restore the initial baudrate.

## Dependencies And Integration Points
Depends on serdev, firmware loading, CRC8/CRC32, GPIO, regulators, reset controls, OF IRQs, HCI core, H4 reassembly, devcoredump, and kobject uevents. Integrates with NXP firmware files under `nxp/`, OF compatibles for 88W8987 and 88W8997, host wakeup IRQs, `local-bd-address`, and Bluetooth HCI command sync queues.

## Risks And Edge Cases
Firmware state machines are fragile: out-of-sync V1 lengths, V3 offset correction under CRC retries, helper-to-main handoff, and bootloader baudrate changes can wedge download until power cycle. `btnxpuart_write_wakeup` only calls `serdev_device_write_wakeup` rather than scheduling the driver's TX worker, so TX progress relies on serdev core behavior. Power-save work/timer interactions must avoid sleeping while TX is active and avoid recursive driver-sent vendor command interception. Firmware dump handling assumes ACL handle `0x0fff` and sufficient packet length for dump headers. Probe error after `hci_register_dev` and `ps_setup` needs careful cleanup of registered devices/resources.

## Test Signals
Exercise V1 and V3 firmware download, helper firmware handoff, missing firmware and old-name fallback, CRC/timeout NAK handling, baudrate switch to 3M/4M, boot signature absent/already-running path, power-save DTR/break/GPIO modes, host wake IRQ suspend/resume, user-originated vendor commands being intercepted and reissued, independent reset after hardware error or command timeout, firmware dump start/complete/timeout uevents, and restore-baudrate behavior on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btnxpuart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btqca.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btqca.c

## Purpose
Provides shared Qualcomm/Atheros Bluetooth setup helpers, primarily for UART and SMD transports. It reads controller version/build metadata, chooses and downloads rampatch and NVM files, edits NVM TLVs for baudrate/sleep/BD address, handles SoC-specific firmware naming and fallbacks, disables logging where needed, performs HCI reset, and exposes BD address and pre-shutdown vendor commands.

## Important APIs, Types, And Functions
- `qca_read_soc_version`, `qca_uart_setup`, `qca_set_bdaddr_rome`, `qca_set_bdaddr`, and `qca_send_pre_shutdown_cmd` are exported transport-facing APIs.
- `qca_tlv_check_data`, `qca_tlv_send_segment`, `qca_download_firmware`, and `qca_inject_cmd_complete_event` validate, mutate, segment, download, and complete patch/NVM transfers.
- `qca_read_fw_build_info`, `qca_read_fw_board_id`, `qca_get_nvm_name_by_board`, `qca_send_patch_config_cmd`, `qca_disable_soc_logging`, and `qca_check_bdaddr` implement SoC-specific setup details.
- `qca_filename_has_extension` and `qca_get_alt_nvm_file` implement board-specific NVM fallback to `.bin`.

## Control Flow
UART setup computes a combined SoC version and ROM-derived firmware suffix, optionally sends WCN6750 patch config, selects a rampatch filename from SoC type or caller override, downloads it, waits briefly, optionally reads board ID, selects an NVM filename from caller override, board ID, ROM version, SoC variant, or legacy fallback, downloads it, disables logging on newer chips, sets Microsoft vendor opcode for WCN399x/WCN6750-class chips, sends HCI reset, reads firmware build info for selected chips, and checks whether a default NVM BD address should trigger the BDADDR property quirk. Firmware download requests the file, copies it into mutable vmalloc memory, validates TLV/ELF metadata, updates NVM tags, sends 243-byte max EDL segments, and injects a command-complete event when the controller skips ordinary completion events.

## State And Persistence
`struct qca_fw_config` is the main transient setup state: firmware type/name, user baudrate, download event-skip mode, and BD address extracted from NVM. Controller state persists after setup through downloaded firmware/NVM, disabled logging, HCI reset, and vendor opcode settings on `hdev`. Firmware blobs are copied to mutable memory only for the duration of TLV patching and download.

## Dependencies And Integration Points
Depends on HCI sync command APIs, firmware loading, vmalloc, Bluetooth address helpers, and definitions in `btqca.h`. It integrates with QCA UART transports, Qualcomm SMD BD address setting through Rome NVM access, Linux firmware naming conventions under `qca/`, HCI quirks for BD address properties, and Microsoft vendor extension opcode setup.

## Risks And Edge Cases
Event format differs by SoC generation: WCN3991+ often returns command-complete payloads where older chips use vendor events. Download mode can skip intermediate completions, requiring the injected command-complete path to avoid HCI command timeout noise. TLV parsing mutates NVM data in place and must bounds-check nested/enclosed TLV sets. Firmware naming has many SoC/board/manufacturer variants; wrong board ID fallback can silently load a generic NVM. `qca_tlv_send_segment` logs TLV response `result` but does not currently convert a nonzero result into `err`, so a controller-side segment error may not fail setup.

## Test Signals
Test version-read paths for pre-WCN3991 and WCN3991+ chips, rampatch/NVM naming for every `qca_btsoc_type`, WCN6750 mbn-to-tlv fallback, WCN6855 legacy filename fallback, board-specific NVM and `.bin` fallback, malformed TLV lengths/tags, skipped-event firmware download with injected command complete, logging-disable failures, HCI reset failures, build-info parsing, and BDADDR quirk detection when public address matches NVM address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btqca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btqca.h -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btqca.h

## Purpose
Defines Qualcomm/Atheros Bluetooth EDL command constants, TLV structures, firmware configuration types, SoC type enumeration, baudrate values, and exported helper prototypes or stubs for QCA setup code.

## Important APIs, Types, And Functions
- EDL opcode and subcommand macros describe patch, NVM, BD address, build-info, board-ID, pre-shutdown, and logging-disable commands.
- Event and tag constants identify EDL responses and NVM tags for BD address, HCI transport, and deep sleep.
- `enum qca_baudrate`, `enum qca_tlv_dnld_mode`, `enum qca_tlv_type`, and `enum qca_btsoc_type` classify UART speed encodings, firmware download acknowledgment modes, firmware file formats, and supported SoC families.
- `struct qca_fw_config`, `edl_event_hdr`, `qca_btsoc_version`, `tlv_seg_resp`, `tlv_type_patch`, `tlv_type_nvm`, and `tlv_type_hdr` are parsed/filled by `btqca.c`.
- Prototypes expose setup, version read, BD address, and pre-shutdown helpers when `CONFIG_BT_QCA` is enabled; inline stubs return `-EOPNOTSUPP` otherwise.

## Control Flow
The header has no runtime flow but determines how `btqca.c` builds HCI vendor commands and parses controller responses. Callers use the exported prototypes for QCA setup; the compiler selects real functions or stubs based on `CONFIG_BT_QCA`.

## State And Persistence
Most definitions are immutable protocol ABI. `qca_fw_config` carries transient setup state across rampatch/NVM validation and download. `qca_btsoc_version` persists only long enough for callers to select firmware and log version information.

## Dependencies And Integration Points
Depends on Bluetooth HCI device and address types through includers. It is included by QCA transports such as UART and SMD and by the shared implementation in `btqca.c`. Firmware file naming and SoC enum values are part of transport setup contracts.

## Risks And Edge Cases
Packed TLV and event structs must match firmware byte layouts. `get_soc_ver` combines little-endian fields and is central to firmware suffix selection. Stub behavior must be handled by callers in builds without QCA support. Adding SoC types requires synchronized changes to firmware naming in `btqca.c`.

## Test Signals
Build with QCA enabled/disabled, validate struct sizes against known firmware blobs, exercise SoC enum additions through `qca_uart_setup`, and verify NVM tag IDs and baudrate enum values produce expected controller-side behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btqca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btqcomsmd.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btqcomsmd.c

## Purpose
Implements a Qualcomm WCNSS SMD/RPMSG Bluetooth HCI transport. It opens separate command/event and ACL channels to the remote WCNSS firmware, registers an HCI device on `HCI_SMD`, forwards incoming RPMSG payloads as HCI frames, sends outgoing HCI command/ACL packets over the matching channel, resets the controller during setup, and delegates BD address programming to QCA Rome helpers.

## Important APIs, Types, And Functions
- `struct btqcomsmd` stores the HCI device and the two RPMSG endpoints.
- `btqcomsmd_acl_callback` and `btqcomsmd_cmd_callback` are RPMSG receive callbacks for ACL data and events.
- `btqcomsmd_recv` allocates an skb in IRQ context, assigns HCI packet type, copies payload, and submits it to `hci_recv_frame`.
- `btqcomsmd_send` routes `HCI_ACLDATA_PKT` to `acl_channel` and `HCI_COMMAND_PKT` to `cmd_channel`.
- `btqcomsmd_setup` sends HCI reset and sets `HCI_QUIRK_USE_BDADDR_PROPERTY`; `btqcomsmd_set_bdaddr` calls `qca_set_bdaddr_rome` and sleeps for firmware recovery.
- `btqcomsmd_probe`/`remove` manage endpoint and HCI lifetime.

## Control Flow
Probe obtains the parent WCNSS controller data, opens the ACL and CMD channels, allocates an HCI device, installs callbacks, registers the device, and stores driver data. Incoming RPMSG channel callbacks increment RX byte counts and call the shared receive allocator. Outgoing HCI packets are sent immediately over the selected endpoint and freed only on success. Setup sends a reset to synchronize the controller and marks the BD address as firmware-node-provided. Remove unregisters/frees HCI first, then destroys command and ACL endpoints.

## State And Persistence
State is minimal and persists for platform-device lifetime: two endpoints and one HCI device. The remote firmware owns controller state and packet buffering. HCI stats are updated for RX/TX/errors. BD address persistence is absent on these devices, so the HCI quirk records that the firmware node property should supply it.

## Dependencies And Integration Points
Depends on rpmsg, Qualcomm WCNSS control channel opening, platform/OF matching, Bluetooth HCI core, and `btqca.h` for Rome BD address commands. It integrates with device tree compatible `qcom,wcnss-bt` and parent WCNSS infrastructure that exposes named SMD channels.

## Risks And Edge Cases
Callbacks run in IRQ context and use `GFP_ATOMIC`; allocation failures increment only error stats. `btqcomsmd_send` does not free skb on send failure, relying on caller/error handling expectations. Only command and ACL packet types are supported; SCO/ISO are rejected. Firmware is known to pause after BD address programming, requiring an arbitrary sleep before subsequent commands.

## Test Signals
Probe failure cleanup for first/second channel open and HCI registration, RX event/ACL delivery through both RPMSG callbacks, TX routing and stats for command/ACL packets, unsupported packet rejection, HCI reset during setup, BD address command plus post-command delay, and remove destroying endpoints after HCI unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btqcomsmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btrsi.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btrsi.c

## Purpose
Provides the Bluetooth HCI adapter glue for Redpine/RSI 91x coexistence devices. It registers an HCI device for the RSI core, forwards outgoing HCI packets into the RSI coexistence queue with required headroom/alignment, receives RSI-framed Bluetooth packets from the core, and exports `rsi_bt_ops` for attach/detach/receive integration.

## Important APIs, Types, And Functions
- `struct rsi_hci_adapter` stores the RSI private pointer, protocol operations, and HCI device.
- `rsi_hci_attach` allocates adapter/HCI state, stores BT context in the RSI core, selects HCI bus based on host interface, installs HCI callbacks, and registers the HCI device.
- `rsi_hci_detach` unregisters/frees the HCI device and adapter.
- `rsi_hci_send_pkt` updates TX stats, ensures `RSI_HEADROOM_FOR_BT_HAL` and 8-byte DMA alignment, then calls `coex_send_pkt(..., RSI_BT_Q)`.
- `rsi_hci_recv_pkt` extracts packet length/type from the RSI frame descriptor, copies the HCI payload into a new skb, and passes it to `hci_recv_frame`.
- `rsi_bt_ops` exports the module operations consumed by the RSI wireless core.

## Control Flow
The RSI core calls `attach` with its private context and operations. This driver allocates and registers an HCI device but leaves open/close/flush as no-ops because the parent core owns hardware power and transport. Bluetooth core TX invokes `send`, which may reallocate headroom and align data before handing the skb to the coexistence queue. Parent RX invokes `recv_pkt`; the driver reads the frame descriptor length, copies bytes after the 16-byte descriptor, sets packet type from descriptor byte 14, and submits the HCI frame upward. Detach tears down HCI registration and frees adapter memory.

## State And Persistence
Persistent state is only `rsi_hci_adapter` for the attachment lifetime. The parent RSI core stores the BT context and owns lower-level hardware state. SKBs are transient; TX ownership transfers to `coex_send_pkt` on success, while RX allocates a fresh skb per frame.

## Dependencies And Integration Points
Depends on Bluetooth HCI core, unaligned helpers, and `net/rsi_91x.h` for `rsi_proto_ops`, `rsi_mod_ops`, host-interface constants, and queue IDs. It integrates as an exported module API rather than as a bus driver with device IDs.

## Risks And Edge Cases
If `skb_realloc_headroom` succeeds but the subsequent DMA alignment adjustment is wrong, payload bytes can be corrupted before the parent sends them. When `skb_headroom` is already sufficient, the function does not enforce DMA alignment. `rsi_hci_recv_pkt` trusts the descriptor length and type without validating the provided buffer size. `rsi_hci_attach` returns `-EINVAL` for all post-allocation failures, losing the original error code.

## Test Signals
Attach/detach over SDIO and USB host interfaces, TX with insufficient and sufficient headroom, misaligned TX buffers, command/ACL/SCO stat updates, parent `coex_send_pkt` failures and ownership behavior, RX frame descriptor length/type parsing, allocation failure paths, and repeated attach/detach without leaked HCI devices or adapter contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btrsi.c -->
