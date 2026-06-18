# subset-b-000678 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/uaccess.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/uaccess.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/uaccess.h` defines arm64 user-access primitives: `get_user`/`put_user`, raw copy helpers, unsafe user access regions, privileged-access enable/disable hooks, TTBR0/PAN/MTE handling, and nofault kernel probes. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_UACCESS_H`, `access_ok`, `uaccess_mask_ptr`, `__get_mem_asm`, `__raw_get_mem`, `__raw_get_user`, `__get_user_error`, `__get_user`, `get_user`, `__get_kernel_nofault`, `__put_mem_asm`, `__raw_put_mem`, `__raw_put_user`, `__put_user_error`, `__put_user`, `put_user`, `__put_kernel_nofault`, `raw_copy_from_user`, `raw_copy_to_user`, `user_access_begin`, `user_access_end`, `arch_unsafe_put_user`, `arch_unsafe_get_user`, `unsafe_copy_loop`, `unsafe_copy_to_user`, `INLINE_COPY_TO_USER`, `INLINE_COPY_FROM_USER`, `clear_user`; functions/prototypes/exports: `access_ok`, `__uaccess_ttbr0_disable`, `__uaccess_ttbr0_enable`, `uaccess_ttbr0_disable`, `uaccess_ttbr0_enable`, `__uaccess_disable_hw_pan`, `__uaccess_enable_hw_pan`, `uaccess_disable_privileged`, `uaccess_enable_privileged`, `volatile`, `goto`, `user_access_begin`, `user_access_save`, `user_access_restore`, `__clear_user`, `copy_from_user_flushcache`, `probe_subpage_writeable`. The file is 503 lines / 14012 bytes. Direct includes are `asm/alternative.h`, `asm/kernel-pgtable.h`, `asm/sysreg.h`, `linux/bitops.h`, `linux/kasan-checks.h`, `linux/string.h`, `asm/asm-extable.h`, `asm/cpufeature.h`, `asm/mmu.h`, `asm/mte.h`, `asm/ptrace.h`, `asm/memory.h`, `asm/extable.h`, `asm-generic/access_ok.h`.

### Control Flow
Callers first pass through `access_ok` and size-specialized inline assembly. Faulting loads/stores are paired with exception-table fixups so a bad user pointer returns `-EFAULT` rather than taking the kernel down. Copy paths branch to arch copy/clear routines, while `user_access_begin/end` and `uaccess_ttbr0_enable/disable` toggle addressability around short critical sections.

### State, Persistence, And Dependencies
Notable global/static state symbols are `__gma_err`, `__gu_err`, `__pu_err`. The header does not persist data, but it temporarily changes CPU state such as PAN, UAO, TTBR0, and MTE tag-check override state. Correctness depends on exception tables and per-task address-limit assumptions owned by the memory-management and fault subsystems. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
The main risks are missing barriers around privileged user access, stale exception-table entries after inline assembly changes, wrong behavior on PAN/UAO/MTE combinations, and accidental user pointer dereference outside an enabled access window.

### Test Signals
Cross-build arm64 configs with PAN, UAO, KASAN, and MTE variants; run usercopy, nofault probe, hardened-usercopy, and fault-injection tests; inspect generated exception-table entries and copy helper disassembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd.h` connects arm64 syscall numbering to generated `unistd_64.h`, declares compatibility syscall feature wants, and defines the AArch32 private compatibility syscall range. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ARCH_WANT_COMPAT_STAT`, `__ARCH_WANT_COMPAT_STAT64`, `__ARCH_WANT_SYS_GETHOSTNAME`, `__ARCH_WANT_SYS_PAUSE`, `__ARCH_WANT_SYS_GETPGRP`, `__ARCH_WANT_SYS_NICE`, `__ARCH_WANT_SYS_SIGPENDING`, `__ARCH_WANT_SYS_SIGPROCMASK`, `__ARCH_WANT_COMPAT_SYS_SENDFILE`, `__ARCH_WANT_SYS_UTIME32`, `__ARCH_WANT_SYS_FORK`, `__ARCH_WANT_SYS_VFORK`, `__ARM_NR_COMPAT_BASE`, `__ARM_NR_compat_cacheflush`, `__ARM_NR_compat_set_tls`, `__ARM_NR_COMPAT_END`, `__ARCH_WANT_SYS_CLONE`, `__ARCH_WANT_NEW_STAT`, `NR_syscalls`. The file is 33 lines / 898 bytes. Direct includes are `asm/unistd_64.h`.

### Control Flow
There is no runtime control flow; syscall dispatch tables and generic syscall glue consume these macros at build time. The compat block is enabled only under `CONFIG_COMPAT`.

### State, Persistence, And Dependencies
The file contributes ABI constants only. Persistence is in the stable userspace/kernel syscall ABI, not in kernel storage. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
ABI drift between generated syscall tables, compat syscall numbers, and userspace headers can break seccomp, tracing, libc, or 32-bit process compatibility.

### Test Signals
Run arm64 and compat syscall table generation checks, build with and without `CONFIG_COMPAT`, and exercise syscall selftests and strace/seccomp decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd32.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd32.h` adapts the arm64 compat include path so the AArch32 `unistd_32.h` numbers are visible while preserving the historical ARM UAPI include guard name. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_ARM_UNISTD_H`, `__NR_sync_file_range2`. The file is 9 lines / 240 bytes. Direct includes are `asm/unistd_32.h`.

### Control Flow
The file is purely preprocessor glue. It defines the guard expected by included ARM headers and includes `asm/unistd_32.h`.

### State, Persistence, And Dependencies
No runtime state; the persistent contract is the 32-bit syscall ABI exposed to compat tasks. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Incorrect guard or include ordering can hide generated 32-bit syscall numbers or redefine symbols differently from ARM userspace expectations.

### Test Signals
Build compat syscall users, compare generated `__NR_*` values, and run AArch32 syscall selftests on an arm64 kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/uprobes.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/uprobes.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/uprobes.h` declares arm64 uprobes architecture state, breakpoint instruction constants, XOL slot sizing, and the single-step handler entry point. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_ASM_UPROBES_H`, `UPROBE_SWBP_INSN`, `UPROBE_SWBP_INSN_SIZE`, `UPROBE_XOL_SLOT_BYTES`; types: `arch_uprobe_task`, `arch_uprobe`, `arch_probe_insn`, `pt_regs`; functions/prototypes/exports: `uprobe_single_step_handler`. The file is 42 lines / 868 bytes. Direct includes are `asm/debug-monitors.h`, `asm/insn.h`, `asm/probes.h`.

### Control Flow
The generic uprobes core stores decoded arm64 probe instruction data in `struct arch_uprobe`, replaces probed userspace instructions with `UPROBE_SWBP_INSN`, executes the copied instruction from an XOL slot, then routes single-step completion through `uprobe_single_step_handler`.

### State, Persistence, And Dependencies
Notable global/static state symbols are `api`, `simulate`, `uprobe_brk_handler`, `uprobe_single_step_handler`. `arch_uprobe_task` tracks per-task probe execution state and `arch_uprobe` stores decoded probe metadata. State lives in uprobe/task structures, not persistent storage. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong instruction decode, breakpoint size, or XOL slot assumptions can corrupt userspace state, mis-handle PC-relative instructions, or leave threads stuck after single-step.

### Test Signals
Run uprobes/perf tests for A64 and compat tasks, test PC-relative and faulting instructions, and verify breakpoint restore across signal and exec paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/uprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso.h` defines arm64 vDSO page count and symbol lookup arithmetic used by kernel code that maps and patches the vDSO image. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_VDSO_H`, `__VDSO_PAGES`, `VDSO_SYMBOL`. The file is 24 lines / 470 bytes. Direct includes are `generated/vdso-offsets.h`.

### Control Flow
Runtime code passes generated vDSO offsets through `VDSO_SYMBOL` to locate symbols in the mapped image; this header supplies only the compile-time arithmetic.

### State, Persistence, And Dependencies
No storage is created here. It depends on generated `vdso-offsets.h` and the kernel's vDSO mapping data. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Mismatch between generated offsets, page count, and the linked vDSO image can break userspace fast time or signal trampoline entry.

### Test Signals
Build vDSO, run `readelf`/symbol offset checks, and execute vDSO clock/getcpu/selftests on arm64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/clocksource.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/clocksource.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/clocksource.h` declares the arm64 vDSO clocksource modes supported by this architecture, currently the architected timer mode. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_VDSOCLOCKSOURCE_H`, `VDSO_ARCH_CLOCKMODES`. The file is 11 lines / 316 bytes. There are no direct C include dependencies in this file.

### Control Flow
The generic vDSO time code checks these mode bits when deciding whether it can use the userspace fast path or must fall back to syscalls.

### State, Persistence, And Dependencies
No local state; clocksource mode is supplied through the vDSO data page by kernel timekeeping. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Advertising an unsupported or unstable clock mode would make vDSO time reads incorrect under migration, suspend, or unstable-counter conditions.

### Test Signals
Exercise clocksource watchdog, vDSO clock_gettime selftests, suspend/resume, and CPU migration with architected timer enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/compat_barrier.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/compat_barrier.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/compat_barrier.h` provides AArch32-compatible barrier instructions for the 32-bit compat vDSO build. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__COMPAT_BARRIER_H`, `dmb`, `aarch32_smp_mb`, `aarch32_smp_rmb`, `aarch32_smp_wmb`, `smp_mb`, `smp_rmb`, `smp_wmb`. The file is 36 lines / 755 bytes. There are no direct C include dependencies in this file.

### Control Flow
`smp_mb`, `smp_rmb`, and `smp_wmb` expand to AArch32 `dmb` assembly so compat vDSO seqlock reads observe kernel time data in order.

