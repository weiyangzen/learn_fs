# sources/distributed-fs/ceph-client/arch/mips/include/asm/hazards.h


### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/hazards.h` Low-level MIPS ISA, instruction encoding, hazard barrier, jump-label patching, or symbol linkage contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 422 lines / 8648 bytes. macros/constants: `_ASM_HAZARDS_H`, `___ssnop`, `___ehb`, `__mtc0_tlbw_hazard`, `__mtc0_tlbr_hazard`, `__tlbw_use_hazard`, `__tlb_read_hazard`, `__tlb_probe_hazard`, `__irq_enable_hazard`, `__irq_disable_hazard`, `__back_to_back_c0_hazard`, `instruction_hazard`, `__mtc0_tlbw_hazard`, `__mtc0_tlbr_hazard`, `__tlbw_use_hazard`, `__tlb_read_hazard`, `__tlb_probe_hazard`, `__irq_enable_hazard`; types/functions/declarations: `extern void mips_ihb(void);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/stringify.h>`, `<asm/compiler.h>`.

### Integration Points
Used by assembly, exception/TLB code, static keys, syscall linkage, emulators, probes, and patching paths. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong ISA selection, barriers, instruction fields, or symbol aliases cause configuration-specific crashes. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
