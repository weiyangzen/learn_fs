# subset-b-000727 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn01.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn01.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn01.h` DECstation platform hardware contract for kn01.h: board slot offsets, interrupt input numbering, CSR/error/status bits, and where present bus-error or IRQ setup declarations. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 89 lines / 3291 bytes. macros/constants: `__ASM_MIPS_DEC_KN01_H`, `KN01_SLOT_BASE`, `KN01_SLOT_SIZE`, `KN01_PMASK`, `KN01_PCC`, `KN01_VDAC`, `KN01_RES_3`, `KN01_RES_4`, `KN01_RES_5`, `KN01_RES_6`, `KN01_ERRADDR`, `KN01_LANCE`, `KN01_LANCE_MEM`, `KN01_SII`, `KN01_SII_MEM`, `KN01_DZ11`, `KN01_RTC`, `KN01_ESAR`; types/functions/declarations: `struct pt_regs;`, `extern u16 cached_kn01_csr;`, `extern void dec_kn01_be_init(void);`, `extern int dec_kn01_be_handler(struct pt_regs *regs, int is_fixup);`, `extern irqreturn_t dec_kn01_be_interrupt(int irq, void *dev_id);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/interrupt.h>`, `<linux/spinlock.h>`, `<linux/types.h>`.

### Integration Points
DEC board setup, TURBOchannel/IOASIC probing, RTC, serial, Ethernet, SCSI, framebuffer, HALT, LED, and bus-error paths use these values to map hardware and dispatch interrupts. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Primary risks are fixed hardware ABI drift, misrouted cascaded interrupts, stale cached CSR shadows, and incorrect acknowledgement of memory or I/O bus errors. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn01.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02.h` DECstation platform hardware contract for kn02.h: board slot offsets, interrupt input numbering, CSR/error/status bits, and where present bus-error or IRQ setup declarations. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 91 lines / 3264 bytes. macros/constants: `__ASM_MIPS_DEC_KN02_H`, `KN02_SLOT_BASE`, `KN02_SLOT_SIZE`, `KN02_SYS_ROM`, `KN02_RES_1`, `KN02_CHKSYN`, `KN02_ERRADDR`, `KN02_DZ11`, `KN02_RTC`, `KN02_CSR`, `KN02_SYS_ROM_7`, `KN02_CSR_RES_28`, `KN02_CSR_PSU`, `KN02_CSR_NVRAM`, `KN02_CSR_REFEVEN`, `KN02_CSR_NRMOD`, `KN02_CSR_IOINTEN`, `KN02_CSR_DIAGCHK`; types/functions/declarations: `extern u32 cached_kn02_csr;`, `extern void init_kn02_irqs(int base);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/types.h>`.

### Integration Points
DEC board setup, TURBOchannel/IOASIC probing, RTC, serial, Ethernet, SCSI, framebuffer, HALT, LED, and bus-error paths use these values to map hardware and dispatch interrupts. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Primary risks are fixed hardware ABI drift, misrouted cascaded interrupts, stale cached CSR shadows, and incorrect acknowledgement of memory or I/O bus errors. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02ba.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02ba.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02ba.h` DECstation platform hardware contract for kn02ba.h: board slot offsets, interrupt input numbering, CSR/error/status bits, and where present bus-error or IRQ setup declarations. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 63 lines / 2097 bytes. macros/constants: `__ASM_MIPS_DEC_KN02BA_H`, `KN02BA_CPU_INR_HALT`, `KN02BA_CPU_INR_CASCADE`, `KN02BA_CPU_INR_TC2`, `KN02BA_CPU_INR_TC1`, `KN02BA_CPU_INR_TC0`, `KN02BA_IO_INR_RES_15`, `KN02BA_IO_INR_NVRAM`, `KN02BA_IO_INR_RES_13`, `KN02BA_IO_INR_BUS`, `KN02BA_IO_INR_RES_11`, `KN02BA_IO_INR_NRMOD`, `KN02BA_IO_INR_ASC`, `KN02BA_IO_INR_LANCE`, `KN02BA_IO_INR_SCC1`, `KN02BA_IO_INR_SCC0`, `KN02BA_IO_INR_RTC`, `KN02BA_IO_INR_PSU`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/dec/kn02xa.h>		/* For common definitions. */`.

### Integration Points
DEC board setup, TURBOchannel/IOASIC probing, RTC, serial, Ethernet, SCSI, framebuffer, HALT, LED, and bus-error paths use these values to map hardware and dispatch interrupts. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Primary risks are fixed hardware ABI drift, misrouted cascaded interrupts, stale cached CSR shadows, and incorrect acknowledgement of memory or I/O bus errors. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02ba.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02ca.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02ca.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02ca.h` DECstation platform hardware contract for kn02ca.h: board slot offsets, interrupt input numbering, CSR/error/status bits, and where present bus-error or IRQ setup declarations. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 75 lines / 2869 bytes. macros/constants: `__ASM_MIPS_DEC_KN02CA_H`, `KN02CA_CPU_INR_HALT`, `KN02CA_CPU_INR_CASCADE`, `KN02CA_CPU_INR_BUS`, `KN02CA_CPU_INR_RTC`, `KN02CA_CPU_INR_TIMER`, `KN02CA_IO_INR_FLOPPY`, `KN02CA_IO_INR_NVRAM`, `KN02CA_IO_INR_POWERON`, `KN02CA_IO_INR_TC0`, `KN02CA_IO_INR_TIMER`, `KN02CA_IO_INR_ISDN`, `KN02CA_IO_INR_NRMOD`, `KN02CA_IO_INR_ASC`, `KN02CA_IO_INR_LANCE`, `KN02CA_IO_INR_HDFLOPPY`, `KN02CA_IO_INR_SCC0`, `KN02CA_IO_INR_TC1`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/dec/kn02xa.h>		/* For common definitions. */`.

### Integration Points
DEC board setup, TURBOchannel/IOASIC probing, RTC, serial, Ethernet, SCSI, framebuffer, HALT, LED, and bus-error paths use these values to map hardware and dispatch interrupts. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Primary risks are fixed hardware ABI drift, misrouted cascaded interrupts, stale cached CSR shadows, and incorrect acknowledgement of memory or I/O bus errors. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02ca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02xa.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02xa.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02xa.h` DECstation platform hardware contract for kn02xa.h: board slot offsets, interrupt input numbering, CSR/error/status bits, and where present bus-error or IRQ setup declarations. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 84 lines / 2904 bytes. macros/constants: `__ASM_MIPS_DEC_KN02XA_H`, `KN02XA_SLOT_BASE`, `KN02XA_MER`, `KN02XA_MSR`, `KN02XA_MEM_CONF`, `KN02XA_EAR`, `KN02XA_BOOT0`, `KN02XA_MEM_INTR`, `KN02XA_MER_RES_28`, `KN02XA_MER_RES_17`, `KN02XA_MER_PAGERR`, `KN02XA_MER_TRANSERR`, `KN02XA_MER_PARDIS`, `KN02XA_MER_SIZE`, `KN02XA_MER_RES_12`, `KN02XA_MER_BYTERR`, `KN02XA_MER_BYTERR_3`, `KN02XA_MER_BYTERR_2`; types/functions/declarations: `struct pt_regs;`, `extern void dec_kn02xa_be_init(void);`, `extern int dec_kn02xa_be_handler(struct pt_regs *regs, int is_fixup);`, `extern irqreturn_t dec_kn02xa_be_interrupt(int irq, void *dev_id);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/dec/ioasic_addrs.h>`, `<linux/interrupt.h>`.

### Integration Points
DEC board setup, TURBOchannel/IOASIC probing, RTC, serial, Ethernet, SCSI, framebuffer, HALT, LED, and bus-error paths use these values to map hardware and dispatch interrupts. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Primary risks are fixed hardware ABI drift, misrouted cascaded interrupts, stale cached CSR shadows, and incorrect acknowledgement of memory or I/O bus errors. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn02xa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn03.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn03.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn03.h` DECstation platform hardware contract for kn03.h: board slot offsets, interrupt input numbering, CSR/error/status bits, and where present bus-error or IRQ setup declarations. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 74 lines / 2785 bytes. macros/constants: `__ASM_MIPS_DEC_KN03_H`, `KN03_SLOT_BASE`, `KN03_CPU_INR_HALT`, `KN03_CPU_INR_BUS`, `KN03_CPU_INR_RES_4`, `KN03_CPU_INR_RTC`, `KN03_CPU_INR_CASCADE`, `KN03_IO_INR_3MAXP`, `KN03_IO_INR_NVRAM`, `KN03_IO_INR_TC2`, `KN03_IO_INR_TC1`, `KN03_IO_INR_TC0`, `KN03_IO_INR_NRMOD`, `KN03_IO_INR_ASC`, `KN03_IO_INR_LANCE`, `KN03_IO_INR_SCC1`, `KN03_IO_INR_SCC0`, `KN03_IO_INR_RTC`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/dec/ecc.h>`, `<asm/dec/ioasic_addrs.h>`.

### Integration Points
DEC board setup, TURBOchannel/IOASIC probing, RTC, serial, Ethernet, SCSI, framebuffer, HALT, LED, and bus-error paths use these values to map hardware and dispatch interrupts. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Primary risks are fixed hardware ABI drift, misrouted cascaded interrupts, stale cached CSR shadows, and incorrect acknowledgement of memory or I/O bus errors. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn03.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn05.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn05.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn05.h` DECstation platform hardware contract for kn05.h: board slot offsets, interrupt input numbering, CSR/error/status bits, and where present bus-error or IRQ setup declarations. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 81 lines / 3232 bytes. macros/constants: `__ASM_MIPS_DEC_KN05_H`, `KN4K_SLOT_BASE`, `KN4K_MB_ROM`, `KN4K_IOCTL`, `KN4K_ESAR`, `KN4K_LANCE`, `KN4K_MB_INT`, `KN4K_MB_EA`, `KN4K_MB_EC`, `KN4K_MB_CSR`, `KN4K_RES_08`, `KN4K_RES_09`, `KN4K_RES_10`, `KN4K_RES_11`, `KN4K_SCSI`, `KN4K_RES_13`, `KN4K_RES_14`, `KN4K_RES_15`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/dec/ioasic_addrs.h>`.