### State, Persistence, And Dependencies
No storage; it constrains CPU memory ordering for userspace vDSO code. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
A wrong barrier mnemonic or missing clobber can let compat vDSO readers observe torn timekeeper data.

### Test Signals
Build `CONFIG_COMPAT_VDSO`, disassemble barrier sites, and stress compat vDSO time reads across CPU migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/compat_barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/compat_gettimeofday.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/compat_gettimeofday.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/compat_gettimeofday.h` implements arm64's AArch32 vDSO clock and gettimeofday architecture hooks, including syscall fallbacks and virtual counter reads. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_VDSO_COMPAT_GETTIMEOFDAY_H`, `VDSO_HAS_CLOCK_GETRES`, `BUILD_VDSO32`, `__arch_get_vdso_u_time_data`, `vdso_clocksource_ok`; types: `timezone`, `__kernel_old_timeval`, `__kernel_timespec`, `old_timespec32`, `vdso_time_data`, `vdso_clock`; functions/prototypes/exports: `gettimeofday_fallback`, `volatile`, `clock_gettime_fallback`, `clock_gettime32_fallback`, `clock_getres_fallback`, `clock_getres32_fallback`, `__arch_get_hw_counter`, `vdso_clocksource_ok`. The file is 169 lines / 4338 bytes. Direct includes are `vdso/clocksource.h`, `vdso/time32.h`, `asm/barrier.h`, `asm/unistd_compat_32.h`, `asm/errno.h`, `asm/vdso/compat_barrier.h`.

### Control Flow
Compat vDSO callers read the time data page, validate the clock mode, read the architected counter with the correct barriers, and fall back to compat syscall numbers for unsupported clocks or invalid data.

### State, Persistence, And Dependencies
Notable global/static state symbols are `gettimeofday_fallback`, `clock_getres_fallback`, `clock_getres32_fallback`, `res`. State comes from the vDSO time data page and the hardware counter. The header itself only emits inline userspace code for the compat vDSO object. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Counter ordering, wrong compat syscall numbers, or stale clocksource validation can produce incorrect time or make fallback paths fail for 32-bit tasks.

### Test Signals
Run 32-bit vDSO clock_gettime/gettimeofday/getres tests, compare against syscall results, and test unstable clocksource fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/compat_gettimeofday.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/getrandom.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/getrandom.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/getrandom.h` supplies the arm64 vDSO getrandom fallback syscall shim used by generic vDSO random code. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_VDSO_GETRANDOM_H`; functions/prototypes/exports: `getrandom_syscall`, `volatile`. The file is 38 lines / 1011 bytes. Direct includes are `asm/unistd.h`, `asm/vdso/vsyscall.h`, `vdso/datapage.h`.

### Control Flow
When the vDSO random fast path cannot satisfy a request, `getrandom_syscall` issues `svc #0` with `__NR_getrandom` and returns the kernel result.

### State, Persistence, And Dependencies
Randomness state is in the kernel RNG and vDSO data page, not in this header. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Register constraint or syscall-number mistakes can corrupt arguments or silently fail random reads from userspace.

### Test Signals
Run getrandom vDSO selftests, compare fallback error handling with the real syscall, and disassemble the generated vDSO stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/getrandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/gettimeofday.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/gettimeofday.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/gettimeofday.h` implements native arm64 vDSO gettimeofday/clock_gettime architecture hooks, hardware counter reads, and syscall fallbacks. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_VDSO_GETTIMEOFDAY_H`, `VDSO_HAS_CLOCK_GETRES`, `__arch_get_vdso_u_time_data`; types: `timezone`, `__kernel_old_timeval`, `__kernel_timespec`, `vdso_time_data`; functions/prototypes/exports: `gettimeofday_fallback`, `volatile`, `clock_gettime_fallback`, `clock_getres_fallback`, `__arch_get_hw_counter`. The file is 109 lines / 2594 bytes. Direct includes are `vdso/clocksource.h`, `asm/alternative.h`, `asm/arch_timer.h`, `asm/barrier.h`, `asm/unistd.h`, `asm/sysreg.h`, `compat_gettimeofday.h`.

### Control Flow
The vDSO reads the shared time data page, verifies the clocksource mode, uses the architected timer counter with alternatives-aware sequences, and falls back through `svc #0` syscalls when the fast path is unavailable.

### State, Persistence, And Dependencies
Notable global/static state symbols are `gettimeofday_fallback`, `clock_getres_fallback`. The persistent contract is the vDSO data page updated by kernel timekeeping. Inline code temporarily reads system registers and depends on seqlock/barrier ordering. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Misordered counter reads, wrong alternatives patching, or syscall fallback ABI drift can cause time jumps or failures in libc fast paths.

### Test Signals
Run native vDSO selftests for `clock_gettime`, `gettimeofday`, and `clock_getres`; compare to syscalls under CPU hotplug, suspend/resume, and counter-frequency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/gettimeofday.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/processor.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/processor.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/processor.h` defines the vDSO-side `cpu_relax` primitive for busy-wait loops. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_VDSO_PROCESSOR_H`; functions/prototypes/exports: `cpu_relax`. The file is 17 lines / 309 bytes. There are no direct C include dependencies in this file.

### Control Flow
The helper emits the AArch64 `yield` instruction so userspace vDSO loops can hint to the CPU while polling.

### State, Persistence, And Dependencies
No state; it only changes scheduling/microarchitectural hint behavior. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong instruction selection would affect spin-wait efficiency or assembler compatibility, not persistent data.

### Test Signals
Build and disassemble vDSO objects and run vDSO seqlock stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/vsyscall.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/vsyscall.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/vsyscall.h` connects generic vDSO update code to arm64 precision masks and clock update hooks. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_VDSO_VSYSCALL_H`, `VDSO_PRECISION_MASK`, `__arch_update_vdso_clock`; types: `vdso_clock`; functions/prototypes/exports: `__arch_update_vdso_clock`. The file is 27 lines / 629 bytes. Direct includes are `vdso/datapage.h`, `asm-generic/vdso/vsyscall.h`.

### Control Flow
Kernel timekeeping calls the generic vDSO update path, while `__arch_update_vdso_clock` reports whether a clock mode remains acceptable for arm64 fast paths.

### State, Persistence, And Dependencies
State lives in the vDSO data page and timekeeper structures; this header defines arm64 masks and inline validation. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Incorrect precision masks or clock acceptance can make userspace read invalid fast-time data.

### Test Signals
Run timekeeping and vDSO selftests, validate clock mode transitions, and test fallback after clocksource changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso/vsyscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vectors.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vectors.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vectors.h` declares arm64 exception-vector aliases and branch-history-buffer hardening vector selection. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_VECTORS_H`, `EL1_VECTOR_BHB_LOOP`, `EL1_VECTOR_BHB_FW`, `EL1_VECTOR_BHB_CLEAR_INSN`, `TRAMP_VALIAS`; types: `arm64_bp_harden_el1_vectors`; functions/prototypes/exports: `arm64_get_bp_hardening_vector`. The file is 73 lines / 1785 bytes. Direct includes are `linux/bug.h`, `linux/percpu.h`, `asm/fixmap.h`.

### Control Flow
Exception entry and mitigation code select EL1 vector variants such as loop, firmware, or clear-instruction BHB hardening through `arm64_get_bp_hardening_vector`.

### State, Persistence, And Dependencies
State is per-CPU vector base selection and mitigation capability data owned by entry and CPU feature code. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong vector alias arithmetic or mitigation choice can break exception entry or leave branch-history hardening incomplete.

### Test Signals
Boot with affected CPU errata configs, inspect vector mappings, run Spectre/BHB mitigation checks, and exercise exception entry paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vectors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vermagic.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vermagic.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vermagic.h` adds the arm64 architecture token to module vermagic strings. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_ASM_VERMAGIC_H`, `MODULE_ARCH_VERMAGIC`. The file is 10 lines / 200 bytes. There are no direct C include dependencies in this file.

### Control Flow
Kbuild embeds `MODULE_ARCH_VERMAGIC` into modules so module loading can reject incompatible objects.

### State, Persistence, And Dependencies
No runtime storage beyond generated module metadata. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong vermagic would allow incompatible modules or reject valid arm64 modules.

### Test Signals
Build and load a simple module, check `modinfo vermagic`, and test cross-architecture rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vermagic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/virt.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/virt.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/virt.h` defines arm64 hypervisor-stub calls, boot exception-level state, and helpers for KVM/VHE/nVHE/protected-KVM mode detection. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM__VIRT_H`, `HVC_SET_VECTORS`, `HVC_SOFT_RESTART`, `HVC_RESET_VECTORS`, `HVC_FINALISE_EL2`, `HVC_GET_ICH_VTR_EL2`, `HVC_STUB_HCALL_NR`, `HVC_STUB_ERR`, `BOOT_CPU_MODE_EL1`, `BOOT_CPU_MODE_EL2`, `BOOT_CPU_FLAG_E2H`, `ARM64_VECTOR_TABLE_LEN`; functions/prototypes/exports: `is_pkvm_initialized`, `pkvm_force_reclaim_guest_page`, `is_hyp_mode_available`, `is_hyp_mode_mismatched`, `is_kernel_in_hyp_mode`, `has_vhe`, `is_protected_kvm_enabled`, `has_hvhe`, `is_hyp_nvhe`. The file is 180 lines / 4650 bytes. Direct includes are `asm/ptrace.h`, `asm/sections.h`, `asm/sysreg.h`, `asm/cpufeature.h`.

### Control Flow
Early boot records `__boot_cpu_mode`; KVM and low-level restart code use HVC stub numbers for vector setup, soft restart, EL2 finalization, and capability probes. Inline helpers branch on static keys, current EL, and final CPU capabilities.

