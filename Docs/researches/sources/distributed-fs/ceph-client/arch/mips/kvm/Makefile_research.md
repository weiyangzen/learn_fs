## sources/distributed-fs/ceph-client/arch/mips/kvm/Makefile

Purpose: Builds the MIPS KVM backend and related TLB helper object.

Important APIs, types, and functions: Includes `virt/kvm/Makefile.kvm`, adds include paths for `virt/kvm` and `arch/mips/kvm`, and composes `kvm.o` from `mips.o`, `emulate.o`, `entry.o`, `interrupt.o`, `stats.o`, `fpu.o`, `hypcall.o`, `mmu.o`, `vz.o`, optional `msa.o`, and optional `loongson_ipi.o`. `tlb.o` is built into `obj-y`.

Control flow: `obj-$(CONFIG_KVM) += kvm.o` gates the main backend. `obj-y += tlb.o` keeps TLB helper code available from the architecture tree even outside the KVM module linkage pattern.

State and persistence: No runtime state; this is a build graph declaration.

Dependencies and integration points: Integrates MIPS KVM with generic KVM build infrastructure, optional MSA support (`CONFIG_CPU_HAS_MSA`), and Loongson IPI support (`CONFIG_CPU_LOONGSON64`).

Risks: Missing optional object gates can break references in CPU-specific paths. Because `tlb.o` is unconditional, symbols and dependencies in that file must remain buildable for the broader MIPS configuration matrix.

Test signals: Build with KVM built-in/module/off, MSA on/off, Loongson64 on/off, and generic MIPS VZ targets.
