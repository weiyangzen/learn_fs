# sources/distributed-fs/ceph-client/arch/arm64/include/asm/suspend.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/suspend.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/suspend.h` Defines CPU suspend/hibernate saved-state layouts and resume entry declarations. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
NR_CTX_REGS, NR_CALLEE_SAVED_REGS, struct cpu_suspend_ctx, struct sleep_stack_data, sleep_save_stash, cpu_suspend(), cpu_resume(), __cpu_suspend_enter/exit(), _cpu_resume(), swsusp_arch_suspend/resume(), hibernation header save/restore, hibernate_resume_nonboot_cpu_disable(). The file is 54 lines / 1695 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Suspend callers allocate sleep_stack_data on a valid stack, __cpu_suspend_enter saves system and callee-saved registers, firmware finisher powers down, and resume paths restore state before returning. Hibernation saves architecture headers and may resume on the original CPU.

### State, Persistence, And Dependencies
Persistent suspend state lives in stack-allocated sleep_stack_data until resume, sleep_save_stash, and hibernation image metadata. Depends on proc.S layout and PM/hibernation core; integrates PSCI/cpuidle suspend, CPU hotplug, hibernation, and low-level MMU resume.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Struct layout must match assembly exactly and remain 16-byte aligned; stack lifetime assumptions are critical across powerdown; wrong CPU resume can corrupt state.

### Test Signals
Run suspend-to-RAM, CPU idle deep states, hibernation, nonboot CPU resume, and objdump/layout checks against assembly offsets.
