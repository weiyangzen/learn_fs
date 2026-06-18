# sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq_64.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq_64.h` declares SPARC64 IRQ limits, IRQ bucket encoding, interrupt builder hooks, softirq stack handling, and hypervisor interrupt helpers. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 98 lines, 3075 bytes. Primary surface: `NR_IRQS`, `irq_bucket`, `irq_canonicalize`, `__irq_ino`, `irq_alloc`, `irq_free`, `sun4u_build_irq`, `sun4v_build_irq`, `sun4v_build_virq`, `sun4v_build_msi`, `handler_irq`, `do_softirq_own_stack`, and `get_irq_regs`. Symbol scan highlights: `_SPARC64_IRQ_H`, `IMAP_VALID`, `IMAP_TID_UPA`, `IMAP_TID_JBUS`, `IMAP_TID_SHIFT`, `IMAP_AID_SAFARI`, `IMAP_AID_SHIFT`, `IMAP_NID_SAFARI`, `IMAP_NID_SHIFT`, `IMAP_IGN`, `IMAP_INO`, `IMAP_INR`, `ICLR_IDLE`, `ICLR_TRANSMIT`, `ICLR_PENDING`, `NR_IRQS`, `irq_install_pre_handler`, `irq_canonicalize`, `build_irq`, `sun4v_build_irq`, `sun4v_build_virq`, `sun4v_build_msi`, `sun4v_destroy_msi`, `sun4u_build_msi`, and 10 more.

### Control Flow
platform and PCI code allocate IRQ buckets, map device/sysino/INO/MSI sources to Linux IRQs, and dispatch through low-level trap handlers while preserving register context. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
IRQ bucket arrays and per-CPU interrupt register state persist in IRQ core and low-level architecture code. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/linkage.h>`, `<linux/kernel.h>`, `<linux/errno.h>`, `<linux/interrupt.h>`, `<asm/pil.h>`, `<asm/ptrace.h>`. Integration dependencies: `linux/interrupt.h`, `linux/cache.h`, `linux/percpu.h`, `asm/pil.h`, hypervisor interrupt calls, PCI MSI, and irq core.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
bucket pointer/IRQ encoding errors, per-CPU register mishandling, or wrong mondo/sysino target programming can lose interrupts.

### Test Signals
SPARC64 boot with PCI/MSI devices, CPU hotplug interrupt retargeting, softirq stack tests, and interrupt storm handling. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
