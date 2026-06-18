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
