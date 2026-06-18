# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/pio.h

## Purpose
`pio.h` declares the B43 PIO register interface, queue data structures, MMIO helper accessors, and public PIO lifecycle/TX/RX entry points. It is the shared contract between `pio.c` and the broader B43 driver for programmed I/O transfers.

## Important APIs, Types, And Definitions
- Pre-revision-8 register offsets and bits: `B43_PIO_TXCTL`, `B43_PIO_TXDATA`, `B43_PIO_TXQBUFSIZE`, `B43_PIO_RXCTL`, and `B43_PIO_RXDATA`, with TX byte-lane, EOF, frame-ready, flush, suspend, queue-suspend, and command-count masks.
- Revision-8-plus register offsets and bits: `B43_PIO8_TXCTL`, `B43_PIO8_TXDATA`, `B43_PIO8_RXCTL`, and `B43_PIO8_RXDATA`, with 32-bit byte-lane masks and EOF/FREADY/SUSPREQ/QSUSP/FLUSH bits.
- `B43_PIO_MAX_NR_TXPACKETS`: fixed metadata slot count of 32 per TX queue.
- `struct b43_pio_txpacket`: per in-flight TX frame metadata: owning queue, SKB pointer, fixed index, and list node.
- `struct b43_pio_txqueue`: per hardware TX queue state: device pointer, MMIO base, hardware buffer size and used count, available packet slots, stopped flag, queue index, mac80211 priority, slot array, free list, and core revision shortcut.
- `struct b43_pio_rxqueue`: RX queue state with device pointer, MMIO base, and core revision shortcut.
- Inline accessors: `b43_piotx_read16/32()`, `b43_piotx_write16/32()`, `b43_piorx_read16/32()`, and `b43_piorx_write16/32()` add queue-local MMIO offsets to `q->mmio_base`.
- Public functions: `b43_pio_init()`, `b43_pio_free()`, `b43_pio_tx()`, `b43_pio_handle_txstatus()`, `b43_pio_rx()`, `b43_pio_tx_suspend()`, and `b43_pio_tx_resume()`.

## Control Flow And State
This header has no executable high-level control flow beyond inline MMIO wrappers. It defines the mutable state that `pio.c` uses for PIO queue lifecycles. TX queue metadata slots transition from the free list to active ownership when a frame is written, then return to the list on TX status. `buffer_used` and `free_packet_slots` provide software-side queue capacity accounting before writing to hardware. `stopped` and `queue_prio` persist software backpressure state between `b43_stop_queue()` and completion-time `b43_wake_queue()`. Revision-specific register layouts are selected by `q->rev` in implementation code, while this header exposes both layouts.

## Dependencies And Integration Points
- Includes `b43.h` for `struct b43_wldev` and MMIO accessors, plus Linux interrupt, I/O, list, and SKB types.
- `struct b43_pio` in `b43.h` stores pointers to the queue types declared here.
- Public functions are called by `main.c` and `xmit.c`; hardware access helpers are used only by the PIO implementation.
- Register base constants live in `b43.h`, while this file defines offsets relative to each queue base.

## Risks
- The data structures assume single-owner serialized access. Parallel TX/RX/status changes without the driver mutex or proper interrupt serialization would corrupt lists and counters.
- `buffer_size` and `buffer_used` are `u16`; any future hardware with larger PIO FIFOs would require widening or careful bounds checks.
- The fixed 32-slot queue contract is encoded into cookies in `pio.c`; increasing `B43_PIO_MAX_NR_TXPACKETS` beyond the low 12-bit cookie space would require cookie changes.
- Revision-specific offsets are easy to mix because both rev7 and rev8 TXCTL/RXCTL offsets are zero but data offsets differ.

## Test Signals
- Compile coverage should include PIO-capable configurations and catch mismatched prototypes or missing struct members.
- Runtime signals come from the `pio.c` paths: successful forced-PIO init/free, TX status completion returning slots to the list, RX frame delivery, and suspend/resume queue control.
- Static review after changes should check that every new register bit is used under the correct hardware revision gate.
