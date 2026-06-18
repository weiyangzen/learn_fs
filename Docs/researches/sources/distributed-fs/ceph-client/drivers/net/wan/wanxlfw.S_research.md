# sources/distributed-fs/ceph-client/drivers/net/wan/wanxlfw.S

## Purpose
`wanxlfw.S` is the firmware-side m68k/QUICC code for wanXL cards. It is loaded by `wanxl.c` into on-card RAM and handles SCC HDLC port setup, host/card descriptor movement, PLX DMA transfers, doorbell commands, cable/status monitoring, and interrupts.

## Important APIs, Types, And Functions
The firmware consumes shared constants from `wanxl.h`. Entry starts at `_start`, then `init`. Important routines are `open_port`, `close_port`, `tx`, `rx`, `tx_end`, `pci9060_interrupt`, `port_interrupt_1..4`, `check_csr`, `timer_interrupt`, and optional `ram_test`. Macros implement PCI/local copies either via PLX DMA (`memcpy_from_pci`, `memcpy_to_pci`) or direct windowed memcpy depending on `QUICC_MEMCPY_USES_PLX`.

## Control Flow
Initialization translates host-provided shared-memory PCI addresses into the firmware's window, installs interrupt vectors, configures CPM/PLX interrupts and DMA, optionally sizes/tests RAM, signals initialization through mailbox 5, configures port pins, and enters the main loop. The main loop waits for accumulated `channel_stats`, handles close before open for each port, processes open commands, queues host TX descriptors, services SCC tasks by completing TX and draining RX, builds a host doorbell mask, and writes `PLX_DOORBELL_FROM_CARD`.

`open_port` sets shared open status, initializes TX/RX BD rings in DPRAM, applies clocking from host status, asserts DTR, configures SCC parity/CRC/encoding, and enables SCC interrupts. `tx` copies host packet data into card buffers and marks transmit BDs ready. `rx` validates received BDs, removes parity bytes, copies packet data to host RX descriptors if available, updates error counters on overrun/bad frame, and frees BDs. `tx_end` converts SCC completion into `PACKET_SENT` or `PACKET_UNDERRUN`.

## State And Persistence
Firmware state lives in on-card RAM variables such as `channel_stats`, per-port TX/RX indices, `rx_out`, `tx_count`, `parity_bytes`, and CSR output shadows. Shared host-visible state is stored through `ch_status_addr` and `rx_descs_addr`. State lasts until card reset or firmware reload.

## Dependencies And Integration Points
The firmware depends on m68k/QUICC register layout, PLX9060 mailboxes/doorbells/DMA, SCC HDLC buffer descriptors, shared ABI definitions in `wanxl.h`, and host initialization in `wanxl.c` that writes firmware and shared-memory pointers.

## Risks
Host/firmware ABI drift is the primary risk. The firmware assumes descriptor status values, offsets, buffer counts, and shared memory addresses are valid. PLX DMA copy macros wait for interrupts and must run with expected interrupt masking. RX overrun handling drops frames when host RX descriptors are not empty. Cable status is polled by timer and signaled by doorbells, so status updates depend on firmware timer operation.

## Test Signals
Test firmware load and mailbox initialization, port open/close shared status transitions, host TX descriptor to SCC BD movement, TX underrun reporting, RX good/bad/overrun paths, cable status changes, PLX DMA completion, and compatibility checks after changing `wanxl.h`.