### State, Persistence, And Dependencies
Notable global/static state symbols are `is_kvm_arm_initialised`, `pkvm_force_reclaim_guest_page`. `__boot_cpu_mode` and the protected-KVM static key are durable kernel state after boot. Helpers also read CPU system registers and final capability bitmaps. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Mixed EL boot, incorrect HVC numbers, or wrong VHE/nVHE tests can break KVM initialization, CPU restart, or protected-mode assumptions.

### Test Signals
Boot EL1 and EL2 configurations, run KVM selftests for VHE/nVHE/protected KVM, and validate CPU hotplug/restart vector reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/virt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmalloc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmalloc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmalloc.h` customizes arm64 vmalloc/vmap mapping sizes, huge-vmap support, contiguous PTE choices, and tagged vmalloc protections. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_ASM_ARM64_VMALLOC_H`, `arch_vmap_pud_supported`, `arch_vmap_pmd_supported`, `arch_vmap_pte_range_map_size`, `arch_vmap_pte_range_unmap_size`, `arch_vmap_pte_supported_shift`, `arch_vmap_pgprot_tagged`; functions/prototypes/exports: `arch_vmap_pud_supported`, `arch_vmap_pmd_supported`, `arch_vmap_pte_range_map_size`, `arch_vmap_pte_range_unmap_size`, `arch_vmap_pte_supported_shift`, `arch_vmap_pgprot_tagged`. The file is 74 lines / 1869 bytes. Direct includes are `asm/page.h`, `asm/pgtable.h`.

### Control Flow
Generic vmalloc asks these helpers whether PUD/PMD blocks are supported and what PTE range size to use. The PTE helper returns contiguous-PTE mappings only when size and virtual/physical alignment allow it.

### State, Persistence, And Dependencies
Notable global/static state symbols are `max_page_shift`. No local persistent state; decisions affect vmalloc page tables and TLB behavior maintained by the MM subsystem. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Bad alignment checks or unmap size detection can corrupt vmalloc mappings, leak stale TLB entries, or mishandle MTE-tagged vmalloc memory.

### Test Signals
Run vmalloc, module load, BPF JIT, huge-vmap, and KASAN/MTE tagged-vmalloc tests across page-size configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmap_stack.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmap_stack.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmap_stack.h` implements arm64 vmap-stack allocation with consistent alignment for stack overflow detection. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_VMAP_STACK_H`. The file is 25 lines / 641 bytes. Direct includes are `linux/gfp.h`, `linux/vmalloc.h`, `linux/pgtable.h`, `asm/memory.h`, `asm/thread_info.h`.

### Control Flow
`arch_alloc_vmap_stack` calls `__vmalloc_node` with `THREAD_ALIGN` and thread-info GFP flags, then resets KASAN tags before returning the stack pointer.

### State, Persistence, And Dependencies
Allocated stacks persist as vmalloc-backed kernel stacks owned by task/thread lifecycle code. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong alignment or tag reset can weaken overflow detection, confuse KASAN, or produce stacks incompatible with thread-info assumptions.

### Test Signals
Enable `CONFIG_VMAP_STACK`, KASAN, and guard pages; run fork/exit stress, stack overflow probes, and CPU hotplug workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmap_stack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vncr_mapping.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vncr_mapping.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vncr_mapping.h` documents byte offsets for virtualized nested control register state in the arm64 VNCR page. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ARM64_VNCR_MAPPING_H__`, `VNCR_VTTBR_EL2`, `VNCR_VTCR_EL2`, `VNCR_VMPIDR_EL2`, `VNCR_CNTVOFF_EL2`, `VNCR_HCR_EL2`, `VNCR_HSTR_EL2`, `VNCR_VPIDR_EL2`, `VNCR_TPIDR_EL2`, `VNCR_HCRX_EL2`, `VNCR_VNCR_EL2`, `VNCR_CPACR_EL1`, `VNCR_CONTEXTIDR_EL1`, `VNCR_SCTLR_EL1`, `VNCR_ACTLR_EL1`, `VNCR_TCR_EL1`, `VNCR_AFSR0_EL1`, `VNCR_AFSR1_EL1`, `VNCR_ESR_EL1`, `VNCR_MAIR_EL1`, `VNCR_AMAIR_EL1`, `VNCR_MDSCR_EL1`, `VNCR_SPSR_EL1`, `VNCR_CNTV_CVAL_EL0`, `VNCR_CNTV_CTL_EL0`, `VNCR_CNTP_CVAL_EL0`, `VNCR_CNTP_CTL_EL0`, `VNCR_SCXTNUM_EL1`, and 77 more. The file is 115 lines / 4042 bytes. There are no direct C include dependencies in this file.

### Control Flow
KVM and nested-virtualization code use these constants to index saved EL1/EL2, timer, GIC, trace, MPAM, and feature-control registers in the VNCR memory page.

### State, Persistence, And Dependencies
The offsets define layout for in-memory virtual CPU state. The header itself stores nothing but must remain synchronized with KVM save/restore code. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Any offset drift corrupts guest register state, especially for nested virtualization, virtual timer, GIC list registers, or trace/MPAM state.

### Test Signals
Run KVM nested-virtualization selftests, compare layout against architecture documentation, and exercise save/restore across vCPU migration and suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vncr_mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/word-at-a-time.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/word-at-a-time.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/word-at-a-time.h` provides arm64 word-at-a-time zero-byte detection and unaligned zeropad loading used by string and pathname helpers. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_WORD_AT_A_TIME_H`, `WORD_AT_A_TIME_CONSTANTS`, `prep_zero_mask`, `create_zero_mask`, `find_zero`; types: `word_at_a_time`; functions/prototypes/exports: `has_zero`, `zero_bytemask`, `load_unaligned_zeropad`. The file is 69 lines / 1539 bytes. Direct includes are `linux/uaccess.h`, `linux/bitops.h`, `linux/wordpart.h`, `asm-generic/word-at-a-time.h`.

### Control Flow
Little-endian builds use arithmetic masks to find zero bytes; big-endian builds include the generic implementation. `load_unaligned_zeropad` uses an exception-table-protected load with temporary MTE tag-check override.

### State, Persistence, And Dependencies
No persistent state. The helper briefly toggles MTE TCO state and relies on exception fixups for page-crossing loads. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Mask math, endian selection, or exception fixups can break string termination scans or fault incorrectly near page boundaries.

### Test Signals
Run string/pathname tests, page-boundary fault tests, KASAN/MTE builds, and compare little- and big-endian behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/word-at-a-time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/events.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/events.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/events.h` declares arm64 Xen event-channel helpers, IRQ-disable checks, and IPI vector mapping. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_ASM_ARM64_XEN_EVENTS_H`, `xchg_xen_ulong`; types: `ipi_vector`, `pt_regs`; functions/prototypes/exports: `xen_irqs_disabled`, `xen_support_evtchn_rebind`. The file is 28 lines / 547 bytes. Direct includes are `asm/ptrace.h`, `asm/atomic.h`.

### Control Flow
Xen event code uses an atomic exchange for Xen words, checks interrupt masking from `pt_regs`, and requests event-channel rebinding support.

### State, Persistence, And Dependencies
Event state is held by Xen interrupt/event-channel core structures; this header supplies arch-specific glue. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Incorrect atomic width or irq-state decoding can lose event-channel notifications or mishandle interrupt masking in guests.

### Test Signals
Boot Xen dom0/domU arm64 kernels, stress event channels and IPIs, and run CPU hotplug/rebind tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/hypercall.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/hypercall.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/hypercall.h` forwards arm64 Xen hypercall definitions to the shared `xen/arm/hypercall.h` header. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
no local C symbols beyond include or Kbuild directives. The file is 1 lines / 31 bytes. Direct includes are `xen/arm/hypercall.h`.

### Control Flow
There is no local runtime flow; the preprocessor redirects include users to the shared ARM Xen implementation.

### State, Persistence, And Dependencies
No local state. State and ABI behavior are defined by the included Xen ARM header and its consumers. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
The risk is include-path or API drift between arm64 and shared Xen ARM headers, which can break guest, dom0, DMA, or hypercall builds.

### Test Signals
Build arm64 Xen guest/dom0 configurations and compile event-channel, hypercall, SWIOTLB, grant-table, and Xen ops users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/hypercall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/hypervisor.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/hypervisor.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/hypervisor.h` forwards arm64 Xen hypervisor declarations to the shared `xen/arm/hypervisor.h` header. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
no local C symbols beyond include or Kbuild directives. The file is 1 lines / 32 bytes. Direct includes are `xen/arm/hypervisor.h`.

### Control Flow
There is no local runtime flow; the preprocessor redirects include users to the shared ARM Xen implementation.

### State, Persistence, And Dependencies
No local state. State and ABI behavior are defined by the included Xen ARM header and its consumers. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
The risk is include-path or API drift between arm64 and shared Xen ARM headers, which can break guest, dom0, DMA, or hypercall builds.

### Test Signals
Build arm64 Xen guest/dom0 configurations and compile event-channel, hypercall, SWIOTLB, grant-table, and Xen ops users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/hypervisor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/interface.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/interface.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/interface.h` forwards arm64 Xen public interface definitions to the shared `xen/arm/interface.h` header. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
no local C symbols beyond include or Kbuild directives. The file is 1 lines / 31 bytes. Direct includes are `xen/arm/interface.h`.

### Control Flow
There is no local runtime flow; the preprocessor redirects include users to the shared ARM Xen implementation.

### State, Persistence, And Dependencies
No local state. State and ABI behavior are defined by the included Xen ARM header and its consumers. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
The risk is include-path or API drift between arm64 and shared Xen ARM headers, which can break guest, dom0, DMA, or hypercall builds.

### Test Signals
Build arm64 Xen guest/dom0 configurations and compile event-channel, hypercall, SWIOTLB, grant-table, and Xen ops users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/page.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/page.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/page.h` includes Xen ARM page helpers and declares whether the Xen kernel mapping is unmapped at user mode. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
functions/prototypes/exports: `xen_kernel_unmapped_at_usr`. The file is 7 lines / 144 bytes. Direct includes are `xen/arm/page.h`, `asm/mmu.h`.

