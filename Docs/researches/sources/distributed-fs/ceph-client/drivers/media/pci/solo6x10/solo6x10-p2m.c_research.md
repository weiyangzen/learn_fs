<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-p2m.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-p2m.c

## Purpose
`solo6x10-p2m.c` implements the SOLO PCI-to-memory DMA engine abstraction used to move data between host memory and SOLO SDRAM, and it detects usable on-card SDRAM size at probe time.

## Important APIs, Types, and Functions
Module parameters `multi_p2m` and `desc_mode` opt into multiple channels and descriptor mode on SOLO6010. Public APIs are `solo_p2m_dma()`, `solo_p2m_dma_t()`, `solo_p2m_fill_desc()`, and `solo_p2m_dma_desc()`. Interrupt paths are `solo_p2m_isr()` and `solo_p2m_error_isr()`. `solo_p2m_test()` writes/reads SDRAM patterns, while `solo_p2m_init()` configures engines and detects memory size.

## Control Flow
Single-buffer callers map CPU memory with the PCI DMA API, fill a descriptor, and delegate to `solo_p2m_dma_desc()`. The descriptor path chooses P2M channel 0 unless multi-channel 6010 mode is enabled, locks that channel, starts hardware descriptor mode for eligible multi-descriptor transfers or manually starts descriptor 1, waits for completion, handles errors/timeouts, stops the engine, restores config, and unlocks. The ISR either completes a transfer or programs the next descriptor in manual mode. Init configures all P2M channels, enables their IRQs, then probes 128/64/32 MB SDRAM configurations by resetting the chip and verifying test patterns at high addresses.

## State and Persistence
Each `solo_p2m_dev` stores a mutex, completion, descriptor cursor, descriptor pointer, and error flag. `solo_dev` stores detected `sdram_size`, timeout count, P2M wait duration, and the atomic channel counter. State is volatile and reset at driver initialization.

## Dependencies and Integration Points
The file depends on PCI DMA mapping, SOLO P2M and SDRAM control registers, IRQ dispatch from the core driver, and SDRAM layout macros. V4L2 display, V4L2 encoder, ALSA G.723, OSD, and motion code depend on these DMA APIs.

## Risks and Edge Cases
Descriptor arrays are one-based in the call convention (`desc[1]` is first), which is unusual and easy to misuse. SOLO6110 is forced to channel 0 and manual descriptor stepping because nonzero P2M and descriptor mode are known-problematic. P2M init resets memory controller state while probing SDRAM, so ordering relative to other hardware setup is important.

## Test Signals
Validate DMA reads and writes, descriptor and manual modes, wrap-sized encoder transfers, P2M error interrupt completion, timeout accounting, multi-P2M 6010 behavior, 6110 channel-0 restriction, and correct SDRAM size detection including rejection when `SOLO_SDRAM_END()` exceeds memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-p2m.c -->
