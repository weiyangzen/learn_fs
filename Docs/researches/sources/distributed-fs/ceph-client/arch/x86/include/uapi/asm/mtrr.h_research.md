<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mtrr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mtrr.h

Purpose: Defines the legacy x86 MTRR userspace ioctl ABI, variable/fixed range limits, memory type values, and 32-bit versus 64-bit entry layouts.

Important APIs/types/functions: `struct mtrr_sentry`, `struct mtrr_gentry`, `struct mtrr_var_range`, `mtrr_type`, `MTRR_NUM_FIXED_RANGES`, `MTRR_MAX_VAR_RANGES`, `MTRRphysBase_MSR()`, `MTRRphysMask_MSR()`, `MTRRIOC_*`, and `MTRR_TYPE_*`.

Control flow: Userspace issues MTRR ioctls to add, set, delete, kill, or get memory type ranges. Kernel MTRR code validates ranges, programs CPU MSRs, and handles 32-bit emulation layout differences.

State and persistence behavior: MTRR programming persists in CPU hardware registers until changed or reset. The ABI layout must remain stable for old X server and graphics tooling.

Dependencies and integration points: Depends on Linux UAPI types/ioctl/errno. Integrates with cache attribute management, PAT interactions, CPU MSR programming, graphics framebuffers, and compatibility ioctl handling.

Risks and test signals: Risks include 32-bit/64-bit structure-order confusion, cache-type conflicts with PAT, and unsafe memory-type programming. Test legacy MTRR tools, compat ioctls, framebuffer write-combining setup, CPU hotplug synchronization, and invalid range rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mtrr.h -->
