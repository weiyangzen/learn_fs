## sources/distributed-fs/ceph-client/arch/arm64/kernel/vmlinux.lds.S

### Purpose
`vmlinux.lds.S` is the ARM64 kernel linker script defining the final kernel image layout, special text/data sections, page tables, hypervisor sections, init/exit regions, relocation records, BSS, early stack, debug metadata, and layout assertions.

### Important APIs, Types, And Functions
It defines symbols such as `_text`, `_stext`, `_etext`, `__init_begin`, `__init_end`, `_data`, `_edata`, `_end`, idmap/tramp/reserved/swapper page directories, hypervisor section bounds, relocation bounds, and many config-dependent section macros.

### Control Flow
The linker starts at `KIMAGE_VADDR`, places head text, main text including IRQ/entry/scheduler/lock/kprobe/hypervisor/static-call text, read-only data, optional hypervisor rodata, GOT checks, trampoline/hibernate/kexec/idmap text, early page tables, init text/data, alternatives, unwind tables, percpu and hypervisor percpu/data, dynamic relocations, writable data, MMU-off data split by cache-maintenance requirements, PE/COFF padding, BSS, init page tables, early stack, and debug/modinfo/ELF details. Assertions validate size, alignment, PLT/GOT emptiness, page-table offsets, kexec/hibernate bounds, and hypervisor BSS alignment.

### State, Persistence, And Dependencies
The output is the static kernel image layout and linker-defined symbols consumed at boot and runtime. It controls memory placement rather than mutable state.

### Integration Points
It integrates KVM nVHE/hyp sections, EFI PE/COFF metadata, KASLR/relocation support, idmap and trampoline mappings, hibernation, kexec, alternatives, static calls, percpu data, MMU-off data used by boot/suspend paths, and generic linker-script macros.

### Risks
Layout mistakes can break early boot, virtual/physical conversion, KVM hyp mappings, kexec, hibernation, KPTI trampolines, or runtime text patching. Assertions are critical guardrails for image invariants.

### Test Signals
Build broad configs with KVM, EFI, KASLR, KEXEC, HIBERNATION, UNMAP_KERNEL_AT_EL0, UNWIND_TABLES, and NVHE tracing; inspect map files; boot-test and validate linker assertions and absence of unexpected PLT/GOT entries.