### Integration Points
DEC board setup, TURBOchannel/IOASIC probing, RTC, serial, Ethernet, SCSI, framebuffer, HALT, LED, and bus-error paths use these values to map hardware and dispatch interrupts. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Primary risks are fixed hardware ABI drift, misrouted cascaded interrupts, stale cached CSR shadows, and incorrect acknowledgement of memory or I/O bus errors. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn05.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn230.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn230.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn230.h` DECstation platform hardware contract for kn230.h: board slot offsets, interrupt input numbering, CSR/error/status bits, and where present bus-error or IRQ setup declarations. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 22 lines / 649 bytes. macros/constants: `__ASM_MIPS_DEC_KN230_H`, `KN230_CPU_INR_HALT`, `KN230_CPU_INR_BUS`, `KN230_CPU_INR_RTC`, `KN230_CPU_INR_SII`, `KN230_CPU_INR_LANCE`, `KN230_CPU_INR_DZ11`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
DEC board setup, TURBOchannel/IOASIC probing, RTC, serial, Ethernet, SCSI, framebuffer, HALT, LED, and bus-error paths use these values to map hardware and dispatch interrupts. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Primary risks are fixed hardware ABI drift, misrouted cascaded interrupts, stale cached CSR shadows, and incorrect acknowledgement of memory or I/O bus errors. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/kn230.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/machtype.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/machtype.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/machtype.h` DECstation platform hardware contract for machtype.h: board slot offsets, interrupt input numbering, CSR/error/status bits, and where present bus-error or IRQ setup declarations. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 27 lines / 750 bytes. macros/constants: `__ASM_DEC_MACHTYPE_H`, `TURBOCHANNEL`, `IOASIC`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/bootinfo.h>`.

### Integration Points
DEC board setup, TURBOchannel/IOASIC probing, RTC, serial, Ethernet, SCSI, framebuffer, HALT, LED, and bus-error paths use these values to map hardware and dispatch interrupts. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Primary risks are fixed hardware ABI drift, misrouted cascaded interrupts, stale cached CSR shadows, and incorrect acknowledgement of memory or I/O bus errors. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/machtype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/prom.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/prom.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/prom.h` DECstation platform hardware contract for prom.h: board slot offsets, interrupt input numbering, CSR/error/status bits, and where present bus-error or IRQ setup declarations. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 164 lines / 5207 bytes. macros/constants: `_ASM_DEC_PROM_H`, `VEC_RESET`, `PMAX_PROM_ENTRY`, `PMAX_PROM_HALT`, `PMAX_PROM_AUTOBOOT`, `PMAX_PROM_OPEN`, `PMAX_PROM_READ`, `PMAX_PROM_CLOSE`, `PMAX_PROM_LSEEK`, `PMAX_PROM_GETCHAR`, `PMAX_PROM_PUTCHAR`, `PMAX_PROM_GETS`, `PMAX_PROM_PRINTF`, `PMAX_PROM_GETENV`, `REX_PROM_MAGIC`, `REX_PROM_GETBITMAP`, `REX_PROM_GETCHAR`, `REX_PROM_GETENV`; types/functions/declarations: `static inline bool prom_is_rex(u32 magic)`, `typedef struct {`, `extern int (*__rex_bootinit)(void);`, `extern int (*__rex_bootread)(void);`, `extern int (*__rex_getbitmap)(memmap *);`, `extern unsigned long *(*__rex_slot_address)(int);`, `extern void *(*__rex_gettcinfo)(void);`, `extern int (*__rex_getsysid)(void);`, `extern void (*__rex_clear_cache)(void);`, `extern int (*__prom_getchar)(void);`, `extern char *(*__prom_getenv)(char *);`, `extern int (*__prom_printf)(char *, ...);`, `extern int (*__pmax_open)(char*, int);`, `extern int (*__pmax_lseek)(int, long, int);`, `extern int (*__pmax_read)(int, void *, int);`, `extern int (*__pmax_close)(int);`, `extern void prom_meminit(u32);`, `extern void prom_identify_arch(u32);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/types.h>`, `<asm/addrspace.h>`.

### Integration Points
DEC board setup, TURBOchannel/IOASIC probing, RTC, serial, Ethernet, SCSI, framebuffer, HALT, LED, and bus-error paths use these values to map hardware and dispatch interrupts. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Primary risks are fixed hardware ABI drift, misrouted cascaded interrupts, stale cached CSR shadows, and incorrect acknowledgement of memory or I/O bus errors. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/prom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/system.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/system.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/system.h` DECstation platform hardware contract for system.h: board slot offsets, interrupt input numbering, CSR/error/status bits, and where present bus-error or IRQ setup declarations. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 15 lines / 347 bytes. macros/constants: `__ASM_DEC_SYSTEM_H`; types/functions/declarations: `extern unsigned long dec_kn_slot_base, dec_kn_slot_size;`, `extern int dec_tc_bus;`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
DEC board setup, TURBOchannel/IOASIC probing, RTC, serial, Ethernet, SCSI, framebuffer, HALT, LED, and bus-error paths use these values to map hardware and dispatch interrupts. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Primary risks are fixed hardware ABI drift, misrouted cascaded interrupts, stale cached CSR shadows, and incorrect acknowledgement of memory or I/O bus errors. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/system.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/delay.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/delay.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/delay.h` MIPS calibrated delay API for busy-waiting at loop, nanosecond, and microsecond granularity. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 32 lines / 841 bytes. macros/constants: `_ASM_DELAY_H`, `ndelay`, `udelay`, `MAX_UDELAY_MS`, `MAX_UDELAY_MS`, `MAX_UDELAY_MS`; types/functions/declarations: `extern void __delay(unsigned long loops);`, `extern void __ndelay(unsigned long ns);`, `extern void __udelay(unsigned long us);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/param.h>`.

### Integration Points
Used by drivers and early platform code for reset and MMIO timing. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Overflow or bad calibration breaks hardware timing and can hang boot or devices. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/div64.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/div64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/div64.h` MIPS optimized 64-by-32 division helper layered under generic div64 support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 91 lines / 2223 bytes. macros/constants: `__ASM_DIV64_H`, `do_div64_32`, `__div64_32`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/bitsperlong.h>`, `<asm-generic/div64.h>`.

