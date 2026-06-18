# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1000_dma.h

**Purpose:** Defines the legacy Au1000-style eight-channel, double-buffer DMA controller interface used by early Alchemy peripheral drivers.

**Important APIs/types/functions:** Exports DMA register offsets and mode bits, device ID enums for primary and AU1100 secondary banks, `struct dma_chan`, extern `au1000_dma_table[]`, `request_au1000_dma()`, `free_au1000_dma()`, proc read hook, and `au1000_dma_spin_lock`. Inline API includes `get_dma_chan()`, `claim_dma_lock()/release_dma_lock()`, buffer enable helpers, `start_dma()`, `halt_dma()`, `disable_dma()`, `dma_halted()`, `init_dma()`, mode/fifo/address/count setters, done-bit clear/query helpers, `get_dma_done_irq()`, and `get_dma_residue()`.

**Control flow:** Drivers request a channel, set permitted mode bits, initialize FIFO/device ID, program buffer addresses/counts, enable buffers, start DMA, handle done interrupts, clear done bits, and halt/disable on teardown. `halt_dma()` polls the hardware halt bit and logs if it expires.

**State and persistence behavior:** Software state lives in the global channel table and spinlock; hardware state lives in channel MMIO registers. The inline layer silently returns on invalid/unallocated channels, which avoids crashes but can hide misuse.

**Dependencies and integration points:** Depends on Linux raw IO, spinlocks, delays, IRQ handler types, `CPHYSADDR()`, and DMA controller implementation in Alchemy common code. Used by UART, AC97, USB device, I2S, SD, and general-purpose DMA users.

**Risks:** Double-buffer ownership and count masks are easy to misuse. `disable_dma()` writes `~DMA_GO` to the clear register, relying on write-one-to-clear semantics. Residue conversion depends on DMA width bits. Missing locks around register programming by callers can race interrupts.

**Test signals:** Exercise each device ID, allocate/free channels under contention, run RX/TX double-buffer transfers, verify interrupt clearing, halt timeout behavior, residue accounting for 8/16/32-bit widths, and invalid-channel handling.
