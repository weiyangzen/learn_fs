# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/bluecard_cs.c

## Purpose

`bluecard_cs.c` is the PCMCIA HCI driver for Anycom BlueCard Bluetooth cards. It directly programs card I/O registers, manages two transmit and receive windows, controls LEDs and baud rate, parses HCI packets from byte streams, and registers an `HCI_PCCARD` device.

## Important APIs, Types, And Functions

`struct bluecard_info` stores the PCMCIA device, HCI device, spinlock, LED timer, TX queue/state, RX parser state/count/skb, control register shadow, and hardware state bits. Hardware constants define command, interrupt, control, RX control, reset, and LED registers. TX functions include `bluecard_write`, `bluecard_write_wakeup`, and `bluecard_hci_send_frame`. RX and interrupt handling is in `bluecard_read`, `bluecard_receive`, and `bluecard_interrupt`. Lifecycle functions include `bluecard_open`, `bluecard_close`, `bluecard_probe`, `bluecard_config`, and `bluecard_release`.

## Control Flow

Probe allocates `bluecard_info`, enables IRQ configuration, and calls `bluecard_config`. Configuration claims an 8-bit I/O range by probing addresses, requests IRQ, enables the PCMCIA device, and opens the card. `bluecard_open` allocates an HCI device, detects card ID and LED capabilities from register `0x30`, resets and powers the card, enables interrupts, starts RX buffers, marks hardware ready, configures RTS threshold, waits before first traffic, and registers HCI.

The interrupt handler disables card interrupts, reads `REG_INTERRUPT`, handles RX buffer one/two ready bits by reading windows and acknowledging them, handles TX buffer ready bits by setting state flags and waking TX, then re-enables interrupts. RX parsing is a byte-oriented HCI state machine from packet type to header to payload; complete frames are delivered with `hci_recv_frame`. TX prepends packet type, writes up to 15 bytes into the selected hardware buffer, commands the FPGA to send, and toggles buffer selection. Special packet types with high bits encode baud-rate changes and trigger RTS/baud sequencing delays.

## State And Persistence

All state is volatile host/card state. `ctrl_reg` mirrors the card control register so bit updates are coherent. `hw_state` records readiness and LED features. `tx_state` records which hardware buffer is ready and whether TX is active. `rx_state`, `rx_count`, and `rx_skb` persist the HCI parser across interrupts. LED state is timer-driven and changes hardware LED output. Card contents do not persist across close or removal.

## Dependencies And Integration Points

The driver depends on PCMCIA core, ISA-style I/O port access, timers, spinlocks, skbuffs, and Bluetooth HCI core. It is built by `CONFIG_BT_HCIBLUECARD`, which requires `PCMCIA && HAS_IOPORT`. Device matching uses PCMCIA product IDs for BlueCard/LSE variants.

## Risks

This is register-level code with many timing assumptions. The baud-rate path uses blocking delays and special internal packet types, so changing TX queue handling can disturb initialization. The RX parser allocates `HCI_MAX_FRAME_SIZE` skbs and trusts header lengths; malformed hardware bytes can drive error counters and skb frees. Shared IRQ handling must return `IRQ_NONE` only for clearly unrelated interrupts. Cleanup must stop the LED timer and unregister/free HCI exactly once.

## Test Signals

Validation signals include successful PCMCIA I/O/IRQ allocation, HCI registration, card reset/power sequencing, interrupt-driven RX/TX, baud-rate setup on PCCARD-ID devices, LED timer behavior, clean detach, and HCI stats. Negative coverage should include no usable port range, IRQ request failure, card removal during TX/RX, unknown HCI packet type, and partial TX buffer writes.
