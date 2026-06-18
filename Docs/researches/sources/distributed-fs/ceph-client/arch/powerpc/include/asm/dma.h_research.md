## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dma.h

Purpose: provides legacy 8237-style ISA DMA register definitions and channel helpers for PowerPC platforms that emulate or expose PC-compatible DMA.

Important APIs/types/functions: constants define DMA controller ports, address/count/page registers, modes, and limits. Helpers include `claim_dma_lock()`, `release_dma_lock()`, `enable_dma()`, `disable_dma()`, `clear_dma_ff()`, `set_dma_mode()`, `set_dma_page()`, `set_dma_addr()`, `set_dma_count()`, `get_dma_residue()`, `request_dma()`, and `free_dma()`.

Control flow: callers claim `dma_spin_lock`, program mode/address/count/page registers with port I/O, enable the channel, and later query residue or disable/free. Address/count programming differs for 8-bit channels 0-3 and 16-bit channels 5-7.

State and persistence: hardware DMA controller registers persist transfer state. `dma_spin_lock` serializes register programming. `DMA_MODE_READ/WRITE` are externs on 32-bit and constants on 64-bit.

Dependencies and integration: depends on `asm/io.h`, spinlocks, and legacy ISA/floppy/sound style drivers. The header mainly keeps old generic DMA code buildable on PowerPC.

Risks and test signals: boundary, alignment, flip-flop, and count-minus-one rules are easy to violate. Port writes must happen with interrupts disabled while holding the lock. Test signals include floppy/ISA DMA operation, residue correctness, DMA API debug, and builds on 32-bit/64-bit PowerPC.
