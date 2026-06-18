# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/fpu.h

## Purpose

`fpu.h` manages FPU, LSX and LASX ownership, save/restore and user context helpers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 326 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: kernel_fpu_begin/end, _save/_restore_fp/lsx/lasx, context copy helpers, is_*_enabled, own/lose/init_fpu, save_fpu_regs, thread_lsx/lasx_context_live. Symbol extraction from the file shows representative defines `_ASM_FPU_H`, `kernel_fpu_available`, `enable_fpu`, `disable_fpu`, `clear_fpu_owner`, representative callable declarations or inline helpers `kernel_fpu_begin`, `kernel_fpu_end`, `_init_fpu`, `_save_fp`, `_restore_fp`, `_save_fp_context`, `_restore_fp_context`, `_save_lsx`, `_restore_lsx`, `_init_lsx_upper`, `_restore_lsx_upper`, `_save_lsx_context`, and representative local types `sigcontext`. Direct includes seen in the header are `asm/cpu-features.h`, `asm/cpu.h`, `asm/current.h`, `asm/loongarch.h`, `asm/processor.h`, `asm/ptrace.h`, `linux/bitops.h`, `linux/ptrace.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header ties CPU feature detection, CSR_EUEN bits, thread flags, signal frames, context switch and kernel FPU users together. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: preemption windows, lazy ownership flags and upper SIMD state are high-risk; tests need signal, ptrace, context-switch and SIMD workloads. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
