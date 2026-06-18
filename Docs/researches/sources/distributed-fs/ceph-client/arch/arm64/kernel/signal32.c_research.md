# sources/distributed-fs/ceph-client/arch/arm64/kernel/signal32.c

Purpose: this file implements AArch32 compatibility signal delivery and `sigreturn`/`rt_sigreturn` for ARM64 kernels running compat tasks. It translates between AArch32 signal frame ABI and ARM64 internal pt_regs/FPSIMD state.

Important APIs and state: structures include `compat_vfp_sigframe` and `compat_aux_sigframe`. Public compat entry points are `COMPAT_SYSCALL_DEFINE0(sigreturn)`, `COMPAT_SYSCALL_DEFINE0(rt_sigreturn)`, `compat_setup_rt_frame()`, `compat_setup_frame()`, and `compat_setup_restart_syscall()`. Helpers convert sigsets, save/restore VFP state, compute compat frame addresses, set return trampolines, and write compat sigcontexts.

Control flow: signal delivery selects old or RT frame shape, places it on an 8-byte-aligned compat stack, writes GPRs, CPSR, fault metadata, sigmask, optional VFP auxiliary state, siginfo/altstack for RT signals, and then updates regs for handler entry. `compat_setup_return()` chooses a user restorer or the kernel-provided compat sigpage stub, handles ARM versus Thumb handler bit, clears IT state, restores endianness, and sets r0/SP/LR/PC/PSTATE. Sigreturn validates SP alignment and access, restores sigmask, GPRs, CPSR via `compat_psr_to_pstate()`, validates user regs, restores VFP if supported, and returns r0.

State and dependencies: uses `thread.uw.fpsimd_state`, current fault address/code, compat VDSO/sigpage, `valid_user_regs()`, altstack helpers, and `__NR_compat32_restart_syscall`. Big-endian builds swap D-register halves out of Q-register storage via `union __fpsimd_vreg`.

Risks: compat signal ABI is fixed and offset-sensitive; the file ends with static assertions for `compat_siginfo_t`. VFP save/restore must handle AArch32 D-register layout despite ARM64 FPSIMD Q-register storage. Restorer selection must encode ARM/Thumb correctly because no OABI userspace is supported.

Test signals: compat signal selftests, Thumb and ARM handlers, old and RT signal frames, VFP state preservation, altstack restore, syscall restart via r7, and static assert build failures if ABI layouts drift.
