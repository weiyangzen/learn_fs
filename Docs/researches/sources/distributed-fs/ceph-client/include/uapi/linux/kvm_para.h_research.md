# sources/distributed-fs/ceph-client/include/uapi/linux/kvm_para.h

Purpose: defines the generic UAPI hypercall number and error-code namespace used by KVM paravirtualized guests, then includes the architecture-specific paravirtual header.

Important APIs and types: exported values include KVM hypercall error returns such as `KVM_ENOSYS`, `KVM_EFAULT`, `KVM_EINVAL`, `KVM_E2BIG`, `KVM_EPERM`, and `KVM_EOPNOTSUPP`, plus hypercall IDs `KVM_HC_VAPIC_POLL_IRQ`, `KVM_HC_MMU_OP`, `KVM_HC_FEATURES`, `KVM_HC_PPC_MAP_MAGIC_PAGE`, `KVM_HC_KICK_CPU`, `KVM_HC_MIPS_GET_CLOCK_FREQ`, `KVM_HC_MIPS_EXIT_VM`, `KVM_HC_MIPS_CONSOLE_OUTPUT`, `KVM_HC_CLOCK_PAIRING`, `KVM_HC_SEND_IPI`, `KVM_HC_SCHED_YIELD`, and `KVM_HC_MAP_GPA_RANGE`.

Control flow: guest code uses architecture-provided `kvm_hypercall*` helpers and feature discovery to invoke these numeric operations on the host. The generic header only reserves IDs and return codes; calling convention and feature bits are provided by `<asm/kvm_para.h>`.

State and persistence: no local state. The ABI affects guest/host behavior at runtime, but any state changed by a hypercall is owned by the KVM host or guest architecture code.

Dependencies and integration points: includes `<asm/kvm_para.h>` and expects architectures to provide `kvm_hypercall0`, `kvm_hypercall1`, feature queries, and availability checks. It is consumed by paravirtual guest kernels and low-level KVM support code.

Risks and test signals: risks are numeric ID collisions, architecture mismatch, and guests issuing hypercalls not advertised by feature discovery. Test by compiling guest headers on supported architectures and running KVM paravirtual feature selftests for clock pairing, IPI, sched-yield, and GPA-range mapping where available.
