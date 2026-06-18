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
