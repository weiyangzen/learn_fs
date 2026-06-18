# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu.c

Purpose: This file implements RISC-V KVM vCPU lifecycle, ioctls, interrupt state, MP state, load/put CSR and extension context switching, request handling, guest entry/exit, and the main `KVM_RUN` loop. It is the central integration point for timers, AIA, SBI, PMU, FP/vector state, NACL, G-stage VMID, and tracepoints.

Important APIs/types/functions: It defines vCPU stats descriptors/header and per-CPU `kvm_former_vcpu` for CSR reload elision. Lifecycle functions include `kvm_arch_vcpu_create`, `postcreate`, and `destroy`; runtime helpers include `kvm_arch_vcpu_load`, `put`, `kvm_arch_vcpu_ioctl_run`, and `kvm_riscv_vcpu_enter_exit`. Interrupt APIs include flush/sync/set/unset/has-interrupts. MP state, guest-debug, one-reg ioctls, and reset logic are also implemented.

Control flow: vCPU creation initializes config, ISA, vendor IDs, hfence queue, vector/timer/PMU/AIA/SBI state, then resets the vCPU. Nonboot vCPUs are powered off after creation. `KVM_RUN` first completes pending userspace MMIO/SBI/CSR exits, checks signals, loads the vCPU, updates VMID, handles requests, updates AIA hardware, disables preemption/interrupts, flushes pending interrupts into HVIP/HVICTL, sanitizes local TLB state, traces entry, switches to guest through NACL or direct assembly, syncs interrupts/timers after exit, traces exit, and dispatches traps through `vcpu_exit.c`.

State and persistence: Guest context, CSRs, smstateen CSRs, interrupt bitmaps, MP state, reset state, hfence queue, MMU cache, PMU/timer/AIA/SBI/vector/FP state all persist in `vcpu->arch`. Host FP/vector and select CSRs are saved while guest state is loaded. `csr_dirty` forces CSR reload when ioctls changed saved CSR state. `ran_atleast_once` freezes configuration that must not change after execution.

Dependencies and integration points: It depends on KVM core vCPU APIs, SRCU, preempt notifiers, NACL, MMU/VMID/TLB helpers, timers, SBI emulation, PMU, AIA, vector/FP save-restore, one-reg handling, dirty-ring requests, and tracepoints.

Risks and test signals: The guest-entry path is ordering-sensitive: request checks, SRCU unlock, interrupt flush, mode transition, and local IRQ state must match KVM expectations. CSR reload elision requires every mutating ioctl to set `csr_dirty`. Tests should cover vCPU create/destroy, KVM_RUN returns for MMIO/SBI/CSR, signals, sleep/wakeup, reset requests, interrupt set/unset races, guest debug breakpoint exits, CPU migration, NACL and non-NACL entry, FP/vector preservation, and stats increments.
