# sources/distributed-fs/ceph-client/arch/sparc/kernel/ebus.c

## Purpose
`ebus.c` provides EBus DMA controller helper routines for SPARC systems. It abstracts CSR programming, DMA setup, interrupt enable/disable, residue/address reporting, and optional shared interrupt handling for EBus clients.

## Important APIs, Types, and Functions
The public API is `ebus_dma_register()`, `ebus_dma_irq_enable()`, `ebus_dma_unregister()`, `ebus_dma_request()`, `ebus_dma_prepare()`, `ebus_dma_residue()`, `ebus_dma_addr()`, and `ebus_dma_enable()`. It operates on `struct ebus_dma_info` from `<asm/ebus_dma.h>`. Internal functions are `__ebus_dma_reset()` and `ebus_dma_irq()`.

## Control Flow and State
Registration validates MMIO registers, flags, callback requirements, and name, then resets the channel and programs burst/count/TCI bits. `ebus_dma_prepare()` resets and programs direction plus next-descriptor support. `ebus_dma_request()` refuses oversized or inactive transfers, verifies no next address is loaded, then writes count and bus address. Interrupt enable optionally calls `request_irq()` and toggles `EBDMA_CSR_INT_EN`; the IRQ handler acknowledges pending bits by writing CSR back and calls the client callback for error, DMA terminal count, or device interrupt events.

## Persistence and Dependencies
Persistent state is in device registers and the caller-owned `ebus_dma_info` lock, flags, IRQ, callback, and cookie. The file depends on MMIO accessors, Linux IRQ APIs, delays, and exported EBus DMA ABI.

## Integration Points, Risks, and Test Signals
Drivers using EBus DMA integrate through these helpers and must initialize `p->lock`, MMIO `regs`, IRQ, callback, and flags. Risks include reset timeout being silent, incorrect use of `no_drain`, races if callers manipulate registers outside the lock, and transfer length limited to 24 bits. Test signals are DMA completion callbacks, error callbacks, stable residue/address reads, correct IRQ free on disable/unregister, and no stuck drain/cycle-pending bits after prepare.
