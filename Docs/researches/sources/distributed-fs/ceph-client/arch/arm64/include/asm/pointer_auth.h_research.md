# sources/distributed-fs/ceph-client/arch/arm64/include/asm/pointer_auth.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pointer_auth.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/pointer_auth.h` Defines pointer-authentication key structures, masks, install/init helpers, and prctl integration for user and optional kernel PAC keys. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
ptrauth_user_pac_mask(), ptrauth_kernel_pac_mask(), PR_PAC_ENABLED_KEYS_MASK, struct ptrauth_key, struct ptrauth_keys_user, struct ptrauth_keys_kernel, __ptrauth_key_install_nosync(), ptrauth_keys_init/install/switch_user/kernel(), ptrauth_enable(), ptrauth_prctl_reset_keys(), ptrauth_set/get_enabled_keys(), thread init/switch macros. The file is 153 lines / 4789 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
When enabled, fork inherits process keys while exec initializes fresh random keys; context switch installs user keys and optional kernel APIA key, then ISB synchronizes. ptrauth_enable sets SCTLR_EL1 ENIA/ENIB/ENDA/ENDB when hardware supports address auth.

### State, Persistence, And Dependencies
Persistent state lives in thread_struct keys_user and optional keys_kernel, plus SCTLR/sysreg key registers. Disabled configs collapse to no-ops or -EINVAL. Depends on random, prctl, cpufeature, memory, sysreg, task/thread_struct; integrates with processor.h prctl macros, stackprotector boot init, suspend exit, exec, fork, and context switch.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Key installation without ISB or wrong support gating can leave stale PAC keys active; mask calculations depend on VA size/TBI; randomization failures or disabled-key drift can weaken userspace control-flow protection.

### Test Signals
Build with/without ARM64_PTR_AUTH and ARM64_PTR_AUTH_KERNEL; run PAC prctl selftests, exec/fork key reset checks, context-switch stress, suspend/resume, and invalid-key ABI tests.
