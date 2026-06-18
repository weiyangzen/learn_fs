# sources/distributed-fs/ceph-client/arch/loongarch/kvm/Makefile

Purpose: defines the object composition of the LoongArch KVM module/built-in support.

Important APIs, types, and functions: includes `virt/kvm/Makefile.kvm`, builds `kvm.o` under `CONFIG_KVM`, always includes `switch.o` in this directory's object list, and aggregates `exit.o`, `interrupt.o`, `main.o`, `mmu.o`, `timer.o`, `tlb.o`, `vcpu.o`, `vm.o`, interrupt-controller objects, and `irqfd.o` into `kvm-y`.

Control flow: Kbuild compiles `switch.S` plus the C implementation units and suppresses `override-init` warnings for `exit.o`.

State and persistence: build metadata only; it determines which runtime KVM code is linked.

Dependencies and integration points: integrates with generic KVM build rules, LoongArch assembly world-switch code, and intc subdirectory sources.

Risks: object ordering and omissions can cause missing symbols, unregistered device types, or unavailable world-switch entry points. The warning suppression hints at designated initializer ranges in exit dispatch tables.

Test signals: `CONFIG_KVM=y/m` builds, module symbol resolution, and boot/module load tests.
