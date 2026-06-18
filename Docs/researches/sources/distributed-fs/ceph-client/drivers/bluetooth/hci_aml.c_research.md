# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_aml.c

## Purpose

`hci_aml.c` is the Amlogic Bluetooth HCI UART/serdev driver. It controls platform power resources, downloads ICCM/DCCM firmware over Amlogic TCI vendor commands, configures RF and baudrate, starts the controller, handles BDADDR operations, and registers both an HCI UART protocol and a serdev device driver for Amlogic device-tree compatible controllers.

## Important APIs, Types, and Functions

- `struct aml_serdev` combines `struct hci_uart`, device resources, enable GPIO, regulator, LPO clock, match data, and firmware name.
- `struct aml_data` stores per-protocol RX SKB and TX queue.
- `struct aml_device_data` provides ICCM/DCCM offsets and coexistence RF behavior from OF match data.
- `aml_send_tci_cmd()` is the central command helper for private TCI read/write/baud/reset/download opcodes.
- Firmware helpers `aml_download_firmware()`, `aml_send_firmware()`, and `aml_send_firmware_segment()` load the named firmware and write ICCM/DCCM sections in 248-byte operations, enforcing a 512 KiB max.
- Setup helpers include `aml_power_on()`, `aml_power_off()`, `aml_set_baudrate()`, `aml_config_rf()`, `aml_start_chip()`, `aml_dump_fw_version()`, `aml_send_reset()`, and `aml_check_bdaddr()`.
- HCI UART callbacks `aml_open()`, `aml_close()`, `aml_setup()`, `aml_recv()`, `aml_enqueue()`, and `aml_dequeue()` implement protocol lifecycle and H4 framing.
- `aml_serdev_probe()`, `aml_serdev_remove()`, and `aml_serdev_shutdown()` bind serdev devices and register/unregister the HCI UART device.

## Control Flow

Serdev probe allocates `aml_serdev`, stores it as serdev driver data, registers an HCI UART device with `aml_hci_proto`, then assigns match data. Protocol open parses device tree resources, requires UART flow control, allocates protocol data, and initializes the TX queue. Setup powers the chip, changes controller and host baudrate to `oper_speed`, downloads firmware, configures RF based on coexistence, starts the chip via memory transaction enable and reset bits, waits for startup, logs firmware version, sends HCI reset, and marks the default Amlogic BDADDR invalid when detected.

TX queues SKBs and prepends the H4 packet type when dequeued. RX uses `h4_recv_buf()` for ACL, SCO, event, and ISO packets. Close purges queues, frees partial RX, releases private data, and powers off the device. Shutdown also powers off platform resources.

## State and Persistence

Runtime state includes platform resource enablement, UART baudrate, TX/RX SKB state, firmware download progress, and controller RAM contents. Firmware name is provided by device property. The driver does not persist settings locally; BDADDR setting is issued through a vendor command if requested by HCI core.

## Dependencies and Integration Points

The driver integrates Linux serdev, device properties/OF match data, GPIO, regulator, clock APIs, firmware loading, HCI UART core, H4 receive helpers, and Bluetooth HCI command sync. Device-tree compatibles include `amlogic,w155s2-bt` and `amlogic,w265s2-bt`.

## Risks

Ordering is critical: power, baudrate, firmware download, RF config, start, reset, and BDADDR validation must remain synchronized with controller expectations. `aml_download_firmware()` assumes firmware layout begins with `struct aml_fw_len` followed by ICCM and DCCM images; malformed firmware could produce invalid offsets/lengths unless size checks are strengthened. `aml_serdev_probe()` assigns `aml_dev_data` after registering the HCI UART device; if registration can trigger open/setup immediately, match data may be observed unset. Power-on error paths do not unwind partially enabled resources in every failure case. TCI response parsing treats missing response payload as success in some helpers because `err` remains zero.

## Test Signals

Signals include successful GPIO/regulator/clock acquisition, flow-control requirement enforcement, firmware size and segment download success, RF single/double antenna writes, firmware version log, HCI reset completion, invalid default BDADDR quirk, and clean power-off on close/remove/shutdown. Tests should cover malformed firmware lengths, missing DT properties, baudrate command failure, partial power-on failure, coexistence match data, and RX/TX H4 framing.