### Integration Points
Used by time, block, network, and filesystem arithmetic on 32-bit MIPS. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Inline assembly carry/remainder bugs silently corrupt arithmetic. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/div64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dma-direct.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dma-direct.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dma-direct.h` DMA mapping and legacy DMA programming contract, including address translation, controller registers, cache maintenance, or Jazz VDMA APIs. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 8 lines / 255 bytes. macros/constants: `_MIPS_DMA_DIRECT_H`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by block, network, floppy, SCSI, ISA/Jazz devices, and noncoherent cache paths. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong DMA address translation, cache flushing, locking, or channel programming can corrupt memory and page-cache data. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dma-direct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dma-mapping.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dma-mapping.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dma-mapping.h` DMA mapping and legacy DMA programming contract, including address translation, controller registers, cache maintenance, or Jazz VDMA APIs. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 18 lines / 349 bytes. macros/constants: `_ASM_DMA_MAPPING_H`; types/functions/declarations: `extern const struct dma_map_ops jazz_dma_ops;`, `static inline const struct dma_map_ops *get_arch_dma_ops(void)`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/swiotlb.h>`.

### Integration Points
Used by block, network, floppy, SCSI, ISA/Jazz devices, and noncoherent cache paths. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong DMA address translation, cache flushing, locking, or channel programming can corrupt memory and page-cache data. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dma-mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dma.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dma.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dma.h` DMA mapping and legacy DMA programming contract, including address translation, controller registers, cache maintenance, or Jazz VDMA APIs. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 310 lines / 10047 bytes. macros/constants: `_ASM_DMA_H`, `dma_outb`, `dma_outb`, `dma_inb`, `MAX_DMA_CHANNELS`, `MAX_DMA_ADDRESS`, `MAX_DMA_ADDRESS`, `MAX_DMA_PFN`, `MAX_DMA32_PFN`, `IO_DMA1_BASE`, `IO_DMA2_BASE`, `DMA1_CMD_REG`, `DMA1_STAT_REG`, `DMA1_REQ_REG`, `DMA1_MASK_REG`, `DMA1_MODE_REG`, `DMA1_CLEAR_FF_REG`, `DMA1_TEMP_REG`; types/functions/declarations: `extern spinlock_t  dma_spin_lock;`, `extern int request_dma(unsigned int dmanr, const char * device_id);	/* reserve a DMA channel */`, `extern void free_dma(unsigned int dmanr);	/* release it again */`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/io.h>			/* need byte IO */`, `<linux/spinlock.h>		/* And spinlocks */`, `<linux/delay.h>`.

### Integration Points
Used by block, network, floppy, SCSI, ISA/Jazz devices, and noncoherent cache paths. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong DMA address translation, cache flushing, locking, or channel programming can corrupt memory and page-cache data. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dmi.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dmi.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dmi.h` DMI/SMBIOS remap, allocation, and scan-base glue for MIPS firmware tables. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 20 lines / 547 bytes. macros/constants: `_ASM_DMI_H`, `dmi_early_remap`, `dmi_early_unmap`, `dmi_remap`, `dmi_unmap`, `dmi_alloc`, `SMBIOS_ENTRY_POINT_SCAN_START`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/io.h>`, `<linux/memblock.h>`.

### Integration Points
Used by generic DMI scanners during early and normal boot. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong mapping or scan base misses firmware data or reads invalid memory. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ds1287.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/ds1287.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/ds1287.h` DS1287 RTC timer/clockevent declarations for MIPS platforms. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 14 lines / 333 bytes. macros/constants: `__ASM_DS1287_H`; types/functions/declarations: `extern int ds1287_timer_state(void);`, `extern int ds1287_set_base_clock(unsigned int hz);`, `extern int ds1287_clockevent_init(int irq);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by DEC and other RTC-backed timer initialization. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong base clock or IRQ setup causes time drift and lost ticks. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ds1287.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dsemul.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dsemul.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dsemul.h` Branch delay-slot emulation API and cleanup/rollback hooks. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 115 lines / 3595 bytes. macros/constants: `__MIPS_ASM_DSEMUL_H__`, `BREAK_MATH`, `BD_EMUFRAME_NONE`; types/functions/declarations: `struct mm_struct;`, `struct pt_regs;`, `struct task_struct;`, `extern int mips_dsemul(struct pt_regs *regs, mips_instruction ir,`, `extern bool do_dsemulret(struct pt_regs *xcp);`, `static inline bool do_dsemulret(struct pt_regs *xcp)`, `extern bool dsemul_thread_cleanup(struct task_struct *tsk);`, `static inline bool dsemul_thread_cleanup(struct task_struct *tsk)`, `extern bool dsemul_thread_rollback(struct pt_regs *regs);`, `static inline bool dsemul_thread_rollback(struct pt_regs *regs)`, `extern void dsemul_mm_cleanup(struct mm_struct *mm);`, `static inline void dsemul_mm_cleanup(struct mm_struct *mm)`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/break.h>`, `<asm/inst.h>`.

### Integration Points
Used by trap, signal, FPU emulator, and MIPS R6 compatibility paths. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Bad emulation frames or cleanup leave user PC and signal state inconsistent. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dsemul.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dsp.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dsp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dsp.h` DSP ASE enable, save, restore, and register access helpers. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 81 lines / 1747 bytes. macros/constants: `_ASM_DSP_H`, `DSP_DEFAULT`, `DSP_MASK`, `__enable_dsp_hazard`, `__save_dsp`, `save_dsp`, `__restore_dsp`, `restore_dsp`, `__get_dsp_regs`; types/functions/declarations: `static inline void __init_dsp(void)`, `static inline void init_dsp(void)`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/cpu.h>`, `<asm/cpu-features.h>`, `<asm/hazards.h>`, `<asm/mipsregs.h>`.

### Integration Points
Used by context switch and user DSP ABI support. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Missing hazards or feature checks corrupt DSP state or execute unsupported instructions. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/edac.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/edac.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/edac.h` EDAC atomic memory scrub helper for MIPS ECC correction. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 38 lines / 839 bytes. macros/constants: `ASM_EDAC_H`; types/functions/declarations: `static inline void edac_atomic_scrub(void *va, u32 size)`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/compiler.h>`.

### Integration Points
Used by EDAC drivers to trigger writeback/correction without changing contents. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Alignment or inline-assembly mistakes can miss or corrupt memory. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/edac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/elf.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/elf.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/elf.h` MIPS ELF ABI, core-dump, process personality, relocation, auxv, FP/NAN ABI, and register-set contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 522 lines / 15585 bytes. macros/constants: `_ASM_ELF_H`, `EF_MIPS_ARCH_1`, `EF_MIPS_ARCH_2`, `EF_MIPS_ARCH_3`, `EF_MIPS_ARCH_4`, `EF_MIPS_ARCH_5`, `EF_MIPS_ARCH_32`, `EF_MIPS_ARCH_64`, `EF_MIPS_ARCH_32R2`, `EF_MIPS_ARCH_64R2`, `EF_MIPS_ABI_O32`, `EF_MIPS_ABI_O64`, `PT_MIPS_REGINFO`, `PT_MIPS_RTPROC`, `PT_MIPS_OPTIONS`, `PT_MIPS_ABIFLAGS`, `EF_MIPS_NOREORDER`, `EF_MIPS_PIC`; types/functions/declarations: `struct mips_elf_abiflags_v0 {`, `typedef unsigned long elf_greg_t;`, `typedef elf_greg_t elf_gregset_t[ELF_NGREG];`, `typedef double elf_fpreg_t;`, `typedef elf_fpreg_t elf_fpregset_t[ELF_NFPREG];`, `struct elfhdr *__h = (hdr);					\`, `struct elfhdr *__h = (hdr);					\`, `struct mips_abi;`, `extern struct mips_abi mips_abi;`, `extern struct mips_abi mips_abi_32;`, `extern struct mips_abi mips_abi_n32;`, `extern unsigned int elf_hwcap;`, `extern const char *__elf_platform;`, `extern const char *__elf_base_platform;`, `struct linux_binprm;`, `extern int arch_setup_additional_pages(struct linux_binprm *bprm,`, `struct arch_elf_state {`, `extern int arch_elf_pt_proc(void *ehdr, void *phdr, struct file *elf,`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/auxvec.h>`, `<linux/fs.h>`, `<linux/mm_types.h>`, `<uapi/linux/elf.h>`, `<asm/current.h>`, `<asm/hwcap.h>`.

### Integration Points
Used by exec, compat loading, vDSO auxv setup, core dumps, dynamic loaders, ptrace, and debuggers. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
ABI drift can reject valid binaries, run incompatible FP modes, or emit unreadable core files. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/elfcore-compat.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/elfcore-compat.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/elfcore-compat.h` MIPS ELF ABI, core-dump, process personality, relocation, auxv, FP/NAN ABI, and register-set contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 29 lines / 841 bytes. macros/constants: `_ASM_MIPS_ELFCORE_COMPAT_H`, `PRSTATUS_SIZE`, `SET_PR_FPVALID`; types/functions/declarations: `typedef elf_gregset_t compat_elf_gregset_t;`, `struct o32_elf_prstatus`, `struct compat_elf_prstatus_common	common;`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by exec, compat loading, vDSO auxv setup, core dumps, dynamic loaders, ptrace, and debuggers. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
ABI drift can reject valid binaries, run incompatible FP modes, or emit unreadable core files. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/elfcore-compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/errno.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/errno.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/errno.h` MIPS errno UAPI inclusion and maximum kernel errno value. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 17 lines / 429 bytes. macros/constants: `_ASM_ERRNO_H`, `EMAXERRNO`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<uapi/asm/errno.h>`.

### Integration Points
Used by syscall/error-pointer handling. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Changing the limit breaks error-pointer classification and ABI expectations. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/eva.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/eva.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/eva.h` Enhanced Virtual Addressing entry setup glue. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 43 lines / 798 bytes. macros/constants: `_ASM_EVA_H`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<kernel-entry-init.h>`.

### Integration Points
Used by early kernel entry and machine initialization for EVA address spaces. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong setup breaks overlapping user/kernel mapping assumptions. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/eva.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/exec.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/exec.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/exec.h` MIPS memory-management and process-execution glue for stack alignment, exception fixups, fixed mappings, highmem mappings, or hugepage PTEs. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 17 lines / 579 bytes. macros/constants: `_ASM_EXEC_H`; types/functions/declarations: `extern unsigned long arch_align_stack(unsigned long sp);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by exec, uaccess fault recovery, early ioremap/kmap, page cache, TLB flush, and hugetlb code. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong ordering, address geometry, or PTE layout can crash faults or leave stale translations. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/exec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/extable.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/extable.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/extable.h` MIPS memory-management and process-execution glue for stack alignment, exception fixups, fixed mappings, highmem mappings, or hugepage PTEs. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 14 lines / 241 bytes. macros/constants: `_ASM_EXTABLE_H`; types/functions/declarations: `struct exception_table_entry`, `struct pt_regs;`, `extern int fixup_exception(struct pt_regs *regs);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by exec, uaccess fault recovery, early ioremap/kmap, page cache, TLB flush, and hugetlb code. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong ordering, address geometry, or PTE layout can crash faults or leave stale translations. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fixmap.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/fixmap.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/fixmap.h` MIPS memory-management and process-execution glue for stack alignment, exception fixups, fixed mappings, highmem mappings, or hugepage PTEs. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 79 lines / 2221 bytes. macros/constants: `_ASM_FIXMAP_H`, `FIX_N_COLOURS`, `FIXADDR_SIZE`, `FIXADDR_START`; types/functions/declarations: `enum fixed_addresses {`, `extern void fixrange_init(unsigned long start, unsigned long end,`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/page.h>`, `<spaces.h>`, `<linux/threads.h>`, `<asm/kmap_size.h>`, `<asm-generic/fixmap.h>`.

### Integration Points
Used by exec, uaccess fault recovery, early ioremap/kmap, page cache, TLB flush, and hugetlb code. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong ordering, address geometry, or PTE layout can crash faults or leave stale translations. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/floppy.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/floppy.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/floppy.h` DMA mapping and legacy DMA programming contract, including address translation, controller registers, cache maintenance, or Jazz VDMA APIs. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 41 lines / 947 bytes. macros/constants: `_ASM_FLOPPY_H`, `MAX_BUFFER_SECTORS`, `FLOPPY0_TYPE`, `FLOPPY1_TYPE`, `FDC1`, `N_FDC`, `N_DRIVE`, `EXTRA_FLOPPY_PARAMS`; types/functions/declarations: `static inline void fd_cacheflush(char * addr, long size)`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/io.h>`, `<floppy.h>`.

### Integration Points
Used by block, network, floppy, SCSI, ISA/Jazz devices, and noncoherent cache paths. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong DMA address translation, cache flushing, locking, or channel programming can corrupt memory and page-cache data. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/floppy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fpregdef.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/fpregdef.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/fpregdef.h` Assembler register-name aliases for MIPS FPU ABI variants. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 99 lines / 2151 bytes. macros/constants: `_ASM_FPREGDEF_H`, `fv0`, `fv0f`, `fv1`, `fv1f`, `fa0`, `fa0f`, `fa1`, `fa1f`, `ft0`, `ft0f`, `ft1`, `ft1f`, `ft2`, `ft2f`, `ft3`, `ft3f`, `ft4`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/sgidefs.h>`.

### Integration Points
Used by low-level FPU assembly and ABI-specific save/restore code. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong aliases corrupt FP argument, return, or callee-saved registers. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fpregdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fpu.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/fpu.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/fpu.h` MIPS FPU ownership, context, emulator, FCSR, and feature-gated FP support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 343 lines / 7567 bytes. macros/constants: `_ASM_FPU_H`, `FPU_FR_MASK`, `__disable_fpu`, `clear_fpu_owner`; types/functions/declarations: `enum fpu_mode {`, `extern void _save_fp(struct task_struct *);`, `extern void _restore_fp(struct task_struct *);`, `static inline int __enable_fpu(enum fpu_mode mode)`, `static inline int __is_fpu_owner(void)`, `static inline int is_fpu_owner(void)`, `static inline int __own_fpu(void)`, `enum fpu_mode mode;`, `static inline int own_fpu_inatomic(int restore)`, `static inline int own_fpu(int restore)`, `static inline void lose_fpu_inatomic(int save, struct task_struct *tsk)`, `static inline void lose_fpu(int save)`, `static inline bool init_fp_ctx(struct task_struct *target)`, `static inline void save_fp(struct task_struct *tsk)`, `static inline void restore_fp(struct task_struct *tsk)`, `static inline union fpureg *get_fpu_regs(struct task_struct *tsk)`, `static inline int __enable_fpu(enum fpu_mode mode)`, `static inline void __disable_fpu(void)`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/sched.h>`, `<linux/sched/task_stack.h>`, `<linux/ptrace.h>`, `<linux/thread_info.h>`, `<linux/bitops.h>`, `<asm/mipsregs.h>`, `<asm/cpu.h>`, `<asm/cpu-features.h>`.

### Integration Points
Used by context switch, traps, KVM, signal/ptrace, and soft-FPU emulation. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Lazy ownership, FR mode, exception, or emulation bugs leak or corrupt userspace FP state. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fpu_emulator.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/fpu_emulator.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/fpu_emulator.h` MIPS FPU ownership, context, emulator, FCSR, and feature-gated FP support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 187 lines / 4844 bytes. macros/constants: `_ASM_FPU_EMULATOR_H`, `MIPS_FPU_EMU_INC_STATS`, `MIPS_FPU_EMU_INC_STATS`; types/functions/declarations: `struct mips_fpu_emulator_stats {`, `extern int fpu_emulator_cop1Handler(struct pt_regs *xcp,`, `struct mips_fpu_struct *ctx, int has_fpu,`, `struct task_struct *tsk);`, `static inline unsigned long mask_fcr31_x(unsigned long fcr31)`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/sched.h>`, `<asm/dsemul.h>`, `<asm/thread_info.h>`, `<asm/inst.h>`, `<asm/local.h>`, `<asm/processor.h>`.

### Integration Points
Used by context switch, traps, KVM, signal/ptrace, and soft-FPU emulation. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Lazy ownership, FR mode, exception, or emulation bugs leak or corrupt userspace FP state. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fpu_emulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ftrace.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/ftrace.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/ftrace.h` MIPS ftrace call-site metadata, safe text/stack access, and syscall symbol matching. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 110 lines / 2771 bytes. macros/constants: `_ASM_MIPS_FTRACE_H`, `MCOUNT_ADDR`, `MCOUNT_INSN_SIZE`, `mcount`, `safe_load`, `safe_store`, `safe_load_code`, `safe_store_code`, `safe_load_stack`, `safe_store_stack`, `ARCH_HAS_SYSCALL_MATCH_SYM_NAME`; types/functions/declarations: `extern void _mcount(void);`, `static inline unsigned long ftrace_call_adjust(unsigned long addr)`, `struct dyn_arch_ftrace {`, `static inline bool arch_syscall_match_sym_name(const char *sym,`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by dynamic tracing and runtime text patching. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Bad instruction sizing or safe access can patch the wrong code and crash. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/futex.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/futex.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/futex.h` MIPS futex atomic user-memory operations with LL/SC, barriers, exception fixups, and EVA support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 210 lines / 5557 bytes. macros/constants: `_ASM_FUTEX_H`, `arch_futex_atomic_op_inuser`, `futex_atomic_cmpxchg_inatomic`, `__futex_atomic_op`; types/functions/declarations: `static inline int`, `static inline int`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/futex.h>`, `<linux/uaccess.h>`, `<asm/asm-eva.h>`, `<asm/barrier.h>`, `<asm/compiler.h>`, `<asm/errno.h>`, `<asm/sync.h>`, `<asm-generic/futex.h>`.

### Integration Points
Used by futex syscalls and all userspace synchronization stacks. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Atomicity, barrier, or fault-fixup bugs cause deadlocks or memory corruption. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/arc/hinv.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/arc/hinv.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/arc/hinv.h` ARC/ARCS firmware type and hardware inventory ABI definitions. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 176 lines / 3335 bytes. macros/constants: `_ASM_ARC_HINV_H`, `NULL`, `SGI_ARCS_VERS`, `SGI_ARCS_REV`, `SGI_ARCS_VERS`, `SGI_ARCS_REV`; types/functions/declarations: `typedef enum configclass {`, `typedef enum configtype {`, `typedef enum {`, `struct {`, `typedef struct {`, `struct cfgdata {`, `typedef struct {`, `typedef enum memorytype {`, `typedef struct {`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/sgidefs.h>`, `<asm/fw/arc/types.h>`.

### Integration Points
Used by SGI firmware discovery and early device/memory enumeration. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong type widths or struct layout break firmware inventory parsing. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/arc/hinv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/arc/types.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/arc/types.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/arc/types.h` ARC/ARCS firmware type and hardware inventory ABI definitions. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 86 lines / 2280 bytes. macros/constants: `_ASM_ARC_TYPES_H`; types/functions/declarations: `typedef char		CHAR;`, `typedef short		SHORT;`, `typedef long		LARGE_INTEGER __attribute__ ((__mode__ (__DI__)));`, `typedef long		LONG __attribute__ ((__mode__ (__SI__)));`, `typedef unsigned char	UCHAR;`, `typedef unsigned short	USHORT;`, `typedef unsigned long	ULONG __attribute__ ((__mode__ (__SI__)));`, `typedef void		VOID;`, `typedef LONG		_PCHAR;`, `typedef LONG		_PSHORT;`, `typedef LONG		_PLARGE_INTEGER;`, `typedef LONG		_PLONG;`, `typedef LONG		_PUCHAR;`, `typedef LONG		_PUSHORT;`, `typedef LONG		_PULONG;`, `typedef LONG		_PVOID;`, `typedef char		CHAR;`, `typedef short		SHORT;`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by SGI firmware discovery and early device/memory enumeration. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong type widths or struct layout break firmware inventory parsing. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/arc/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/cfe/cfe_api.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/cfe/cfe_api.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/cfe/cfe_api.h` MIPS firmware interface declarations for CFE or generic fw argv/env/cmdline/memory/console handling. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 108 lines / 3199 bytes. macros/constants: `CFE_API_H`, `CFE_EPTSEAL`, `CFE_MI_RESERVED`, `CFE_MI_AVAILABLE`, `CFE_FLG_WARMSTART`, `CFE_FLG_FULL_ARENA`, `CFE_FLG_ENV_PERMANENT`, `CFE_CPU_CMD_START`, `CFE_CPU_CMD_STOP`, `CFE_STDHANDLE_CONSOLE`, `CFE_DEV_NETWORK`, `CFE_DEV_DISK`, `CFE_DEV_FLASH`, `CFE_DEV_SERIAL`, `CFE_DEV_CPU`, `CFE_DEV_NVRAM`, `CFE_DEV_CLOCK`, `CFE_DEV_OTHER`; types/functions/declarations: `typedef struct {`, `extern unsigned long cfe_seal;`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/types.h>`, `<linux/string.h>`.

### Integration Points
Used during early boot, memory discovery, environment parsing, console, device and CPU firmware services. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Pointer-width, handle, or error-code mistakes hang early boot or misconfigure memory. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/cfe/cfe_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/cfe/cfe_error.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/cfe/cfe_error.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/cfe/cfe_error.h` MIPS firmware interface declarations for CFE or generic fw argv/env/cmdline/memory/console handling. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 67 lines / 1493 bytes. macros/constants: `CFE_OK`, `CFE_ERR`, `CFE_ERR_INV_COMMAND`, `CFE_ERR_EOF`, `CFE_ERR_IOERR`, `CFE_ERR_NOMEM`, `CFE_ERR_DEVNOTFOUND`, `CFE_ERR_DEVOPEN`, `CFE_ERR_INV_PARAM`, `CFE_ERR_ENVNOTFOUND`, `CFE_ERR_ENVREADONLY`, `CFE_ERR_NOTELF`, `CFE_ERR_NOT32BIT`, `CFE_ERR_WRONGENDIAN`, `CFE_ERR_BADELFVERS`, `CFE_ERR_NOTMIPS`, `CFE_ERR_BADELFFMT`, `CFE_ERR_BADADDR`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used during early boot, memory discovery, environment parsing, console, device and CPU firmware services. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Pointer-width, handle, or error-code mistakes hang early boot or misconfigure memory. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/cfe/cfe_error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/fw.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/fw.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/fw.h` MIPS firmware interface declarations for CFE or generic fw argv/env/cmdline/memory/console handling. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 31 lines / 898 bytes. macros/constants: `__ASM_FW_H_`, `fw_argv`, `fw_envp`; types/functions/declarations: `extern int fw_argc;`, `extern int *_fw_argv;`, `extern int *_fw_envp;`, `extern void fw_init_cmdline(void);`, `extern char *fw_getcmdline(void);`, `extern void fw_meminit(void);`, `extern char *fw_getenv(char *name);`, `extern unsigned long fw_getenvl(char *name);`, `extern void fw_init_early_console(void);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/bootinfo.h>	/* For cleaner code... */`.

### Integration Points
Used during early boot, memory discovery, environment parsing, console, device and CPU firmware services. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Pointer-width, handle, or error-code mistakes hang early boot or misconfigure memory. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/fw/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ginvt.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/ginvt.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/ginvt.h` GINVT global invalidation instruction wrappers with assembler fallback macros. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 59 lines / 1159 bytes. macros/constants: `__MIPS_ASM_GINVT_H__`; types/functions/declarations: `enum ginvt_type {`, `static inline void ginvt_full(void)`, `static inline void ginvt_va(unsigned long addr)`, `static inline void ginvt_mmid(void)`, `static inline void ginvt_va_mmid(unsigned long addr)`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/mipsregs.h>`.

### Integration Points
Used by MMU/TLB/cache invalidation paths on supporting CPUs. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong invalidation type or VA masking leaves stale translations. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ginvt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/gio_device.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/gio_device.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/gio_device.h` SGI GIO Linux device/driver model structures and registration APIs. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 53 lines / 1411 bytes. macros/constants: `to_gio_device`, `to_gio_driver`, `gio_get_drvdata`, `gio_set_drvdata`; types/functions/declarations: `struct gio_device_id {`, `struct gio_device {`, `struct device	dev;`, `struct resource resource;`, `struct gio_device_id id;`, `struct gio_driver {`, `struct module *owner;`, `struct device_driver driver;`, `extern struct gio_device *gio_dev_get(struct gio_device *);`, `extern void gio_dev_put(struct gio_device *);`, `extern int gio_device_register(struct gio_device *);`, `extern void gio_device_unregister(struct gio_device *);`, `extern void gio_release_dev(struct device *);`, `static inline void gio_device_free(struct gio_device *dev)`, `extern int gio_register_driver(struct gio_driver *);`, `extern void gio_unregister_driver(struct gio_driver *);`, `extern void gio_set_master(struct gio_device *);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/device.h>`, `<linux/mod_devicetable.h>`.

### Integration Points
Used by GIO bus enumeration and expansion drivers. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Lifetime, resource, or IRQ ownership bugs cause driver binding failures or use-after-free. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/gio_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/gt64120.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/gt64120.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/gt64120.h` Galileo GT64120/GT641xx controller register, endian MMIO, timer, PCI, DMA, and IRQ contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 566 lines / 19218 bytes. macros/constants: `_ASM_GT64120_H`, `MSK`, `GT_CPU_OFS`, `GT_MULTI_OFS`, `GT_SCS10LD_OFS`, `GT_SCS10HD_OFS`, `GT_SCS32LD_OFS`, `GT_SCS32HD_OFS`, `GT_CS20LD_OFS`, `GT_CS20HD_OFS`, `GT_CS3BOOTLD_OFS`, `GT_CS3BOOTHD_OFS`, `GT_PCI0IOLD_OFS`, `GT_PCI0IOHD_OFS`, `GT_PCI0M0LD_OFS`, `GT_PCI0M0HD_OFS`, `GT_ISD_OFS`, `GT_PCI0M1LD_OFS`; types/functions/declarations: `extern void gt641xx_set_base_clock(unsigned int clock);`, `extern int gt641xx_timer0_state(void);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/addrspace.h>`, `<asm/byteorder.h>`, `<mach-gt64120.h>`.

### Integration Points
Used by Malta/Galileo board setup, PCI host bridge, timers, DMA, and interrupt dispatch. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong endian, window, or interrupt masks break PCI, timers, DMA, and memory decode. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/gt64120.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/hardirq.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/hardirq.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/hardirq.h` MIPS interrupt, IRQ-controller, IRQ-stack, IRQ-register, CPU idle, or local IRQ flag support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 18 lines / 544 bytes. macros/constants: `_ASM_HARDIRQ_H`, `ack_bad_irq`; types/functions/declarations: `extern void ack_bad_irq(unsigned int irq);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm-generic/hardirq.h>`.

### Integration Points
Used by interrupt entry/exit, irqdomains, PIC/CPU irqchips, timers, scheduler idle, tracing, and diagnostics. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Missing hazards, wrong stack bounds, bad IRQ numbering, or failed acknowledgements can create lost interrupts or storms. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/hazards.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/hazards.h

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/hazards.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/highmem.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/highmem.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/highmem.h` MIPS memory-management and process-execution glue for stack alignment, exception fixups, fixed mappings, highmem mappings, or hugepage PTEs. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 60 lines / 1741 bytes. macros/constants: `_ASM_HIGHMEM_H`, `LAST_PKMAP`, `LAST_PKMAP`, `LAST_PKMAP_MASK`, `PKMAP_NR`, `PKMAP_ADDR`, `ARCH_HAS_KMAP_FLUSH_TLB`, `flush_cache_kmaps`, `arch_kmap_local_set_pte`, `arch_kmap_local_post_map`, `arch_kmap_local_post_unmap`; types/functions/declarations: `extern unsigned long highstart_pfn, highend_pfn;`, `extern pte_t *pkmap_page_table;`, `extern void kmap_flush_tlb(unsigned long addr);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/bug.h>`, `<linux/interrupt.h>`, `<linux/uaccess.h>`, `<asm/cpu-features.h>`, `<asm/kmap_size.h>`.

### Integration Points
Used by exec, uaccess fault recovery, early ioremap/kmap, page cache, TLB flush, and hugetlb code. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong ordering, address geometry, or PTE layout can crash faults or leave stale translations. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/highmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/hpet.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/hpet.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/hpet.h` MIPS architecture include contract for platform or subsystem code. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 74 lines / 1974 bytes. macros/constants: `_ASM_HPET_H`, `HPET_MMAP_SIZE`, `HPET_ID`, `HPET_PERIOD`, `HPET_CFG`, `HPET_STATUS`, `HPET_COUNTER`, `HPET_Tn_CFG`, `HPET_Tn_CMP`, `HPET_Tn_ROUTE`, `HPET_T0_IRS`, `HPET_T1_IRS`, `HPET_T3_IRS`, `HPET_T0_CFG`, `HPET_T0_CMP`, `HPET_T0_ROUTE`, `HPET_T1_CFG`, `HPET_T1_CMP`; types/functions/declarations: `extern void __init setup_hpet_timer(void);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by including MIPS kernel code; Ceph relevance is indirect through kernel services. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
ABI drift or feature-guard mistakes break builds or runtime behavior. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/hpet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/hugetlb.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/hugetlb.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/hugetlb.h` MIPS memory-management and process-execution glue for stack alignment, exception fixups, fixed mappings, highmem mappings, or hugepage PTEs. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 72 lines / 1849 bytes. macros/constants: `__ASM_HUGETLB_H`, `__HAVE_ARCH_HUGE_PTEP_GET_AND_CLEAR`, `__HAVE_ARCH_HUGE_PTEP_CLEAR_FLUSH`, `__HAVE_ARCH_HUGE_PTE_NONE`, `__HAVE_ARCH_HUGE_PTEP_SET_ACCESS_FLAGS`; types/functions/declarations: `static inline pte_t huge_ptep_get_and_clear(struct mm_struct *mm,`, `static inline pte_t huge_ptep_clear_flush(struct vm_area_struct *vma,`, `static inline int huge_pte_none(pte_t pte)`, `static inline int huge_ptep_set_access_flags(struct vm_area_struct *vma,`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/page.h>`, `<asm-generic/hugetlb.h>`.

### Integration Points
Used by exec, uaccess fault recovery, early ioremap/kmap, page cache, TLB flush, and hugetlb code. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong ordering, address geometry, or PTE layout can crash faults or leave stale translations. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/hugetlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/hw_irq.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/hw_irq.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/hw_irq.h` MIPS interrupt, IRQ-controller, IRQ-stack, IRQ-register, CPU idle, or local IRQ flag support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 20 lines / 475 bytes. macros/constants: `__ASM_HW_IRQ_H`; types/functions/declarations: `extern atomic_t irq_err_count;`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/atomic.h>`.

### Integration Points
Used by interrupt entry/exit, irqdomains, PIC/CPU irqchips, timers, scheduler idle, tracing, and diagnostics. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Missing hazards, wrong stack bounds, bad IRQ numbering, or failed acknowledgements can create lost interrupts or storms. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/hw_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/i8259.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/i8259.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/i8259.h` MIPS interrupt, IRQ-controller, IRQ-stack, IRQ-register, CPU idle, or local IRQ flag support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 93 lines / 2440 bytes. macros/constants: `_ASM_I8259_H`, `PIC_MASTER_CMD`, `PIC_MASTER_IMR`, `PIC_MASTER_ISR`, `PIC_MASTER_POLL`, `PIC_MASTER_OCW3`, `PIC_SLAVE_CMD`, `PIC_SLAVE_IMR`, `PIC_CASCADE_IR`, `MASTER_ICW4_DEFAULT`, `SLAVE_ICW4_DEFAULT`, `PIC_ICW4_AEOI`; types/functions/declarations: `extern raw_spinlock_t i8259A_lock;`, `extern void make_8259A_irq(unsigned int irq);`, `extern void init_i8259_irqs(void);`, `extern struct irq_domain *__init_i8259_irqs(struct device_node *node);`, `extern void i8259_set_poll(int (*poll)(void));`, `static inline int i8259_irq(void)`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/compiler.h>`, `<linux/spinlock.h>`, `<asm/io.h>`, `<irq.h>`.

### Integration Points
Used by interrupt entry/exit, irqdomains, PIC/CPU irqchips, timers, scheduler idle, tracing, and diagnostics. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Missing hazards, wrong stack bounds, bad IRQ numbering, or failed acknowledgements can create lost interrupts or storms. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/i8259.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/idle.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/idle.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/idle.h` MIPS interrupt, IRQ-controller, IRQ-stack, IRQ-register, CPU idle, or local IRQ flag support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 31 lines / 697 bytes. macros/constants: `__ASM_IDLE_H`, `MIPS_CPUIDLE_WAIT_STATE`; types/functions/declarations: `extern void (*cpu_wait)(void);`, `extern asmlinkage void r4k_wait(void);`, `extern void r4k_wait_irqoff(void);`, `static inline int using_skipover_handler(void)`, `extern void __init check_wait(void);`, `extern int mips_cpuidle_wait_enter(struct cpuidle_device *dev,`, `struct cpuidle_driver *drv, int index);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/cpuidle.h>`, `<linux/linkage.h>`.

### Integration Points
Used by interrupt entry/exit, irqdomains, PIC/CPU irqchips, timers, scheduler idle, tracing, and diagnostics. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Missing hazards, wrong stack bounds, bad IRQ numbering, or failed acknowledgements can create lost interrupts or storms. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/idle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/inst.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/inst.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/inst.h` Low-level MIPS ISA, instruction encoding, hazard barrier, jump-label patching, or symbol linkage contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 88 lines / 2398 bytes. macros/constants: `_ASM_INST_H`, `MIPSInst`, `I_OPCODE_SFT`, `MIPSInst_OPCODE`, `I_JTARGET_SFT`, `MIPSInst_JTARGET`, `I_RS_SFT`, `MIPSInst_RS`, `I_RT_SFT`, `MIPSInst_RT`, `I_IMM_SFT`, `MIPSInst_SIMM`, `MIPSInst_UIMM`, `I_CACHEOP_SFT`, `MIPSInst_CACHEOP`, `I_CACHESEL_SFT`, `MIPSInst_CACHESEL`, `I_RD_SFT`; types/functions/declarations: `typedef unsigned int mips_instruction;`, `struct mm_decoded_insn {`, `extern const int reg16to32[];`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<uapi/asm/inst.h>`.

### Integration Points
Used by assembly, exception/TLB code, static keys, syscall linkage, emulators, probes, and patching paths. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong ISA selection, barriers, instruction fields, or symbol aliases cause configuration-specific crashes. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/inst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/io.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/io.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/io.h` MIPS architecture include contract for platform or subsystem code. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 564 lines / 16634 bytes. macros/constants: `_ASM_IO_H`, `iobarrier_rw`, `iobarrier_r`, `iobarrier_w`, `iobarrier_sync`, `__virt_to_phys`, `virt_to_phys`, `ioremap`, `ioremap_cache`, `ioremap_wc`, `war_io_reorder_wmb`, `war_io_reorder_wmb`, `__BUILD_MEMORY_SINGLE`, `__BUILD_IOPORT_SINGLE`, `__BUILD_MEMORY_PFX`, `BUILDIO_MEM`, `__BUILD_IOPORT_PFX`, `BUILDIO_IOPORT`; types/functions/declarations: `extern unsigned long mips_io_port_base;`, `static inline void set_io_port_base(unsigned long base)`, `static inline unsigned long __virt_to_phys_nodebug(volatile const void *address)`, `extern phys_addr_t __virt_to_phys(volatile const void *x);`, `static inline phys_addr_t virt_to_phys(const volatile void *x)`, `static inline unsigned long isa_virt_to_bus(volatile void *address)`, `static inline void pfx##write##bwlq(type val,				\`, `static inline type pfx##read##bwlq(const volatile void __iomem *mem)	\`, `static inline void pfx##out##bwlq(type val, unsigned long port)		\`, `static inline type pfx##in##bwlq(unsigned long port)			\`, `static inline void writes##bwlq(volatile void __iomem *mem,		\`, `static inline void reads##bwlq(const volatile void __iomem *mem,	\`, `static inline void outs##bwlq(unsigned long port, const void *addr,	\`, `static inline void ins##bwlq(unsigned long port, void *addr,		\`, `extern void (*_dma_cache_wback_inv)(unsigned long start, unsigned long size);`, `extern void (*_dma_cache_wback)(unsigned long start, unsigned long size);`, `extern void (*_dma_cache_inv)(unsigned long start, unsigned long size);`, `struct pci_dev;`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/compiler.h>`, `<linux/types.h>`, `<linux/irqflags.h>`, `<asm/addrspace.h>`, `<asm/barrier.h>`, `<asm/bug.h>`, `<asm/byteorder.h>`, `<asm/cpu.h>`.

### Integration Points
Used by including MIPS kernel code; Ceph relevance is indirect through kernel services. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
ABI drift or feature-guard mistakes break builds or runtime behavior. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/crime.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/crime.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/crime.h` Platform hardware register, IRQ, and device-layout contract for Jazz or SGI IP32 CRIME/MACE systems. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 158 lines / 5261 bytes. macros/constants: `__ASM_CRIME_H__`, `CRIME_BASE`, `CRIME_ID_MASK`, `CRIME_ID_IDBITS`, `CRIME_ID_IDVALUE`, `CRIME_ID_REV`, `CRIME_REV_PETTY`, `CRIME_REV_11`, `CRIME_REV_13`, `CRIME_REV_14`, `CRIME_CONTROL_MASK`, `CRIME_CONTROL_TRITON_SYSADC`, `CRIME_CONTROL_CRIME_SYSADC`, `CRIME_CONTROL_HARD_RESET`, `CRIME_CONTROL_SOFT_RESET`, `CRIME_CONTROL_DOG_ENA`, `CRIME_CONTROL_ENDIANESS`, `CRIME_CONTROL_ENDIAN_BIG`; types/functions/declarations: `struct sgi_crime {`, `extern struct sgi_crime __iomem *crime;`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by platform setup, PCI/ISA, Ethernet, SCSI, audio, serial, keyboard, timers, DMA, and error handling. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Struct layout and fixed address/IRQ mistakes can misprogram hardware or clear wrong error bits. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/crime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/ip32_ints.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/ip32_ints.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/ip32_ints.h` Platform hardware register, IRQ, and device-layout contract for Jazz or SGI IP32 CRIME/MACE systems. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 114 lines / 2326 bytes. macros/constants: `__ASM_IP32_INTS_H`; types/functions/declarations: `enum ip32_irq_no {`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/irq.h>`.

### Integration Points
Used by platform setup, PCI/ISA, Ethernet, SCSI, audio, serial, keyboard, timers, DMA, and error handling. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Struct layout and fixed address/IRQ mistakes can misprogram hardware or clear wrong error bits. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/ip32_ints.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/mace.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/mace.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/mace.h` Platform hardware register, IRQ, and device-layout contract for Jazz or SGI IP32 CRIME/MACE systems. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 365 lines / 10742 bytes. macros/constants: `__ASM_MACE_H__`, `MACE_BASE`, `MACEPCI_ERROR_MASTER_ABORT`, `MACEPCI_ERROR_TARGET_ABORT`, `MACEPCI_ERROR_DATA_PARITY_ERR`, `MACEPCI_ERROR_RETRY_ERR`, `MACEPCI_ERROR_ILLEGAL_CMD`, `MACEPCI_ERROR_SYSTEM_ERR`, `MACEPCI_ERROR_INTERRUPT_TEST`, `MACEPCI_ERROR_PARITY_ERR`, `MACEPCI_ERROR_OVERRUN`, `MACEPCI_ERROR_RSVD`, `MACEPCI_ERROR_MEMORY_ADDR`, `MACEPCI_ERROR_CONFIG_ADDR`, `MACEPCI_ERROR_MASTER_ABORT_ADDR_VALID`, `MACEPCI_ERROR_TARGET_ABORT_ADDR_VALID`, `MACEPCI_ERROR_DATA_PARITY_ADDR_VALID`, `MACEPCI_ERROR_RETRY_ADDR_VALID`; types/functions/declarations: `struct mace_pci {`, `struct mace_video {`, `struct mace_ethernet {`, `struct mace_audio {`, `struct {`, `struct mace_parport {`, `struct mace_isactrl {`, `struct mace_parport parport;`, `struct mace_ps2port {`, `struct mace_ps2 {`, `struct mace_ps2port keyb;`, `struct mace_ps2port mouse;`, `struct mace_i2c {`, `typedef union {`, `struct reg {`, `struct mace_timers {`, `struct mace_perif {`, `struct mace_audio audio;`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by platform setup, PCI/ISA, Ethernet, SCSI, audio, serial, keyboard, timers, DMA, and error handling. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Struct layout and fixed address/IRQ mistakes can misprogram hardware or clear wrong error bits. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/mace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/irq.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/irq.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/irq.h` MIPS interrupt, IRQ-controller, IRQ-stack, IRQ-register, CPU idle, or local IRQ flag support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 83 lines / 2257 bytes. macros/constants: `_ASM_IRQ_H`, `IRQ_STACK_SIZE`, `IRQ_STACK_START`, `irq_canonicalize`, `CP0_LEGACY_COMPARE_IRQ`, `CP0_LEGACY_PERFCNT_IRQ`, `arch_trigger_cpumask_backtrace`; types/functions/declarations: `extern void *irq_stack[NR_CPUS];`, `static inline bool on_irq_stack(int cpu, unsigned long sp)`, `static inline int irq_canonicalize(int irq)`, `extern void do_IRQ(unsigned int irq);`, `struct irq_domain;`, `extern void do_domain_IRQ(struct irq_domain *domain, unsigned int irq);`, `extern void arch_init_irq(void);`, `extern void spurious_interrupt(void);`, `extern int cp0_compare_irq;`, `extern int cp0_compare_irq_shift;`, `extern int cp0_perfcount_irq;`, `extern int cp0_fdc_irq;`, `extern int get_c0_fdc_int(void);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/linkage.h>`, `<linux/smp.h>`, `<asm/mipsmtregs.h>`, `<irq.h>`.

### Integration Points
Used by interrupt entry/exit, irqdomains, PIC/CPU irqchips, timers, scheduler idle, tracing, and diagnostics. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Missing hazards, wrong stack bounds, bad IRQ numbering, or failed acknowledgements can create lost interrupts or storms. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/irq_cpu.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/irq_cpu.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/irq_cpu.h` MIPS interrupt, IRQ-controller, IRQ-stack, IRQ-register, CPU idle, or local IRQ flag support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 20 lines / 427 bytes. macros/constants: `_ASM_IRQ_CPU_H`; types/functions/declarations: `extern void mips_cpu_irq_init(void);`, `struct device_node;`, `extern int mips_cpu_irq_of_init(struct device_node *of_node,`, `struct device_node *parent);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by interrupt entry/exit, irqdomains, PIC/CPU irqchips, timers, scheduler idle, tracing, and diagnostics. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Missing hazards, wrong stack bounds, bad IRQ numbering, or failed acknowledgements can create lost interrupts or storms. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/irq_cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/irq_gt641xx.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/irq_gt641xx.h

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/irq_gt641xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/irq_regs.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/irq_regs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/irq_regs.h` MIPS interrupt, IRQ-controller, IRQ-stack, IRQ-register, CPU idle, or local IRQ flag support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 28 lines / 540 bytes. macros/constants: `__ASM_IRQ_REGS_H`, `ARCH_HAS_OWN_IRQ_REGS`; types/functions/declarations: `static inline struct pt_regs *get_irq_regs(void)`, `static inline struct pt_regs *set_irq_regs(struct pt_regs *new_regs)`, `struct pt_regs *old_regs;`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/thread_info.h>`.

### Integration Points
Used by interrupt entry/exit, irqdomains, PIC/CPU irqchips, timers, scheduler idle, tracing, and diagnostics. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Missing hazards, wrong stack bounds, bad IRQ numbering, or failed acknowledgements can create lost interrupts or storms. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/irq_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/irqflags.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/irqflags.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/irqflags.h` MIPS interrupt, IRQ-controller, IRQ-stack, IRQ-register, CPU idle, or local IRQ flag support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 185 lines / 4208 bytes. macros/constants: `_ASM_IRQFLAGS_H`; types/functions/declarations: `static inline void arch_local_irq_disable(void)`, `static inline unsigned long arch_local_irq_save(void)`, `static inline void arch_local_irq_restore(unsigned long flags)`, `static inline void arch_local_irq_enable(void)`, `static inline unsigned long arch_local_save_flags(void)`, `static inline int arch_irqs_disabled_flags(unsigned long flags)`, `static inline int arch_irqs_disabled(void)`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/compiler.h>`, `<linux/stringify.h>`, `<asm/compiler.h>`, `<asm/hazards.h>`.

### Integration Points
Used by interrupt entry/exit, irqdomains, PIC/CPU irqchips, timers, scheduler idle, tracing, and diagnostics. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Missing hazards, wrong stack bounds, bad IRQ numbering, or failed acknowledgements can create lost interrupts or storms. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/isa-rev.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/isa-rev.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/isa-rev.h` Low-level MIPS ISA, instruction encoding, hazard barrier, jump-label patching, or symbol linkage contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 24 lines / 556 bytes. macros/constants: `__MIPS_ASM_ISA_REV_H__`, `MIPS_ISA_REV`, `MIPS_ISA_REV`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by assembly, exception/TLB code, static keys, syscall linkage, emulators, probes, and patching paths. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong ISA selection, barriers, instruction fields, or symbol aliases cause configuration-specific crashes. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/isa-rev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/isadep.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/isadep.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/isadep.h` Low-level MIPS ISA, instruction encoding, hazard barrier, jump-label patching, or symbol linkage contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 35 lines / 573 bytes. macros/constants: `__ASM_ISADEP_H`, `KU_MASK`, `KU_USER`, `KU_KERN`, `KU_MASK`, `KU_USER`, `KU_KERN`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by assembly, exception/TLB code, static keys, syscall linkage, emulators, probes, and patching paths. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong ISA selection, barriers, instruction fields, or symbol aliases cause configuration-specific crashes. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/isadep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/jazz.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/jazz.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/jazz.h` Platform hardware register, IRQ, and device-layout contract for Jazz or SGI IP32 CRIME/MACE systems. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 310 lines / 8200 bytes. macros/constants: `__ASM_JAZZ_H`, `JAZZ_LOCAL_IO_SPACE`, `PICA_ASIC_REVISION`, `PICA_LED`, `LED_DOT`, `LED_SPACE`, `LED_0`, `LED_1`, `LED_2`, `LED_3`, `LED_4`, `LED_5`, `LED_6`, `LED_7`, `LED_8`, `LED_9`, `LED_A`, `LED_b`; types/functions/declarations: `typedef struct {`, `typedef struct {`, `typedef struct {`, `typedef struct {`, `static inline void r4030_delay(void)`, `static inline unsigned short r4030_read_reg16(unsigned long addr)`, `static inline unsigned int r4030_read_reg32(unsigned long addr)`, `static inline void r4030_write_reg16(unsigned long addr, unsigned val)`, `static inline void r4030_write_reg32(unsigned long addr, unsigned val)`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by platform setup, PCI/ISA, Ethernet, SCSI, audio, serial, keyboard, timers, DMA, and error handling. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Struct layout and fixed address/IRQ mistakes can misprogram hardware or clear wrong error bits. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/jazz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/jazzdma.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/jazzdma.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/jazzdma.h` DMA mapping and legacy DMA programming contract, including address translation, controller registers, cache maintenance, or Jazz VDMA APIs. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 88 lines / 2826 bytes. macros/constants: `_ASM_JAZZDMA_H`, `VDMA_PAGESIZE`, `VDMA_PGTBL_ENTRIES`, `VDMA_PGTBL_SIZE`, `VDMA_PAGE_EMPTY`, `VDMA_PAGE`, `VDMA_OFFSET`, `JAZZ_R4030_CHNL_MODE`, `JAZZ_R4030_CHNL_ENABLE`, `JAZZ_R4030_CHNL_COUNT`, `JAZZ_R4030_CHNL_ADDR`, `R4030_CHNL_ENABLE`, `R4030_CHNL_WRITE`, `R4030_TC_INTR`, `R4030_MEM_INTR`, `R4030_ADDR_INTR`, `R4030_MODE_ATIME_40`, `R4030_MODE_ATIME_80`; types/functions/declarations: `extern unsigned long vdma_alloc(unsigned long paddr, unsigned long size);`, `extern int vdma_free(unsigned long laddr);`, `extern unsigned long vdma_phys2log(unsigned long paddr);`, `extern unsigned long vdma_log2phys(unsigned long laddr);`, `extern void vdma_stats(void);		/* for debugging only */`, `extern void vdma_enable(int channel);`, `extern void vdma_disable(int channel);`, `extern void vdma_set_mode(int channel, int mode);`, `extern void vdma_set_addr(int channel, long addr);`, `extern void vdma_set_count(int channel, int count);`, `extern int vdma_get_residue(int channel);`, `extern int vdma_get_enable(int channel);`, `typedef volatile struct VDMA_PGTBL_ENTRY {`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by block, network, floppy, SCSI, ISA/Jazz devices, and noncoherent cache paths. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong DMA address translation, cache flushing, locking, or channel programming can corrupt memory and page-cache data. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/jazzdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/jump_label.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/jump_label.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/jump_label.h` Low-level MIPS ISA, instruction encoding, hazard barrier, jump-label patching, or symbol linkage contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 80 lines / 1694 bytes. macros/constants: `_ASM_MIPS_JUMP_LABEL_H`, `arch_jump_label_transform_static`, `JUMP_LABEL_NOP_SIZE`, `WORD_INSN`, `WORD_INSN`; types/functions/declarations: `struct module;`, `extern void jump_label_apply_nops(struct module *mod);`, `typedef u64 jump_label_t;`, `typedef u32 jump_label_t;`, `struct jump_entry {`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/types.h>`, `<asm/isa-rev.h>`.

### Integration Points
Used by assembly, exception/TLB code, static keys, syscall linkage, emulators, probes, and patching paths. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong ISA selection, barriers, instruction fields, or symbol aliases cause configuration-specific crashes. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/jump_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/kdebug.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/kdebug.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/kdebug.h` MIPS debugging, crash/kexec, KGDB, kprobe, die-notifier, and breakpoint instrumentation contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 20 lines / 303 bytes. macros/constants: `_ASM_MIPS_KDEBUG_H`; types/functions/declarations: `enum die_val {`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/notifier.h>`.

### Integration Points
Used by trap handling, crash kernels, runtime instrumentation, debuggers, and module probing. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Register layout, delay-slot, cache-flush, or SMP rendezvous bugs can make diagnostics unreliable or hang reboot. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/kdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/kexec.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/kexec.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/kexec.h` MIPS debugging, crash/kexec, KGDB, kprobe, die-notifier, and breakpoint instrumentation contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 51 lines / 1495 bytes. macros/constants: `KEXEC_SOURCE_MEMORY_LIMIT`, `KEXEC_DESTINATION_MEMORY_LIMIT`, `KEXEC_CONTROL_MEMORY_LIMIT`, `KEXEC_CONTROL_PAGE_SIZE`, `KEXEC_ARCH`, `MAX_NOTE_BYTES`; types/functions/declarations: `static inline void crash_setup_regs(struct pt_regs *newregs,`, `struct pt_regs *oldregs)`, `struct kimage;`, `extern unsigned long kexec_args[4];`, `extern int (*_machine_kexec_prepare)(struct kimage *);`, `extern void (*_machine_kexec_shutdown)(void);`, `extern void (*_machine_crash_shutdown)(struct pt_regs *regs);`, `extern const unsigned char kexec_smp_wait[];`, `extern unsigned long secondary_kexec_args[4];`, `extern atomic_t kexec_ready_to_reboot;`, `extern void (*_crash_smp_send_stop)(void);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/stacktrace.h>`.

### Integration Points
Used by trap handling, crash kernels, runtime instrumentation, debuggers, and module probing. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Register layout, delay-slot, cache-flush, or SMP rendezvous bugs can make diagnostics unreliable or hang reboot. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/kexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/kgdb.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/kgdb.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/kgdb.h` MIPS debugging, crash/kexec, KGDB, kprobe, die-notifier, and breakpoint instrumentation contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 45 lines / 1218 bytes. macros/constants: `__ASM_KGDB_H_`, `KGDB_GDB_REG_SIZE`, `GDB_SIZEOF_REG`, `KGDB_GDB_REG_SIZE`, `GDB_SIZEOF_REG`, `KGDB_GDB_REG_SIZE`, `GDB_SIZEOF_REG`, `BUFMAX`, `DBG_MAX_REG_NUM`, `NUMREGBYTES`, `NUMCRITREGBYTES`, `BREAK_INSTR_SIZE`, `CACHE_FLUSH_IS_SAFE`; types/functions/declarations: `extern void arch_kgdb_breakpoint(void);`, `extern void *saved_vectors[32];`, `extern void handle_exception(struct pt_regs *regs);`, `extern void breakinst(void);`, `extern int kgdb_ll_trap(int cmd, const char *str,`, `struct pt_regs *regs, long err, int trap, int sig);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/sgidefs.h>`.

### Integration Points
Used by trap handling, crash kernels, runtime instrumentation, debuggers, and module probing. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Register layout, delay-slot, cache-flush, or SMP rendezvous bugs can make diagnostics unreliable or hang reboot. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/kprobes.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/kprobes.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/kprobes.h` MIPS debugging, crash/kexec, KGDB, kprobe, die-notifier, and breakpoint instrumentation contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 76 lines / 1622 bytes. macros/constants: `_ASM_KPROBES_H`, `__ARCH_WANT_KPROBES_INSN_SLOT`, `MAX_INSN_SIZE`, `flush_insn_slot`, `kretprobe_blacklist_size`, `SKIP_DELAYSLOT`; types/functions/declarations: `struct kprobe;`, `struct pt_regs;`, `typedef union mips_instruction kprobe_opcode_t;`, `struct arch_specific_insn {`, `struct prev_kprobe {`, `struct kprobe *kp;`, `struct kprobe_ctlblk {`, `struct prev_kprobe prev_kprobe;`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm-generic/kprobes.h>`, `<linux/ptrace.h>`, `<linux/types.h>`, `<asm/cacheflush.h>`, `<asm/kdebug.h>`, `<asm/inst.h>`.

### Integration Points
Used by trap handling, crash kernels, runtime instrumentation, debuggers, and module probing. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Register layout, delay-slot, cache-flush, or SMP rendezvous bugs can make diagnostics unreliable or hang reboot. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/kvm_host.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/kvm_host.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/kvm_host.h` MIPS KVM host ABI, vCPU/VM state, CP0/TLB/timer/FPU/MSA accessors, callbacks, and MMU/emulation declarations. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 897 lines / 30152 bytes. macros/constants: `__MIPS_KVM_HOST_H__`, `MIPS_CP0_32`, `MIPS_CP0_64`, `KVM_REG_MIPS_CP0_INDEX`, `KVM_REG_MIPS_CP0_ENTRYLO0`, `KVM_REG_MIPS_CP0_ENTRYLO1`, `KVM_REG_MIPS_CP0_CONTEXT`, `KVM_REG_MIPS_CP0_CONTEXTCONFIG`, `KVM_REG_MIPS_CP0_USERLOCAL`, `KVM_REG_MIPS_CP0_XCONTEXTCONFIG`, `KVM_REG_MIPS_CP0_PAGEMASK`, `KVM_REG_MIPS_CP0_PAGEGRAIN`, `KVM_REG_MIPS_CP0_SEGCTL0`, `KVM_REG_MIPS_CP0_SEGCTL1`, `KVM_REG_MIPS_CP0_SEGCTL2`, `KVM_REG_MIPS_CP0_PWBASE`, `KVM_REG_MIPS_CP0_PWFIELD`, `KVM_REG_MIPS_CP0_PWSIZE`; types/functions/declarations: `extern unsigned long GUESTID_MASK;`, `extern unsigned long GUESTID_FIRST_VERSION;`, `extern unsigned long GUESTID_VERSION_MASK;`, `static inline bool kvm_is_error_hva(unsigned long addr)`, `struct kvm_vm_stat {`, `struct kvm_vm_stat_generic generic;`, `struct kvm_vcpu_stat {`, `struct kvm_vcpu_stat_generic generic;`, `struct kvm_arch_memory_slot {`, `struct ipi_state {`, `struct loongson_kvm_ipi;`, `struct ipi_io_device {`, `struct loongson_kvm_ipi *ipi;`, `struct kvm_io_device device;`, `struct loongson_kvm_ipi {`, `struct kvm *kvm;`, `struct ipi_state ipistate[16];`, `struct ipi_io_device dev_ipi[4];`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/cpumask.h>`, `<linux/mutex.h>`, `<linux/hrtimer.h>`, `<linux/interrupt.h>`, `<linux/types.h>`, `<linux/kvm.h>`, `<linux/kvm_types.h>`, `<linux/threads.h>`.

### Integration Points
Used by MIPS KVM/VZ guest execution, KVM ioctls, MMIO emulation, interrupt injection, timers, TLB management, and Loongson IPI support. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
CP0 races, timer drift, MMU/TLB mistakes, or FPU/MSA ownership bugs can corrupt host or guest state. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/kvm_host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/kvm_types.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/kvm_types.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/kvm_types.h` MIPS KVM host ABI, vCPU/VM state, CP0/TLB/timer/FPU/MSA accessors, callbacks, and MMU/emulation declarations. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 7 lines / 184 bytes. macros/constants: `_ASM_MIPS_KVM_TYPES_H`, `KVM_ARCH_NR_OBJS_PER_MEMORY_CACHE`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by MIPS KVM/VZ guest execution, KVM ioctls, MMIO emulation, interrupt injection, timers, TLB management, and Loongson IPI support. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
CP0 races, timer drift, MMU/TLB mistakes, or FPU/MSA ownership bugs can corrupt host or guest state. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/kvm_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/linkage.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/linkage.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/linkage.h` Low-level MIPS ISA, instruction encoding, hazard barrier, jump-label patching, or symbol linkage contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 13 lines / 307 bytes. macros/constants: `__ASM_LINKAGE_H`, `cond_syscall`, `SYSCALL_ALIAS`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/asm.h>`.

### Integration Points
Used by assembly, exception/TLB code, static keys, syscall linkage, emulators, probes, and patching paths. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong ISA selection, barriers, instruction fields, or symbol aliases cause configuration-specific crashes. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/local.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/local.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/local.h` MIPS local per-CPU atomic counter operations based on atomic_long and LL/SC loops. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 189 lines / 4822 bytes. macros/constants: `_ARCH_MIPS_LOCAL_H`, `LOCAL_INIT`, `local_read`, `local_set`, `local_add`, `local_sub`, `local_inc`, `local_dec`, `local_xchg`, `local_inc_not_zero`, `local_dec_return`, `local_inc_return`, `local_sub_and_test`, `local_inc_and_test`, `local_dec_and_test`, `local_add_negative`, `__local_inc`, `__local_dec`; types/functions/declarations: `typedef struct`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/percpu.h>`, `<linux/bitops.h>`, `<linux/atomic.h>`, `<asm/asm.h>`, `<asm/cmpxchg.h>`, `<asm/compiler.h>`.

### Integration Points
Used by local counters, stats, scheduler/perf-style accounting, and per-CPU code. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Using raw helpers without exclusion or bad LL/SC constraints races under SMP. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/maar.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/maar.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/maar.h` MIPS MAAR memory attribute register configuration and pair programming helpers. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 127 lines / 4270 bytes. macros/constants: `__MIPS_ASM_MIPS_MAAR_H__`; types/functions/declarations: `static inline void write_maar_pair(unsigned idx, phys_addr_t lower,`, `extern void maar_init(void);`, `struct maar_config {`, `static inline unsigned maar_config(const struct maar_config *cfg,`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/hazards.h>`, `<asm/mipsregs.h>`.

### Integration Points
Used by boot/cacheability setup and platform memory attribute selection. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong MAAR ranges create invalid cacheability/order attributes for RAM or MMIO. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/maar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath25/ath25_platform.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath25/ath25_platform.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath25/ath25_platform.h` Atheros ATH25 board-data or CPU-feature override contract for AR231x platforms. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 74 lines / 2927 bytes. macros/constants: `__ASM_MACH_ATH25_PLATFORM_H`, `ATH25_BD_MAGIC`, `BD_REV`, `BD_ENET0`, `BD_ENET1`, `BD_UART1`, `BD_UART0`, `BD_RSTFACTORY`, `BD_SYSLED`, `BD_EXTUARTCLK`, `BD_CPUFREQ`, `BD_SYSFREQ`, `BD_WLAN0`, `BD_MEMCAP`, `BD_DISWATCHDOG`, `BD_WLAN1`, `BD_ISCASPER`, `BD_WLAN0_2G_EN`; types/functions/declarations: `struct ath25_boarddata {`, `struct ar231x_board_config {`, `struct ath25_boarddata *config;`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/etherdevice.h>`.

### Integration Points
Used by ATH25 platform setup, Ethernet/WLAN/UART/GPIO/LED registration, and compile-time CPU feature selection. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong board flags, MAC/calibration data, or CPU features break devices or emit unsupported instructions. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath25/ath25_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath25/cpu-feature-overrides.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath25/cpu-feature-overrides.h

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath25/cpu-feature-overrides.h` Atheros ATH25 board-data or CPU-feature override contract for AR231x platforms. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 59 lines / 1417 bytes. macros/constants: `__ASM_MACH_ATH25_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_sb1_cache`, `cpu_has_fpu`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_ejtag`, `cpu_has_mips16`, `cpu_has_mips16e2`, `cpu_has_mdmx`, `cpu_has_mips3d`, `cpu_has_smartmips`, `cpu_has_mips32r1`, `cpu_has_mips64r1`, `cpu_has_mips64r2`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by ATH25 platform setup, Ethernet/WLAN/UART/GPIO/LED registration, and compile-time CPU feature selection. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong board flags, MAC/calibration data, or CPU features break devices or emit unsupported instructions. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath25/cpu-feature-overrides.h -->