### Control Flow
Xen MM paths include this file to obtain ARM page translation helpers plus the arm64 `xen_kernel_unmapped_at_usr` hook.

### State, Persistence, And Dependencies
No local state beyond the external mapping-status helper. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Mismatch with arm64 KPTI/user-unmapped behavior can break Xen page sharing or grant-table address assumptions.

### Test Signals
Build Xen arm64 configurations and run grant-table, ballooning, and KPTI/user access tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/swiotlb-xen.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/swiotlb-xen.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/swiotlb-xen.h` forwards Xen SWIOTLB declarations to the shared ARM Xen DMA bounce-buffer header. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
no local C symbols beyond include or Kbuild directives. The file is 1 lines / 33 bytes. Direct includes are `xen/arm/swiotlb-xen.h`.

### Control Flow
There is no local runtime flow; the preprocessor redirects include users to the shared ARM Xen implementation.

### State, Persistence, And Dependencies
No local state. State and ABI behavior are defined by the included Xen ARM header and its consumers. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
The risk is include-path or API drift between arm64 and shared Xen ARM headers, which can break guest, dom0, DMA, or hypercall builds.

### Test Signals
Build arm64 Xen guest/dom0 configurations and compile event-channel, hypercall, SWIOTLB, grant-table, and Xen ops users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/swiotlb-xen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/xen-ops.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/xen-ops.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/xen-ops.h` forwards Xen operation declarations to the shared ARM Xen operations header. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
no local C symbols beyond include or Kbuild directives. The file is 2 lines / 68 bytes. Direct includes are `xen/arm/xen-ops.h`.

### Control Flow
There is no local runtime flow; the preprocessor redirects include users to the shared ARM Xen implementation.

### State, Persistence, And Dependencies
No local state. State and ABI behavior are defined by the included Xen ARM header and its consumers. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
The risk is include-path or API drift between arm64 and shared Xen ARM headers, which can break guest, dom0, DMA, or hypercall builds.

### Test Signals
Build arm64 Xen guest/dom0 configurations and compile event-channel, hypercall, SWIOTLB, grant-table, and Xen ops users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/xen/xen-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/Kbuild -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/Kbuild

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/Kbuild` selects generic UAPI headers for arm64 that do not need architecture-specific copies: errno, ioctl, ioctls, and ipcbuf. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
UAPI export directives: `syscall-y += unistd_64.h`, `generic-y += kvm_para.h`. The file is 4 lines / 85 bytes. Dependencies are the generic UAPI headers selected by `generic-y`.

### Control Flow
Kbuild consumes `generic-y` lines while exporting sanitized UAPI headers to userspace.

### State, Persistence, And Dependencies
No runtime state; the output is the installed UAPI header set. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Dropping a generic entry can break userspace header installation or produce missing includes for libc/kernel header consumers.

### Test Signals
Run headers_install, compile UAPI consumers, and compare generated include tree for missing generic headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/auxvec.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/auxvec.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/auxvec.h` defines arm64 auxiliary-vector entries for the vDSO base and minimum signal stack size. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_AUXVEC_H`, `AT_SYSINFO_EHDR`, `AT_MINSIGSTKSZ`, `AT_VECTOR_SIZE_ARCH`. The file is 26 lines / 912 bytes. There are no direct C include dependencies in this file.

### Control Flow
ELF exec code emits these constants into each new process auxv so libc can find the vDSO and size signal stacks.

### State, Persistence, And Dependencies
The values persist per process in the initial userspace auxiliary vector. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong auxv numbering breaks libc vDSO discovery or signal-stack sizing.

### Test Signals
Run exec/auxv selftests and inspect `/proc/self/auxv` for `AT_SYSINFO_EHDR` and `AT_MINSIGSTKSZ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bitsperlong.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bitsperlong.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bitsperlong.h` sets arm64 UAPI `__BITS_PER_LONG` to 64 for native userspace and then includes the generic definition fallback. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_BITSPERLONG_H`, `__BITS_PER_LONG`. The file is 29 lines / 960 bytes. Direct includes are `asm-generic/bitsperlong.h`.

### Control Flow
Userspace and sanitized kernel headers consume this compile-time constant when sizing long-based ABI structures.

### State, Persistence, And Dependencies
No runtime state; it is a C ABI sizing contract. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
A wrong value changes structure layouts and ioctl ABI on native arm64.

### Test Signals
Build native and compat UAPI consumers and run ABI layout checks for long-sized structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bpf_perf_event.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bpf_perf_event.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bpf_perf_event.h` exposes the arm64 perf-event register type to BPF programs by including the UAPI ptrace register definitions. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_BPF_PERF_EVENT_H__`; types: `user_pt_regs`. The file is 9 lines / 257 bytes. Direct includes are `asm/ptrace.h`.

### Control Flow
BPF/perf tooling includes this header to interpret sampled register state.

### State, Persistence, And Dependencies
No local state; state is the perf sample context supplied to BPF programs. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Incorrect register type exposure can break BPF stack/register inspection on arm64.

