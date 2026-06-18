# sources/distributed-fs/ceph-client/arch/mips/include/asm/kvm_host.h


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
