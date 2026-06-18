# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00mmio.c

## Purpose
`rt2x00mmio.c` provides generic support for rt2x00 devices accessed through memory-mapped I/O, mainly PCI/PCIe chips. It implements busy-wait register polling, RX completion for descriptor rings, simple queue flush waiting, coherent descriptor DMA allocation, IRQ registration, and corresponding cleanup.

## Important APIs, Types, And Functions
Exported APIs are `rt2x00mmio_regbusy_read()`, `rt2x00mmio_rxdone()`, `rt2x00mmio_flush_queue()`, `rt2x00mmio_initialize()`, and `rt2x00mmio_uninitialize()`. Internal helpers allocate and free coherent descriptor memory for every `struct data_queue`. Per-entry MMIO private state is `struct queue_entry_priv_mmio` from `rt2x00mmio.h`, containing descriptor virtual and DMA addresses.

## Control Flow
`rt2x00mmio_regbusy_read()` reads a register until a supplied bit field clears, delaying between attempts, and returns a success boolean. `rt2x00mmio_rxdone()` processes up to 15 RX entries per invocation. It stops when the hardware-specific `get_entry_state()` says the current entry is still device-owned, wires the descriptor pointer into the skb descriptor, marks DMA start/done, and passes the entry to `rt2x00lib_rxdone()` with `GFP_ATOMIC`. Returning true means the tasklet should reschedule because the loop hit its per-pass budget.

Initialization iterates all queues, allocates one coherent descriptor block per queue sized `limit * desc_size`, and stores per-entry descriptor pointers. After descriptor memory is ready it requests the device IRQ using the hardware driver's `irq_handler`. Error unwind frees all descriptor allocations already made. Uninitialization frees the IRQ first, then releases coherent descriptor memory for every queue.

## State And Persistence
The file mutates queue entry private descriptor pointers and the device IRQ registration. Descriptor memory persists only while the device is initialized. RX completion updates queue indices indirectly through rt2x00lib once entries are processed. There is no durable state outside device memory and kernel allocations.

## Dependencies And Integration Points
It depends on `rt2x00mmio.h` register accessors, Linux DMA coherent allocation, IRQ APIs, queue metadata from `rt2x00queue.h`, and rt2x00lib RX/DMA callbacks. Hardware drivers such as `rt61pci.c` supply descriptor sizes, queue limits, `get_entry_state()`, `clear_entry()`, and the interrupt handler.

## Risks
The RX loop relies on the hardware driver's descriptor ownership bit being correct; a stale or inverted bit can either drop completions or spin through entries not ready for the host. Descriptor DMA allocation must match the queue layout and hardware ring base programming. The flush helper only waits up to ten 50 ms intervals and ignores `drop`, so hardware drivers that cannot drain queues in that window will report flush failures higher up. IRQ registration after DMA allocation means unwind ordering must stay correct.

## Test Signals
Test signals include successful coherent DMA allocation for all RX/TX/beacon queues, IRQ request/free pairing, RX tasklet processing batches without descriptor corruption, indirect register busy-read timeout logging for stuck BBP/RF/MCU registers, queue flush behavior under active TX/RX, and clean suspend/remove without leaked IRQs or DMA mappings.