### Test Signals
Run BPF perf-event selftests and compile libbpf programs that read `struct pt_regs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bpf_perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/byteorder.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/byteorder.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/byteorder.h` selects arm64 UAPI byte order by including the big- or little-endian Linux byteorder header based on `__AARCH64EB__`. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_BYTEORDER_H`. The file is 26 lines / 887 bytes. Direct includes are `linux/byteorder/big_endian.h`, `linux/byteorder/little_endian.h`.

### Control Flow
Preprocessor selection happens at userspace or kernel build time.

### State, Persistence, And Dependencies
No runtime state; this controls compile-time endian conversions. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong endian selection corrupts UAPI structure interpretation and network/storage metadata handling.

### Test Signals
Build little- and big-endian arm64 UAPI consumers and run endian conversion compile tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/fcntl.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/fcntl.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/fcntl.h` defines arm64-specific open flag values for directory/no-follow/direct/large-file behavior before including generic fcntl definitions. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_FCNTL_H`, `O_DIRECTORY`, `O_NOFOLLOW`, `O_DIRECT`, `O_LARGEFILE`. The file is 30 lines / 1045 bytes. Direct includes are `asm-generic/fcntl.h`.

### Control Flow
Userspace passes these bit values into file-related syscalls; VFS and compat layers decode them according to this ABI.

### State, Persistence, And Dependencies
No local state; the values are syscall ABI constants. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Changing values breaks binary compatibility with existing userspace and file-opening semantics.

### Test Signals
Run open/fcntl selftests, libc header ABI checks, and compat flag translation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/hwcap.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/hwcap.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/hwcap.h` defines arm64 `AT_HWCAP` and `AT_HWCAP2` feature bits for FP/SIMD, crypto, atomics, SVE/SME, pointer auth, MTE, RNG, and newer architectural extensions. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_HWCAP_H`, `HWCAP_FP`, `HWCAP_ASIMD`, `HWCAP_EVTSTRM`, `HWCAP_AES`, `HWCAP_PMULL`, `HWCAP_SHA1`, `HWCAP_SHA2`, `HWCAP_CRC32`, `HWCAP_ATOMICS`, `HWCAP_FPHP`, `HWCAP_ASIMDHP`, `HWCAP_CPUID`, `HWCAP_ASIMDRDM`, `HWCAP_JSCVT`, `HWCAP_FCMA`, `HWCAP_LRCPC`, `HWCAP_DCPOP`, `HWCAP_SHA3`, `HWCAP_SM3`, `HWCAP_SM4`, `HWCAP_ASIMDDP`, `HWCAP_SHA512`, `HWCAP_SVE`, `HWCAP_ASIMDFHM`, `HWCAP_DIT`, `HWCAP_USCAT`, `HWCAP_ILRCPC`, and 89 more. The file is 151 lines / 4859 bytes. There are no direct C include dependencies in this file.

### Control Flow
CPU feature detection populates these bitmaps during exec; userspace libraries use them to select optimized code paths.

### State, Persistence, And Dependencies
The capability bits persist per process in auxv and are derived from system-wide CPU feature state. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Advertising unsupported features can crash optimized userspace; omitting supported bits can disable performance paths or feature tests.

### Test Signals
Run cpufeature and hwcap selftests, compare `/proc/cpuinfo`/auxv exposure, and test heterogeneous CPU systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/hwcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/kvm.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/kvm.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/kvm.h` defines the arm64 KVM userspace ABI: register layouts, vCPU initialization features, VGIC addresses, debug state, device attributes, MTE tag copy, counter offsets, and one-reg encodings. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ARM_KVM_H__`, `KVM_SPSR_EL1`, `KVM_SPSR_SVC`, `KVM_SPSR_ABT`, `KVM_SPSR_UND`, `KVM_SPSR_IRQ`, `KVM_SPSR_FIQ`, `KVM_NR_SPSR`, `__KVM_HAVE_IRQ_LINE`, `__KVM_HAVE_VCPU_EVENTS`, `KVM_COALESCED_MMIO_PAGE_OFFSET`, `KVM_DIRTY_LOG_PAGE_OFFSET`, `KVM_ARM_TARGET_AEM_V8`, `KVM_ARM_TARGET_FOUNDATION_V8`, `KVM_ARM_TARGET_CORTEX_A57`, `KVM_ARM_TARGET_XGENE_POTENZA`, `KVM_ARM_TARGET_CORTEX_A53`, `KVM_ARM_TARGET_GENERIC_V8`, `KVM_ARM_NUM_TARGETS`, `KVM_ARM_DEVICE_TYPE_SHIFT`, `KVM_ARM_DEVICE_TYPE_MASK`, `KVM_ARM_DEVICE_ID_SHIFT`, `KVM_ARM_DEVICE_ID_MASK`, `KVM_ARM_DEVICE_VGIC_V2`, `KVM_VGIC_V2_ADDR_TYPE_DIST`, `KVM_VGIC_V2_ADDR_TYPE_CPU`, `KVM_VGIC_V2_DIST_SIZE`, `KVM_VGIC_V2_CPU_SIZE`, and 169 more; types: `kvm_regs`, `user_pt_regs`, `user_fpsimd_state`, `kvm_vcpu_init`, `kvm_sregs`, `kvm_fpu`, `kvm_guest_debug_arch`, `kvm_debug_exit_arch`, `kvm_sync_regs`, `kvm_pmu_event_filter`, `kvm_vcpu_events`, `kvm_arm_copy_mte_tags`, `kvm_arm_counter_offset`, `kvm_smccc_filter_action`, `kvm_smccc_filter`, `reg_mask_range`. The file is 564 lines / 18178 bytes. Direct includes are `linux/psci.h`, `linux/types.h`, `asm/ptrace.h`, `asm/sve_context.h`.

### Control Flow
Userspace VMMs pass these structures through KVM ioctls to create vCPUs, configure interrupts/timers/PMU/SVE/ptrauth/nested virtualization, inspect exits, and synchronize device IRQ levels.

### State, Persistence, And Dependencies
Notable global/static state symbols are `regs`, `fp_regs`. These structures are the persistent ABI between VMM processes and in-kernel KVM vCPU/VM state. The header must remain backwards compatible. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Layout, alignment, or constant changes can break QEMU, crosvm, cloud hypervisors, migration streams, or debug tools.

### Test Signals
Run KVM selftests, QEMU boot tests with GICv2/v3, PMU, SVE, MTE, ptrauth, nested virtualization, and ABI compile checks against userspace VMMs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/mman.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/mman.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/mman.h` adds arm64 memory-protection flags for BTI and MTE plus execute/read pkey mask values before including generic mmap definitions. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_MMAN_H`, `PROT_BTI`, `PROT_MTE`, `PKEY_DISABLE_EXECUTE`, `PKEY_DISABLE_READ`, `PKEY_ACCESS_MASK`. The file is 19 lines / 552 bytes. Direct includes are `asm-generic/mman.h`.

### Control Flow
Userspace passes these flags to `mmap`, `mprotect`, and pkey APIs; MM code validates and applies BTI/MTE permissions to VMAs.

### State, Persistence, And Dependencies
Flags persist in VMA permissions and page-table attributes. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong values or masks break BTI landing-pad enforcement, MTE tag checking, or pkey permission semantics.

### Test Signals
Run `mmap`/`mprotect`, BTI, MTE, and pkey selftests on supporting hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/param.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/param.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/param.h` sets arm64 `EXEC_PAGESIZE` to 65536 and inherits generic system parameter definitions. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_PARAM_H`, `EXEC_PAGESIZE`. The file is 24 lines / 798 bytes. Direct includes are `asm-generic/param.h`.

### Control Flow
Userspace headers and exec-related code consume this constant at compile time.

### State, Persistence, And Dependencies
No runtime state; it is an ABI-visible parameter. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Changing it can affect userspace assumptions about executable page sizing.

### Test Signals
Run headers_install and compile libc/kernel-header users that include asm param definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/perf_regs.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/perf_regs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/perf_regs.h` enumerates arm64 perf register IDs from x0-x30 through SP, PC, PSTATE, and max sentinel values. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_ASM_ARM64_PERF_REGS_H`, `PERF_REG_EXTENDED_MASK`; types: `perf_event_arm_regs`. The file is 48 lines / 1070 bytes. There are no direct C include dependencies in this file.

### Control Flow
perf sample collection and unwinding code use the enum and masks to select which registers are captured or exposed to tooling.

### State, Persistence, And Dependencies
Register samples live in perf event records; this header fixes their numeric ABI. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Renumbering registers breaks perf data interpretation, BPF perf programs, and unwinder tooling.

### Test Signals
Run perf register sampling tests, `perf record --intr-regs`, and BPF stack/register selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/posix_types.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/posix_types.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/posix_types.h` defines arm64 legacy UID type width and includes generic POSIX UAPI type definitions. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_POSIX_TYPES_H`, `__kernel_old_uid_t`. The file is 11 lines / 325 bytes. Direct includes are `asm-generic/posix_types.h`.

### Control Flow
Compilation only; syscall and filesystem ABI structures include these type definitions.

### State, Persistence, And Dependencies
No local state; it controls userspace-visible C type layout. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Type-width drift breaks stat, ownership, and ioctl ABI compatibility.

### Test Signals
Run UAPI header compile tests and ABI layout checks for POSIX types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ptrace.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ptrace.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ptrace.h` defines arm64 ptrace-visible processor state, PSR bits, syscall-emulation requests, MTE tag ptrace requests, SVE ptrace layout macros, and user register structures. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_PTRACE_H`, `PSR_MODE_EL0t`, `PSR_MODE_EL1t`, `PSR_MODE_EL1h`, `PSR_MODE_EL2t`, `PSR_MODE_EL2h`, `PSR_MODE_EL3t`, `PSR_MODE_EL3h`, `PSR_MODE_MASK`, `PSR_MODE32_BIT`, `PSR_F_BIT`, `PSR_I_BIT`, `PSR_A_BIT`, `PSR_D_BIT`, `PSR_BTYPE_MASK`, `PSR_SSBS_BIT`, `PSR_PAN_BIT`, `PSR_UAO_BIT`, `PSR_DIT_BIT`, `PSR_TCO_BIT`, `PSR_V_BIT`, `PSR_C_BIT`, `PSR_Z_BIT`, `PSR_N_BIT`, `PSR_BTYPE_SHIFT`, `PSR_f`, `PSR_s`, `PSR_x`, and 40 more; types: `user_pt_regs`, `user_fpsimd_state`, `user_hwdebug_state`, `user_sve_header`, `user_pac_mask`, `user_pac_address_keys`, `user_pac_generic_keys`, `user_za_header`, `user_gcs`. The file is 337 lines / 9799 bytes. Direct includes are `linux/types.h`, `asm/hwcap.h`, `asm/sve_context.h`.

### Control Flow
ptrace, signal, core-dump, perf, and debugger paths use these structures and constants to exchange register state with userspace.

### State, Persistence, And Dependencies
Register snapshots persist in ptrace stops, signal frames, core files, and perf samples. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Layout or flag mistakes break debuggers, crash dump tools, seccomp tracers, MTE tag inspection, or SVE vector-length handling.

### Test Signals
Run ptrace, gdb, seccomp, core-dump, SVE, and MTE tag selftests on native and compat processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/setup.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/setup.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/setup.h` defines the arm64 kernel command-line buffer size exposed to UAPI consumers. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_SETUP_H`, `COMMAND_LINE_SIZE`. The file is 27 lines / 879 bytes. Direct includes are `linux/types.h`.

### Control Flow
Boot and setup code use this sizing contract while userspace tools include it for architecture constants.

### State, Persistence, And Dependencies
The command line is boot-time kernel state; this header only defines the maximum size constant. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Size mismatches can truncate boot arguments or desynchronize tooling assumptions.

### Test Signals
Boot with long command lines and run headers_install compile checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/sigcontext.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/sigcontext.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/sigcontext.h` defines the arm64 signal-frame ABI, including general registers, FPSIMD, ESR, extra context records, SVE/SME ZA/ZT, TPIDR2, FPMR, GCS, and vector-length layout macros. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_SIGCONTEXT_H`, `FPSIMD_MAGIC`, `ESR_MAGIC`, `POE_MAGIC`, `EXTRA_MAGIC`, `SVE_MAGIC`, `SVE_SIG_FLAG_SM`, `TPIDR2_MAGIC`, `FPMR_MAGIC`, `ZA_MAGIC`, `ZT_MAGIC`, `GCS_MAGIC`, `SVE_VQ_BYTES`, `SVE_VQ_MIN`, `SVE_VQ_MAX`, `SVE_VL_MIN`, `SVE_VL_MAX`, `SVE_NUM_ZREGS`, `SVE_NUM_PREGS`, `sve_vl_valid`, `sve_vq_from_vl`, `sve_vl_from_vq`, `SVE_SIG_ZREG_SIZE`, `SVE_SIG_PREG_SIZE`, `SVE_SIG_FFR_SIZE`, `SVE_SIG_REGS_OFFSET`, `SVE_SIG_ZREGS_OFFSET`, `SVE_SIG_ZREG_OFFSET`, and 16 more; types: `sigcontext`, `_aarch64_ctx`, `fpsimd_context`, `esr_context`, `poe_context`, `extra_context`, `sve_context`, `tpidr2_context`, `fpmr_context`, `za_context`, `zt_context`, `gcs_context`. The file is 358 lines / 11386 bytes. Direct includes are `linux/types.h`, `asm/sve_context.h`.

### Control Flow
Signal delivery writes these records to the user stack and sigreturn parses them to restore task state. Optional records are chained with `_aarch64_ctx` headers and may extend beyond the base reserved area.

### State, Persistence, And Dependencies
Notable global/static state symbols are `head`. Signal context persists on the userspace signal stack until the handler returns or the process inspects/modifies it. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Record sizing, alignment, or magic-number drift breaks signal return, debuggers, checkpoint/restore, SVE/SME state preservation, and forward compatibility.

### Test Signals
Run signal, sigaltstack, SVE/SME, ZA/ZT, GCS, FPSIMD, and checkpoint/restore tests with varying vector lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/signal.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/signal.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/signal.h` sets arm64 signal ABI constants for `SA_RESTORER`, minimum signal stack size, and default signal stack size before including generic signal definitions. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_SIGNAL_H`, `SA_RESTORER`, `MINSIGSTKSZ`, `SIGSTKSZ`. The file is 28 lines / 898 bytes. Direct includes are `asm-generic/signal.h`.

### Control Flow
Signal setup and libc signal APIs use these constants when installing handlers and allocating alternate stacks.

### State, Persistence, And Dependencies
Signal stack choices persist in per-task signal state after `sigaltstack`. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Too-small stack constants can overflow with SVE/SME signal records; flag drift breaks handler installation ABI.

### Test Signals
Run signal-stack selftests with large vector states and libc signal API compile checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/statfs.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/statfs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/statfs.h` defines arm64 compat `statfs64` packing behavior and includes generic statfs definitions. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_STATFS_H`, `ARCH_PACK_COMPAT_STATFS64`. The file is 24 lines / 842 bytes. Direct includes are `asm-generic/statfs.h`.

### Control Flow
Filesystem syscalls and compat translation code use the packing macro for statfs structures.

### State, Persistence, And Dependencies
No local state; the ABI affects syscall result layout. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Packing mismatch breaks 32-bit userspace filesystem statistics on arm64 kernels.

### Test Signals
Run statfs/fstatfs tests from native and compat userspace and compare structure sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/statfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/sve_context.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/sve_context.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/sve_context.h` defines shared SVE vector-length constants and layout helper macros used by ptrace and signal UAPI headers. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_SVE_CONTEXT_H`, `__SVE_VQ_BYTES`, `__SVE_VQ_MIN`, `__SVE_VQ_MAX`, `__SVE_VL_MIN`, `__SVE_VL_MAX`, `__SVE_NUM_ZREGS`, `__SVE_NUM_PREGS`, `__sve_vl_valid`, `__sve_vq_from_vl`, `__sve_vl_from_vq`, `__SVE_ZREG_SIZE`, `__SVE_PREG_SIZE`, `__SVE_FFR_SIZE`, `__SVE_ZREGS_OFFSET`, `__SVE_ZREG_OFFSET`, `__SVE_ZREGS_SIZE`, `__SVE_PREGS_OFFSET`, `__SVE_PREG_OFFSET`, `__SVE_PREGS_SIZE`, `__SVE_FFR_OFFSET`. The file is 64 lines / 2004 bytes. Direct includes are `linux/types.h`.

### Control Flow
Compile-time macros calculate register offsets and sizes from vector length or vector quadword count.

### State, Persistence, And Dependencies
No local state; the values describe SVE state stored elsewhere in signal frames or ptrace buffers. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Bad size arithmetic causes buffer overruns or truncated SVE state for debuggers and signal handlers.

### Test Signals
Run SVE ptrace and signal tests for minimum, maximum, and odd vector lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/sve_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ucontext.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ucontext.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ucontext.h` defines arm64 `ucontext` as exposed to userspace signal handlers, including flags, link pointer, stack, signal mask, and machine context. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_UCONTEXT_H`; types: `ucontext`, `sigcontext`. The file is 33 lines / 1081 bytes. Direct includes are `linux/types.h`.

### Control Flow
Signal delivery fills this structure and user handlers pass it to APIs such as `getcontext`-style consumers or sigreturn paths.

### State, Persistence, And Dependencies
Notable global/static state symbols are `uc_mcontext`. The structure persists on the signal stack while a handler executes. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Layout drift breaks libc, debuggers, language runtimes, and signal-handler context inspection.

### Test Signals
Run signal/ucontext ABI tests and compile libc consumers against installed headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/unistd.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/unistd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/unistd.h` includes generated native arm64 syscall numbers from `asm/unistd_64.h` for the exported UAPI header set. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
no local C symbols beyond include or Kbuild directives. The file is 2 lines / 90 bytes. Direct includes are `asm/unistd_64.h`.

