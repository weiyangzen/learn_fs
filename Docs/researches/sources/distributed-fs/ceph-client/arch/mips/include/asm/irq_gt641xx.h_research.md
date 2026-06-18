# sources/distributed-fs/ceph-client/arch/mips/include/asm/irq_gt641xx.h


### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/irq_gt641xx.h` Galileo GT64120/GT641xx controller register, endian MMIO, timer, PCI, DMA, and IRQ contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 47 lines / 2074 bytes. macros/constants: `_ASM_IRQ_GT641XX_H`, `GT641XX_IRQ_BASE`, `GT641XX_MEMORY_OUT_OF_RANGE_IRQ`, `GT641XX_DMA_OUT_OF_RANGE_IRQ`, `GT641XX_CPU_ACCESS_OUT_OF_RANGE_IRQ`, `GT641XX_DMA0_IRQ`, `GT641XX_DMA1_IRQ`, `GT641XX_DMA2_IRQ`, `GT641XX_DMA3_IRQ`, `GT641XX_TIMER0_IRQ`, `GT641XX_TIMER1_IRQ`, `GT641XX_TIMER2_IRQ`, `GT641XX_TIMER3_IRQ`, `GT641XX_PCI_0_MASTER_READ_ERROR_IRQ`, `GT641XX_PCI_0_SLAVE_WRITE_ERROR_IRQ`, `GT641XX_PCI_0_MASTER_WRITE_ERROR_IRQ`, `GT641XX_PCI_0_SLAVE_READ_ERROR_IRQ`, `GT641XX_PCI_0_ADDRESS_ERROR_IRQ`; types/functions/declarations: `extern void gt641xx_irq_dispatch(void);`, `extern void gt641xx_irq_init(void);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by Malta/Galileo board setup, PCI host bridge, timers, DMA, and interrupt dispatch. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong endian, window, or interrupt masks break PCI, timers, DMA, and memory decode. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
