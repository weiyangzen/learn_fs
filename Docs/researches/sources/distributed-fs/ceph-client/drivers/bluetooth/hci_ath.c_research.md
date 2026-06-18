# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_ath.c

## Purpose

`hci_ath.c` implements the Atheros AR300x HCI UART protocol extension (`HCI_UART_ATH3K`). It is an H4-derived transport with controller sleep/wakeup handling using UART modem-control lines, drops unsupported SCO transmit packets, provides a vendor BDADDR writer, and registers the protocol with HCI UART core.

## Important APIs, Types, and Functions

- `struct ath_struct` stores the owning `hci_uart`, current sleep flag, RX reassembly SKB, TX queue, and work item used for context-switch/wakeup.
- `ath_wakeup_ar3k()` toggles RTS and checks CTS to wake a sleeping controller.
- `ath_hci_uart_work()` verifies wakeup when sleep is enabled, clears `HCI_UART_SENDING`, and calls `hci_uart_tx_wakeup()`.
- `ath_open()`, `ath_close()`, and `ath_flush()` manage private data, flow-control requirement, queue purging, RX SKB cleanup, and work cancellation.
- `ath_vendor_cmd()` sends opcode `0xfc0b` with a tag-write payload; `ath_set_bdaddr()` writes `INDEX_BDADDR`.
- `ath_setup()` installs the HCI BDADDR setter.
- `ath_recv()` uses `h4_recv_buf()` for ACL/SCO/event packets.
- `ath_enqueue()` filters SCO, tracks sleep enable commands (`HCI_OP_ATH_SLEEP`), prepends packet type, queues data, marks sending, and schedules wakeup work.
- `ath_dequeue()` returns queued SKBs to the HCI UART core.

## Control Flow

Open requires UART flow control, allocates private data, initializes the TX queue, stores the back pointer, and initializes work. Setup only installs the BDADDR vendor hook. On transmit, SCO packets are discarded, command packets are inspected for the Atheros sleep vendor opcode to update `cur_sleep`, and all queued packets are prefixed with the H4 type. The worker wakes the controller if sleep mode is active and CTS is low, then clears the sending bit and asks the HCI UART core to transmit.

## State and Persistence

The only driver state is volatile UART protocol state: sleep enabled/disabled, partial RX SKB, queued TX SKBs, and scheduled work. BDADDR writes are sent to the controller through a vendor command; persistence depends on controller behavior and is not managed by the driver.

## Dependencies and Integration Points

The file depends on `hci_uart`, tty modem-control operations, H4 receive helpers, workqueues, sk_buffs, and Bluetooth HCI core. It registers as manufacturer 69 and protocol ID `HCI_UART_ATH3K`.

## Risks

The wakeup sequence assumes tty driver modem-control callbacks are present and meaningful. SCO packets are silently freed, which is intentional for this protocol but can surprise higher-level tests expecting an error. `ath_enqueue()` reads command headers directly and assumes command SKBs are at least header-sized. Work and close ordering must keep `ath` valid until `cancel_work_sync()` completes.

## Test Signals

Signals include open rejection without flow control, successful protocol registration, RTS/CTS wake behavior when sleep is enabled, `HCI_UART_SENDING` clearing, BDADDR vendor command success, SCO drop behavior, and correct H4 RX reassembly. Tests should include sleep command enqueue, CTS low/high cases, close with pending work, and malformed short command SKBs if fuzzing the transport boundary.