### Control Flow
There is no runtime control flow; headers_install and userspace builds consume the generated syscall constants.

### State, Persistence, And Dependencies
No local state; the stable syscall number ABI is the persistent contract. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Generated syscall header drift breaks libc, seccomp, ptrace, and syscall dispatch tooling.

### Test Signals
Run headers_install, compile syscall users, and compare native arm64 `__NR_*` values against the generated syscall table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/Makefile

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/Makefile` selects arm64 kernel objects and per-object instrumentation flags for entry code, CPU feature handling, ACPI, KVM-adjacent support, vDSO wrapping, tracing, modules, kexec, hibernation, and platform features. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
Kbuild selections include `CFLAGS_armv8_deprecated.o := -I$(src)`, `CFLAGS_REMOVE_ftrace.o = $(CC_FLAGS_FTRACE)`, `CFLAGS_REMOVE_insn.o = $(CC_FLAGS_FTRACE)`, `CFLAGS_REMOVE_return_address.o = $(CC_FLAGS_FTRACE)`, `CFLAGS_REMOVE_syscall.o = -fstack-protector -fstack-protector-strong`, `CFLAGS_syscall.o += -fno-stack-protector`, `KASAN_SANITIZE_stacktrace.o := n`, `KCOV_INSTRUMENT_entry-common.o := n`, `KCOV_INSTRUMENT_idle.o := n`, `obj-y := debug-monitors.o entry.o irq.o fpsimd.o \`, `entry-common.o entry-fpsimd.o process.o ptrace.o \`, `setup.o signal.o sys.o stacktrace.o time.o traps.o \`, `io.o vdso.o hyp-stub.o psci.o cpu_ops.o \`, `return_address.o cpuinfo.o cpu_errata.o \`, `cpufeature.o alternative.o cacheinfo.o \`, `smp.o smp_spin_table.o topology.o smccc-call.o \`, `syscall.o proton-pack.o idle.o patching.o pi/ \`, `rsi.o jump_label.o`, `obj-$(CONFIG_COMPAT) += sys32.o signal32.o \`, `sys_compat.o`, `obj-$(CONFIG_COMPAT) += sigreturn32.o`, `obj-$(CONFIG_COMPAT_ALIGNMENT_FIXUPS) += compat_alignment.o`, `obj-$(CONFIG_KUSER_HELPERS) += kuser32.o`, `obj-$(CONFIG_FUNCTION_TRACER) += ftrace.o entry-ftrace.o`, and 39 more. The file is 89 lines / 3473 bytes. Dependencies are Kconfig symbols, Kbuild variables, generated vDSO objects, and per-object instrumentation flags.

### Control Flow
Kbuild evaluates `obj-y` and `obj-$(CONFIG_*)` lines to choose translation units, disables selected tracing/sanitizer instrumentation for fragile low-level files, and adds vDSO object dependencies.

### State, Persistence, And Dependencies
No runtime state; the persistent output is the set of compiled objects and generated dependencies in the kernel build tree. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Incorrect object selection or instrumentation can omit boot-critical code, instrument `noinstr` paths unsafely, or break vDSO/kexec/module builds.

### Test Signals
Build defconfig, allmodconfig, ACPI, compat, kexec, hibernation, tracing, KASAN, KCOV, and module configurations; verify vDSO wrap dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi.c` implements arm64 ACPI boot enablement, FADT validation, table mapping, PSCI detection, ACPI memory mapping attributes, SEA handling, memory reservation, and CPU UID mapping. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `pr_fmt`; types: `acpi_table_header`, `acpi_table_fadt`, `acpi_madt_generic_interrupt`, `acpi_table_facs`, `pt_regs`; functions/prototypes/exports: `parse_acpi`, `dt_is_stub`, `__acpi_unmap_table`, `acpi_psci_present`, `acpi_psci_use_hvc`, `acpi_fadt_sanity_check`, `acpi_boot_table_init`, `__acpi_get_writethrough_mem_attribute`, `__acpi_get_mem_attribute`, `apei_claim_sea`, `arch_reserve_mem_area`, `acpi_map_cpu`, `acpi_unmap_cpu`, `acpi_get_cpu_uid`, `get_cpu_for_acpi_id`, `acpi_disabled`, `acpi_pci_disabled`. The file is 490 lines / 13059 bytes. Direct includes are `linux/acpi.h`, `linux/arm-smccc.h`, `linux/cpumask.h`, `linux/efi.h`, `linux/efi-bgrt.h`, `linux/init.h`, `linux/irq.h`, `linux/irqdomain.h`, `linux/irq_work.h`, `linux/memblock.h`, `linux/of_fdt.h`, `linux/libfdt.h`, `linux/smp.h`, `linux/serial_core.h`, `linux/suspend.h`, `linux/pgtable.h`, `acpi/ghes.h`, `acpi/processor.h`, `asm/cputype.h`, `asm/cpu_ops.h`, `asm/daifflags.h`, `asm/smp_plat.h`.

### Control Flow
`parse_acpi` records boot parameters, `acpi_boot_table_init` arbitrates ACPI versus DT and validates the FADT, `acpi_os_ioremap` maps ACPI-described memory with attribute selection, and CPU helpers map MADT processor identifiers to logical CPUs.

### State, Persistence, And Dependencies
Notable global/static state symbols are `acpi_noirq`, `acpi_disabled`, `acpi_pci_disabled`, `param_acpi_off`, `param_acpi_on`, `param_acpi_force`, `param_acpi_nospcr`, `__init`, `node`, `acpi_psci_use_hvc`, `ret`, `attr`, `end`, `apei_claim_sea`, `err`, `return_to_irqs_enabled`, `acpi_map_cpu`, `acpi_unmap_cpu`, and 3 more. Global ACPI enable flags, boot parameters, FADT-derived PSCI state, memblock reservations, and ACPI processor mappings persist after boot. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
ACPI/DT arbitration mistakes, unsafe memory attributes, bad PSCI conduit detection, or incorrect ACPI CPU IDs can break boot, CPU hotplug, PCI/IRQ setup, or firmware error handling.

