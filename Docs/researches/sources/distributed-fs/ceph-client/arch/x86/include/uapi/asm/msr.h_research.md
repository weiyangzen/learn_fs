<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/msr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/msr.h

Purpose: Defines userspace ioctls for reading and writing model-specific registers through the x86 MSR character device interface.

Important APIs/types/functions: `X86_IOC_RDMSR_REGS` and `X86_IOC_WRMSR_REGS`.

Control flow: Userspace sends an array of eight `__u32` values to the MSR driver via ioctl; the kernel performs the requested register access and copies results back for reads.

State and persistence behavior: No header-owned state. MSR writes mutate CPU-local or package-wide hardware state and can persist until reset or rewritten.

Dependencies and integration points: Depends on Linux UAPI types and ioctl. Integrates with `/dev/cpu/*/msr`, CPU feature tooling, performance/power management, and low-level diagnostics.

Risks and test signals: Risks include unsafe MSR writes, ioctl ABI mismatch, and CPU-hotplug races. Test `rdmsr`/`wrmsr` tooling, 32-bit userspace, permission checks, and invalid MSR error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/msr.h -->
