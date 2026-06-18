<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/Makefile

Purpose: Builds the RISC-V KVM implementation and selects objects for core, vCPU, MMU, SBI emulation, timers, AIA, and nested/guest support.

Important APIs/types/functions: Defines `obj-$(CONFIG_KVM) += kvm.o` and `kvm-y` object composition for `main.o`, `vcpu.o`, `vcpu_exit.o`, `mmu.o`, `timer.o`, `vcpu_sbi*.o`, `aia*.o`, and related files depending on config.

Control flow: Kbuild links selected RISC-V KVM objects into the architecture KVM module/built-in target.

State and persistence: Build-time composition only.

Dependencies and integration points: Ties Kconfig KVM enablement to the RISC-V KVM source tree and optional AIA/IMSIC support.

Risks: Missing object entries create unresolved symbols or disabled functionality despite config support.

Test signals: KVM module/built-in build, AIA and non-AIA variants, guest boot, KVM selftests, and module load/unload.

Source read size: 44 lines, 923 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/Makefile -->
