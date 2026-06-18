# sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/nvhe.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/nvhe.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/nvhe.h` Adds KVM nVHE hypervisor stack-unwind initialization and host-side declarations. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
kvm_nvhe_unwind_init(), DECLARE_KVM_NVHE_PER_CPU overflow_stack and kvm_stacktrace_info, kvm_arm_hyp_stack_base, kvm_nvhe_dump_backtrace(). The file is 55 lines / 1730 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Initialization seeds unwind_state with HYP fp/pc. In non-protected nVHE, the host can unwind HYP stack directly; protected nVHE dumps through shared buffers handled elsewhere.

### State, Persistence, And Dependencies
State is HYP per-CPU stacktrace data, overflow stack, and host hyp stack base. Depends on stacktrace/common and KVM nVHE per-CPU declarations; integrates with KVM hyp diagnostics and protected KVM stack dumping.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Host/protected mode memory visibility differs; direct HYP stack access in pKVM would violate isolation; wrong offset can decode bad frames.

### Test Signals
Run KVM nVHE/pKVM backtrace tests, hyp fault injection, and host dump validation.
