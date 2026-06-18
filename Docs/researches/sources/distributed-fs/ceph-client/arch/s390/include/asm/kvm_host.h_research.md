# sources/distributed-fs/ceph-client/arch/s390/include/asm/kvm_host.h

Purpose: This is the main s390 KVM host header, defining vCPU/VM architectural state, interrupt queues, CPU model data, crypto/AP state, GISA adapter interrupt structures, protected virtualization state, statistics, and SIE entry declarations.

Important APIs/types/functions: Key definitions include KVM limits and requests, `struct kvm_vcpu_stat`, program-interruption constants, pending IRQ enums and masks, `struct kvm_s390_interrupt_info`, local and floating interrupt state, guest-debug state, `struct kvm_vcpu_arch`, `struct kvm_arch`, async page-fault hooks, crypto mask helpers, `__sie64a()`/`sie64a()`, SIE enter/exit declarations, GISC register APIs, protected-guest predicates, and zPCI KVM hooks.

Control flow: A vCPU run path prepares the SIE block and arch state, enters SIE via `sie64a` or `kvm_s390_enter_exit_sie`, handles intercept codes by updating stats and delivering/injecting queued interrupts, and uses request bits to enable/disable IBS, migration, VSIE restart, or prefix refresh. VM-level paths manage floating interrupts, CPU model/facility masks, crypto/AP controls, GISA alert state, protected virtualization imports, and memory-slot/gmap checks.

State and persistence: Persistent state is extensive: per-vCPU SIE pointers, timers, local interrupt bitmaps, debug state, pfault tokens, CPU timer seqcount data, guarded-storage/SKEY flags, protected-vCPU handles, per-VM gmap, adapters, IPTE locks, model facilities, crypto control block, VSIE pages, idle masks, GISA interrupt state, protected VM storage, and zPCI device lists.

Dependencies and integration points: It depends on Linux KVM core, hrtimers, interrupts, seqlocks, PCI, mmu notifiers, s390 SIE layouts from `kvm_host_types.h`, debug, CPU/fpu, ISC, guarded storage, gmap/MMU, AP crypto, and zPCI.

Risks and test signals: This is high-risk virtualization ABI code: IRQ priority masks, SIE state, protected-guest ownership, and facility masks must match hardware and userspace KVM API expectations. Tests should include KVM unit tests, nested/VSIE, protected virtualization, async page faults, SIGP/interruption injection, AP crypto passthrough, zPCI passthrough, migration start/stop, and stats validation.