### Test Signals
Boot with `acpi=off`, `on`, and `force`; validate FADT/SPCR/MADT tables, GHES SEA handling, CPU mapping, memblock reservations, and ACPI ioremap attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_numa.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_numa.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_numa.c` maps arm64 ACPI SRAT/GICC proximity data into NUMA node assignments for CPUs. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `pr_fmt`; types: `acpi_srat_gicc_affinity`, `acpi_table_srat`; functions/prototypes/exports: `acpi_numa_get_nid`, `acpi_parse_gicc_pxm`, `acpi_map_cpus_to_nodes`, `acpi_numa_gicc_affinity_init`. The file is 109 lines / 2656 bytes. Direct includes are `linux/acpi.h`, `linux/bitmap.h`, `linux/kernel.h`, `linux/mm.h`, `linux/memblock.h`, `linux/mmzone.h`, `linux/module.h`, `linux/topology.h`, `asm/numa.h`.

### Control Flow
SRAT parsing records early CPU-to-node IDs, then `acpi_map_cpus_to_nodes` applies those IDs during NUMA setup; invalid proximity domains fall back to `NUMA_NO_NODE`.

### State, Persistence, And Dependencies
Notable global/static state symbols are `acpi_early_node_map`, `__init`, `cpu`, `pxm`. `acpi_early_node_map` is early boot state that seeds per-CPU NUMA topology. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Bad ACPI table validation or missing UID matches can place CPUs on wrong nodes, degrading scheduling and memory locality.

### Test Signals
Boot ACPI NUMA systems, inspect CPU node maps, run NUMA balancing tests, and validate SRAT parser error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_parking_protocol.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_parking_protocol.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_parking_protocol.c` implements the deprecated ACPI parking protocol CPU bring-up method for arm64 secondary CPUs. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
types: `parking_protocol_mailbox`, `cpu_mailbox_entry`, `acpi_madt_generic_interrupt`, `cpu_operations`; functions/prototypes/exports: `acpi_set_mailbox_entry`, `acpi_parking_protocol_valid`, `acpi_parking_protocol_cpu_init`, `acpi_parking_protocol_cpu_prepare`, `acpi_parking_protocol_cpu_boot`, `acpi_parking_protocol_cpu_postboot`. The file is 132 lines / 3595 bytes. Direct includes are `linux/acpi.h`, `linux/mm.h`, `linux/types.h`, `asm/cpu_ops.h`.

### Control Flow
Firmware-provided mailbox entries are recorded by `acpi_set_mailbox_entry`; CPU init validates them, prepare maps the mailbox, boot writes the kernel entry point and signals the parked CPU, and postboot clears temporary mappings.

### State, Persistence, And Dependencies
Notable global/static state symbols are `__iomem`, `cpu_mailbox_entries`, `acpi_parking_protocol_valid`, `acpi_parking_protocol_cpu_init`, `acpi_parking_protocol_cpu_prepare`, `acpi_parking_protocol_cpu_boot`, `cpu_id`, `cpu`, `entry_point`, `acpi_parking_protocol_ops`. Per-CPU mailbox metadata persists during boot. The mailbox memory is firmware-visible shared state used to release secondary CPUs. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong mailbox addresses, missing cache maintenance, or stale temporary mappings can prevent secondary CPU boot or corrupt firmware-owned memory.

### Test Signals
Build `CONFIG_ARM64_ACPI_PARKING_PROTOCOL`, boot firmware using parking protocol, test CPU online/offline, and inspect mailbox write ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_parking_protocol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/alternative.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/alternative.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/alternative.c` applies arm64 alternative instruction patches for CPU capabilities, modules, and the vDSO. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `pr_fmt`, `__ALT_PTR`, `ALT_ORIG_PTR`, `ALT_REPL_PTR`, `ALT_CAP`, `ALT_HAS_CB`, `align_down`; types: `alt_region`, `alt_instr`, `elf64_hdr`, `elf64_shdr`; functions/prototypes/exports: `alternative_is_applied`, `branch_insn_requires_update`, `get_alt_insn`, `patch_alternative`, `clean_dcache_range_nopatch`, `__apply_alternatives`, `apply_alternatives_vdso`, `__apply_alternatives_multi_stop`, `apply_alternatives_all`, `apply_boot_alternatives`, `apply_alternatives_module`, `alt_cb_patch_nops`. The file is 305 lines / 7850 bytes. Direct includes are `linux/init.h`, `linux/cpu.h`, `linux/elf.h`, `asm/cacheflush.h`, `asm/alternative.h`, `asm/cpufeature.h`, `asm/insn.h`, `asm/module.h`, `asm/sections.h`, `asm/vdso.h`, `linux/stop_machine.h`.

### Control Flow
Boot and module paths iterate `struct alt_instr` regions, check capability bits, rewrite branch-relative instructions when needed, patch replacement instructions or callback-generated sequences, flush caches, and use `stop_machine` for system-wide safe application.

### State, Persistence, And Dependencies
Notable global/static state symbols are `all_alternatives_applied`, `alternative_is_applied`, `insn`, `i`, `cur`, `__apply_alternatives`, `is_module`, `nr_inst`, `cap`, `region`, `kernel_alternatives`, `__init`, `apply_alternatives_module`. `applied_alternatives` and `all_alternatives_applied` record patch state. Patched kernel text, module text, and vDSO images persist for the lifetime of the boot/module. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Length mismatches, branch offset errors, missing cache maintenance, or patching without CPU synchronization can corrupt executable text.

### Test Signals
Boot on CPUs with differing capabilities, run module load/unload tests, verify vDSO alternatives, disassemble patched sites, and enable text-patching/debug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/alternative.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/armv8_deprecated.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/armv8_deprecated.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/armv8_deprecated.c` emulates or controls deprecated AArch32 instructions on arm64, including SWP/SWPB, CP15 barrier operations, and SETEND, with sysctl-configurable modes. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `CREATE_TRACE_POINTS`, `ARM_OPCODE_CONDTEST_FAIL`, `ARM_OPCODE_CONDTEST_PASS`, `ARM_OPCODE_CONDTEST_UNCOND`, `ARM_OPCODE_CONDITION_UNCOND`, `__SWP_LL_SC_LOOPS`, `__user_swpX_asm`, `__user_swp_asm`, `__user_swpb_asm`, `TYPE_SWPB`; types: `insn_emulation_mode`, `legacy_insn_status`, `insn_emulation`, `ctl_table`, `pt_regs`; functions/prototypes/exports: `aarch32_check_condition`, `emulate_swpX`, `swp_handler`, `try_emulate_swp`, `cp15barrier_handler`, `cp15_barrier_set_hw_mode`, `try_emulate_cp15_barrier`, `setend_set_hw_mode`, `compat_setend_handler`, `a32_setend_handler`, `t16_setend_handler`, `try_emulate_setend`, `enable_insn_hw_mode`, `disable_insn_hw_mode`, `run_all_cpu_set_hw_mode`, `run_all_insn_set_hw_mode`, `update_insn_emulation_mode`, `emulation_proc_handler`, `register_insn_emulation`, `try_emulate_armv8_deprecated`, `armv8_deprecated_init`. The file is 642 lines / 15818 bytes. Direct includes are `linux/cpu.h`, `linux/init.h`, `linux/list.h`, `linux/perf_event.h`, `linux/sched.h`, `linux/slab.h`, `linux/sysctl.h`, `linux/uaccess.h`, `asm/cpufeature.h`, `asm/insn.h`, `asm/sysreg.h`, `asm/system_misc.h`, `asm/traps.h`, `trace-events-emulation.h`.

### Control Flow
Undefined-instruction handlers decode instruction condition fields, emulate memory operations or endian changes when configured, optionally enable hardware handling on all CPUs, and expose per-instruction mode controls through proc/sysctl.

### State, Persistence, And Dependencies
Notable global/static state symbols are `insn`, `current_mode`, `min`, `max`, `sysctl`, `__maybe_unused`, `cc_bits`, `emulate_swpX`, `type`, `res`, `swp_handler`, `destreg`, `rn`, `try_emulate_swp`, `insn_swp`, `cp15barrier_handler`, `cp15_barrier_set_hw_mode`, `try_emulate_cp15_barrier`, and 17 more. Each `insn_emulation` records current mode, status, min mode, and counters; hardware mode changes are applied per CPU under a mutex. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Instruction decode bugs, user access faults during SWP emulation, inconsistent per-CPU hardware mode, or unsafe sysctl changes can break compat applications.

