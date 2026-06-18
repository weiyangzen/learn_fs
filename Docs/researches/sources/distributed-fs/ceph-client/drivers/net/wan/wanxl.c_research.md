# sources/distributed-fs/ceph-client/drivers/net/wan/wanxl.c

## Purpose
`wanxl.c` is the host-side PCI driver for SBE wanXL serial cards. It loads on-card firmware, establishes a shared host/card status area, handles PLX9060 doorbell interrupts, registers generic HDLC ports, and moves HDLC packets through shared descriptors and DMA mappings.

## Important APIs, Types, And Functions
`struct port` stores per-port HDLC netdevice, TX ring indexes, clock type, and skb ownership. `struct card_status` is the shared memory layout visible to firmware, containing RX descriptors and per-port status blocks. `struct card` stores mapped PLX registers, PCI device, RX ring, coherent status memory, and flexible port array. Key functions include `wanxl_cable_intr()`, `wanxl_tx_intr()`, `wanxl_rx_intr()`, `wanxl_intr()`, `wanxl_xmit()`, `wanxl_attach()`, `wanxl_ioctl()`, `wanxl_open()`, `wanxl_close()`, `wanxl_get_stats()`, `wanxl_puts_command()`, `wanxl_reset()`, and `wanxl_pci_init_one()`.

## Control Flow
Probe enables PCI, sets a temporary 28-bit DMA mask for coherent status memory due to card/QUICC limitations, requests regions, allocates the card and coherent `card_status`, restores 32-bit DMA for packet buffers, maps PLX registers, waits for PUTS self-test completion, reads reported RAM size, commands byte-swap mode, allocates RX skbs/descriptors, maps card RAM, writes included firmware and shared-memory pointers into card RAM, commands abort-and-jump, waits for firmware initialization, requests IRQ, allocates/registers HDLC ports, and reports cable state. TX maps skb data, fills a per-port TX descriptor, rings the card doorbell, advances the ring, and stops the queue if the next descriptor is busy. Doorbell interrupt dispatch handles TX completion, cable changes, and RX completions.

## State And Persistence
Firmware and card registers hold active hardware state; host state is volatile. The coherent `card_status` is the key shared contract with firmware. `wanxl_close()` asks firmware to close a port, waits for status, stops the queue, and unmaps/frees outstanding TX skbs. Remove unregisters ports, frees IRQ, resets the card, unmaps RX buffers, unmaps PLX, frees coherent status memory, releases PCI resources, and frees card memory.

## Dependencies And Integration Points
The driver integrates with generic HDLC, PCI IDs for wanXL100/200/400, DMA mapping APIs, PLX9060 registers, the generated `wanxlfw.inc` firmware blob, constants and shared layouts from `wanxl.h`, and firmware-side doorbell/status behavior from `wanxlfw.S`.

## Risks
The host/firmware ABI is tight: descriptor sizes, status offsets, doorbell bits, and endianness must match `wanxl.h` and `wanxlfw.S`. DMA mask switching is delicate and platform-sensitive. `wanxl_rx_intr()` allocates a replacement skb after consuming one; if allocation fails, the descriptor address becomes zero and later packets are dropped until a future successful replacement. Open/close wait loops use `time_after(timeout, jiffies)` style and should be checked carefully when modified. Firmware loading from an included blob complicates independent updates.

## Test Signals
Test probe through firmware initialization, PUTS timeout/failure paths, RAM-size sanity check, DMA mask failures, IRQ dispatch for RX/TX/cable bits, queue stop/wake under TX ring pressure, port open/close status handshakes, RX replacement allocation failure, and generic HDLC attach validation for all supported parity/encoding modes.
