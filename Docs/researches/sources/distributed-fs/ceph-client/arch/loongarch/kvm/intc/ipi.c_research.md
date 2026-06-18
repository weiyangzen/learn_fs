# sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/ipi.c

Purpose: emulates LoongArch IOCSR IPI registers, per-vCPU IPI status/enables, mailbox buffers, and cross-vCPU send operations.

Important APIs, types, and functions: device callbacks `kvm_ipi_read()` and `kvm_ipi_write()` wrap `loongarch_ipi_readl()` and `loongarch_ipi_writel()`. Helpers include `ipi_set()`, `ipi_clear()`, `ipi_send()`, `mail_send()`, `any_send()`, `send_ipi_data()`, `read_mailbox()`, `write_mailbox()`, and KVM device attr accessors.

Control flow: IOCSR reads expose status, enable, and mailbox registers. Writes can enable IPI bits, set/clear local pending status, send an IPI bit to another CPUID, update a target mailbox, or write arbitrary IOCSR data to another vCPU. `ipi_set()` injects `LARCH_INT_IPI` only on transition from no pending status to pending; `ipi_clear()` deasserts when status reaches zero.

State and persistence: per-vCPU state lives in `vcpu->arch.ipi_state` with `status`, `en`, mailbox `buf`, and a spinlock. Per-VM state is `struct loongarch_ipi` registered on `KVM_IOCSR_BUS`. Migration-visible state is exposed through KVM device attrs.

Dependencies and integration points: relies on CPUID mapping from `vcpu.c`, generic KVM I/O bus, `kvm_vcpu_ioctl_interrupt()`, SRCU-protected IOCSR bus access, and KVM device infrastructure.

Risks: register access lengths and offsets must match hardware. The mailbox byte-mask semantics in `mail_send()` and `send_ipi_data()` are easy to regress. Invalid CPUID handling logs but often returns zero to the emulated access path, matching device-emulation tolerance.

Test signals: guest SMP IPI tests, mailbox read/write width tests, migration save/restore of IPI regs, invalid target handling, and KVM stats counters for IPI exits.
