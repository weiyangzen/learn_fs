# sources/distributed-fs/ceph-client/drivers/bluetooth/btsdio.c

## Purpose

`btsdio.c` is a generic Bluetooth SDIO transport driver for class A and class B Bluetooth SDIO functions. It binds SDIO functions, registers an HCI device with bus type `HCI_SDIO`, sends HCI frames through SDIO write registers, receives interrupt-driven frames from SDIO read registers, and handles open/close/flush lifecycle.

## Important APIs, Types, and Functions

- `btsdio_table` matches `SDIO_CLASS_BT_A` and `SDIO_CLASS_BT_B`.
- `struct btsdio_data` holds the `hci_dev`, `sdio_func`, deferred TX work item, and TX queue.
- Register constants (`REG_RDAT`, `REG_TDAT`, `REG_PC_RRT`, `REG_PC_WRT`, `REG_INTRD`, `REG_EN_INTRD`, `REG_MD_SET`) describe the simple SDIO data/control interface.
- `btsdio_send_frame()` validates outgoing packet types, updates HCI stats, queues SKBs, and schedules work.
- `btsdio_work()` drains the TX queue under `sdio_claim_host()`.
- `btsdio_tx_packet()` prepends the 4-byte Type-A SDIO header and writes to `REG_TDAT`.
- `btsdio_interrupt()` reads interrupt status, clears receive interrupt, and calls `btsdio_rx_packet()`.
- `btsdio_rx_packet()` reads the 4-byte header, validates length and HCI packet type, reads payload, and forwards frames to `hci_recv_frame()`.
- `btsdio_probe()` and `btsdio_remove()` allocate/register and unregister/free the HCI device.

## Control Flow

Probe ignores certain non-removable Broadcom SDIO Bluetooth functions because those boards use UART for Bluetooth. Otherwise it allocates driver data, initializes TX queue/work, creates an HCI device, installs open/close/flush/send callbacks, sets a reset-on-close quirk for one vendor/device pair, registers with HCI core, and stores SDIO driver data.

Open claims the SDIO host, enables the function, claims the IRQ, optionally sets Type-B mode, and enables receive interrupts. Transmit path queues HCI frames and a workqueue serially writes Type-A framed packets. Receive path is IRQ driven: the interrupt handler clears interrupt state, reads and validates one packet, and requests read retry on errors. Close disables interrupts, releases IRQ, disables the function, and releases the SDIO host.

## State and Persistence

Runtime state consists of TX queue contents, the work item, SDIO function pointer, and HCI stats. There is no firmware loading or persistent configuration. SDIO retry control registers provide transient device-side state for failed reads/writes.

## Dependencies and Integration Points

The file integrates Linux MMC/SDIO APIs, Bluetooth HCI core, sk_buff queues, and module SDIO registration. It is a transport-only driver; vendor-specific firmware setup is not implemented here.

## Risks

RX length accepts up to `65543`, allocating `len - 4`; malformed devices can cause large allocations or repeated retry loops. `btsdio_tx_packet()` pushes a header into the SKB and pulls it back only on write failure, so callers must supply sufficient headroom. The IRQ handler processes only the indicated receive event per interrupt and relies on device retry registers for recovery. Work cancellation during remove is covered, but close does not explicitly cancel TX work before disabling the function.

## Test Signals

Signals include successful SDIO probe/registration, IRQ claim, frame TX/RX stat increments, no retry storms on malformed RX, and correct ignore behavior for non-removable Broadcom IDs. Functional tests should exercise Type-A and Type-B classes, invalid HCI packet types, SDIO write failures, remove during queued TX, and open/close cycles.
