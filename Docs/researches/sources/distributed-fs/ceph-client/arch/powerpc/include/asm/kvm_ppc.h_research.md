# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_ppc.h

Purpose: declares the broad PowerPC KVM implementation API: vcpu run, instruction emulation, MMIO load/store, MMU translation, BookE and Book3S backend hooks, HPT/radix management, TCE/RTAS/pSeries hypercalls, interrupt-controller APIs, real-mode HV calls, LPID allocation, and shared-register access helpers.

Important APIs/types/functions: enums model emulation results and translation modes. `struct kvmppc_ops` is the backend dispatch table for HV/PR operations. `union kvmppc_one_reg` helps one-reg ioctls. APIs span `kvmppc_vcpu_run`, `kvmppc_handle_load/store`, `kvmppc_emulate_instruction`, `kvmppc_xlate`, core vcpu lifecycle and interrupt queueing, HPT allocation/resizing, PAPR TCE ioctls/hcalls, RTAS, XICS/XIVE/MPIC, real-mode HPT hypercalls, LPID management, and helpers for EPR, SRs, endian state, MMIO register packing, and field extraction.

Control flow: generic KVM core enters PowerPC through `kvmppc_ops`, which dispatches to PR, HV, BookE, or Book3S implementations. Guest exits are decoded into instruction emulation, MMIO, timer, interrupt, TCE, RTAS, or hypercall paths. Optional interrupt-controller blocks compile to real functions or stubs based on XICS/XIVE/MPIC support.

State and persistence: operations mutate `struct kvm`, `struct kvm_vcpu`, HPT/radix page tables, TCE tables, RTAS token maps, interrupt-controller state, LPID pools, vcpu shared pages, and real-mode host operation tables.

Dependencies and integration points: includes KVM host state, OpenPIC/MPIC, XICS/XIVE, pSeries, BookE, Book3S, CMA HPT allocation, and generic userspace ioctl ABI types.

Risks: this header is the public internal contract between many KVM backends; stub return values must match caller expectations. Real-mode functions have restricted locking/memory rules. Endian and shared-register access helpers directly affect guest ABI.

Test signals: full PowerPC KVM selftest suite, guest boot under HV/PR/BookE, MMIO emulation tests, one-reg ioctl tests, TCE/RTAS tests, XICS/XIVE/MPIC interrupt injection, LPID allocation stress, and HPT resize/migration tests.