### Test Signals
Run AArch32 compatibility tests using SWP, CP15 barriers, and SETEND; exercise sysctl mode changes, perf emulation events, and faulting user addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/armv8_deprecated.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/asm-offsets.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/asm-offsets.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/asm-offsets.c` generates arm64 assembly offsets for task, thread, CPU context, pt_regs, suspend, KVM, SDEI, SMCCC, and feature structures. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `COMPILE_OFFSETS`; types: `task_struct`, `pt_regs`, `__arch_ftrace_regs`, `secondary_data`, `arm64_ftr_override`, `kvm_vcpu`, `kvm_cpu_context`, `kvm_host_data`, `kvm_nvhe_init_params`, `cpu_suspend_ctx`, `mpidr_hash`, `sleep_stack_data`, `arm_smccc_res`, `arm_smccc_quirk`, `arm_smccc_1_2_regs`, `pbe`, `arm64_ftr_reg`, `sdei_registered_event`, `ptrauth_keys_user`, `ptrauth_keys_kernel`, `kimage`, `ftrace_ops`; functions/prototypes/exports: `main`. The file is 189 lines / 9238 bytes. Direct includes are `linux/arm_sdei.h`, `linux/sched.h`, `linux/ftrace.h`, `linux/kexec.h`, `linux/mm.h`, `linux/kvm_host.h`, `linux/suspend.h`, `asm/cpufeature.h`, `asm/fixmap.h`, `asm/thread_info.h`, `asm/memory.h`, `asm/smp_plat.h`, `asm/suspend.h`, `linux/kbuild.h`, `linux/arm-smccc.h`.

### Control Flow
The build compiles `main` for its `DEFINE`/`OFFSET` emissions; generated constants are included by assembly files rather than executed at runtime.

### State, Persistence, And Dependencies
Notable global/static state symbols are `main`. No runtime state. The generated header persists in the build output and must match C structure layouts exactly. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Missing or stale offsets cause assembly entry, context switch, suspend, or KVM code to read the wrong fields.

### Test Signals
Run full arm64 builds after structure changes and inspect generated `asm-offsets.h`; boot-test entry, context switch, suspend, and KVM paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cacheinfo.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/cacheinfo.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/cacheinfo.c` detects arm64 cache hierarchy levels and populates generic cacheinfo leaves. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `MAX_CACHE_LEVEL`; types: `cache_type`, `cpu_cacheinfo`, `cacheinfo`; functions/prototypes/exports: `cache_line_size`, `get_cache_type`, `ci_leaf_init`, `detect_cache_level`, `early_cache_level`, `init_cache_level`, `populate_cache_leaves`. The file is 119 lines / 2725 bytes. Direct includes are `linux/acpi.h`, `linux/cacheinfo.h`, `linux/of.h`.

### Control Flow
The code reads cache type/level registers, determines instruction/data/unified leaves, and initializes per-CPU cacheinfo from firmware or architectural registers.

### State, Persistence, And Dependencies
Notable global/static state symbols are `cache_line_size`, `clidr`, `ctype`, `early_cache_level`, `init_cache_level`, `level`, `fw_level`, `populate_cache_leaves`. Detected cache metadata persists in per-CPU cacheinfo structures exposed to sysfs and scheduling/topology code. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong CLIDR interpretation or firmware override handling can expose incorrect cache topology and affect scheduling or diagnostics.

### Test Signals
Boot on varied cache hierarchies, inspect `/sys/devices/system/cpu/cpu*/cache`, and compare with ACPI/PPTT or device-tree data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cacheinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/compat_alignment.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/compat_alignment.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/compat_alignment.c` handles unaligned memory-access fixups for 32-bit compat tasks on arm64 when compatibility alignment fixups are enabled. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `CODING_BITS`, `LDST_P_BIT`, `LDST_U_BIT`, `LDST_W_BIT`, `LDST_L_BIT`, `LDST_P_EQ_U`, `LDSTHD_I_BIT`, `RN_BITS`, `RD_BITS`, `RM_BITS`, `REGMASK_BITS`, `BAD_INSTR`, `IS_T32`, `TYPE_ERROR`, `TYPE_FAULT`, `TYPE_LDST`, `TYPE_DONE`; types: `offset_union`, `pt_regs`; functions/prototypes/exports: `do_alignment_finish_ldst`, `do_alignment_ldrdstrd`, `do_alignment_ldmstm`, `thumb2arm`, `do_alignment_t32_to_handler`, `alignment_get_arm`, `alignment_get_thumb`, `do_compat_alignment_fixup`. The file is 385 lines / 10056 bytes. Direct includes are `linux/compiler.h`, `linux/errno.h`, `linux/kernel.h`, `linux/init.h`, `linux/perf_event.h`, `linux/uaccess.h`, `asm/exception.h`, `asm/ptrace.h`, `asm/traps.h`.

### Control Flow
Fault handling fetches ARM or Thumb instructions from userspace, decodes load/store forms, translates supported Thumb encodings, performs aligned user accesses, updates registers/writeback, and advances the faulting PC.

### State, Persistence, And Dependencies
Notable global/static state symbols are `do_alignment_ldrdstrd`, `rd`, `rd2`, `load`, `val`, `do_alignment_ldmstm`, `L`, `Rn`, `W`, `subset`, `instr`, `alignment_get_arm`, `fault`, `alignment_get_thumb`, `do_compat_alignment_fixup`, `type`, `isize`, `thumb2_32b`. State changes are limited to the compat task's pt_regs and target user memory for emulated stores. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Decoder gaps, wrong writeback, user access faults, or endian/register-list mistakes can corrupt compat process state or loop on faults.

### Test Signals
Run AArch32 unaligned access tests for ARM and Thumb, multi-register transfers, fault injection, signal interaction, and perf alignment-event checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/compat_alignment.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu-reset.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu-reset.S

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu-reset.S` implements the low-level arm64 `cpu_soft_restart` assembly path used by kexec and restart flows. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
functions/prototypes/exports: `SYM_FUNC_END`, `cpu_soft_restart`. The file is 53 lines / 1391 bytes. Direct includes are `linux/linkage.h`, `linux/cfi_types.h`, `asm/assembler.h`, `asm/sysreg.h`, `asm/virt.h`.

### Control Flow
The function disables MMU-sensitive state, switches to the supplied reset context and entry address, and branches with arguments arranged in registers according to the arm64 calling convention and HVC restart expectations.

### State, Persistence, And Dependencies
It mutates CPU system-register/MMU state and transfers control; no normal kernel state is expected to persist on return. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong register preservation, cache/MMU sequencing, or exception-level handling can hang restart/kexec or jump to an invalid physical address.

### Test Signals
Run kexec/kdump reboot tests, inspect objdump output, and test restart from EL1/EL2-capable boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu-reset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_errata.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_errata.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_errata.c` describes arm64 CPU errata detection and mitigation capabilities across vendor MIDR ranges, feature traps, speculative execution workarounds, PMU/TRBE/TLBI issues, SME workarounds, and implementation-defined target overrides. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `CAP_MIDR_RANGE`, `CAP_MIDR_ALL_VERSIONS`, `MIDR_FIXED`, `ERRATA_MIDR_RANGE`, `CAP_MIDR_RANGE_LIST`, `ERRATA_MIDR_REV_RANGE`, `ERRATA_MIDR_REV`, `ERRATA_MIDR_ALL_VERSIONS`, `ERRATA_MIDR_RANGE_LIST`; types: `target_impl_cpu`, `midr_range`, `arm64_cpu_capabilities`, `arm64_midr_revidr`; functions/prototypes/exports: `cpu_errata_set_target_impl`, `is_midr_in_range`, `is_midr_in_range_list`, `__is_affected_midr_range`, `is_affected_midr_range`, `is_affected_midr_range_list`, `is_kryo_midr`, `has_mismatched_cache_type`, `early_arm_si_l1_workaround_4311569_cfg`, `need_arm_si_l1_workaround_4311569`, `cpu_enable_trap_ctr_access`, `has_cortex_a76_erratum_1463225`, `cpu_enable_cache_maint_trap`, `needs_tx2_tvm_workaround`, `has_neoverse_n1_erratum_1542419`, `has_impdef_pmuv3`, `cpu_enable_impdef_pmuv3_traps`, `has_sme_dvmsync_erratum`, `cpu_enable_sme_dvmsync`. The file is 973 lines / 27462 bytes. Direct includes are `linux/arm-smccc.h`, `linux/types.h`, `linux/cpu.h`, `asm/cpu.h`, `asm/cputype.h`, `asm/cpufeature.h`, `asm/fpsimd.h`, `asm/kvm_asm.h`, `asm/smp_plat.h`.

### Control Flow
Capability matching compares current CPU MIDR values against ranges/lists, optional SMCCC/firmware state, and config gates; enable callbacks install traps, static keys, or system-register settings when a workaround applies.

### State, Persistence, And Dependencies
Notable global/static state symbols are `target_impl_cpu_num`, `cpu_errata_set_target_impl`, `i`, `is_midr_in_range_list`, `__maybe_unused`, `midr`, `scope`, `model`, `has_mismatched_cache_type`, `mask`, `sys`, `ctr_raw`, `__init`, `need_arm_si_l1_workaround_4311569`, `enable_uct_trap`, `has_cortex_a76_erratum_1463225`, `has_dic`, `range`, and 25 more. Target-implementation override pointers, static keys, and final CPU capability bits persist after boot and CPU hotplug. Some mitigations change per-CPU system registers. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Incorrect MIDR ranges or missing enable callbacks can leave affected CPUs vulnerable or impose unnecessary traps/performance costs on unaffected systems.

### Test Signals
Build with errata configs, boot affected and unaffected CPU models, inspect mitigation logs/capability bits, run KVM/perf/TRBE/TLBI/SME tests, and validate CPU hotplug reapplication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_errata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_ops.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_ops.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_ops.c` selects per-CPU boot operations for arm64 CPUs from device tree or ACPI enable-method data. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
types: `device_node`, `cpu_operations`; functions/prototypes/exports: `cpu_get_ops`, `cpu_read_enable_method`, `init_cpu_ops`. The file is 118 lines / 2641 bytes. Direct includes are `linux/acpi.h`, `linux/cache.h`, `linux/errno.h`, `linux/of.h`, `linux/string.h`, `asm/acpi.h`, `asm/cpu_ops.h`, `asm/smp_plat.h`.

### Control Flow
`init_cpu_ops` reads the CPU enable method, looks up a matching `cpu_operations` table, validates it, and stores it for later secondary CPU bring-up; `get_cpu_ops` returns the selected table.

### State, Persistence, And Dependencies
Notable global/static state symbols are `__init`. The `cpu_ops` array is initialized once and then kept read-only after init, defining how each CPU is started. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Missing or mismatched enable-method strings can prevent secondary CPUs from booting, especially across DT, PSCI, spin-table, or ACPI parking protocol systems.

### Test Signals
Boot DT and ACPI systems with PSCI/spin-table/parking methods, test CPU hotplug, and validate error logs for unsupported enable methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_ops.c -->
