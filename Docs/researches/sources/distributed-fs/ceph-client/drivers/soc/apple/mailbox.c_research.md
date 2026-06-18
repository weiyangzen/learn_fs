# sources/distributed-fs/ceph-client/drivers/soc/apple/mailbox.c

## Purpose
This driver implements the low-level Apple mailbox FIFO used for 96-bit messages between the application processor and Apple coprocessors. It supports ASC, T8015 ASC, and M3 register layouts.

## Important APIs, Types, And Functions
`struct apple_mbox_hw` describes register offsets, status bits, and optional mailbox-level IRQ controls. Exported APIs are `apple_mbox_get()`, `apple_mbox_get_byname()`, `apple_mbox_start()`, `apple_mbox_stop()`, `apple_mbox_poll()`, and `apple_mbox_send()`. IRQ handlers are `apple_mbox_recv_irq()` and `apple_mbox_send_empty_irq()`.

## Control Flow
Probe maps registers, requests named `recv-not-empty` and `send-empty` IRQs with `IRQF_NO_AUTOEN`, enables runtime PM, and stores driver data. Consumers get a mailbox via DT phandle, set `rx` and `cookie`, and start it. Sending takes the TX lock, waits for A2I FIFO space either by atomic polling or send-empty completion, writes message words, and returns. Receive IRQs poll I2A messages under RX lock and invoke the consumer callback.

## State, Persistence, And Dependencies
State is `struct apple_mbox`: MMIO registers, active flag, IRQ numbers, locks, TX completion, and callback pointer. Dependencies include OF phandles, platform IRQs, runtime PM, spinlocks, iopoll, and MMIO read/write access.

## Integration Points
RTKit is the primary in-tree consumer. Device links bind consumer lifetime to the mailbox provider. Hardware match data selects register layout for Apple compatibles.

## Risks
The driver assumes callbacks are installed before start; a NULL `rx` would crash on incoming messages. The send path uses level-triggered IRQ behavior carefully, but incorrect ack order on new hardware could cause missed or repeated wakeups. Runtime PM is active only while started.

## Test Signals
Test blocking and atomic sends when FIFO is full, receive polling and IRQ paths, runtime PM transitions on start/stop, M3 IRQ-ack behavior, phandle deferral, and RTKit boot traffic.
