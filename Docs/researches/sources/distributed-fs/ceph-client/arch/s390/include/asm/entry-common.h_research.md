<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/entry-common.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/entry-common.h

Purpose: Customizes generic entry/exit handling for s390.

Important APIs/types/functions: `ARCH_EXIT_TO_USER_MODE_WORK`, `do_per_trap()`, `arch_enter_from_user_mode()`, `arch_exit_to_user_mode_work()`, `arch_exit_to_user_mode()`, and `arch_in_rcu_eqs()`. Source-visible declarations include: #define ARCH_S390_ENTRY_COMMON_H; #define ARCH_EXIT_TO_USER_MODE_WORK (_TIF_GUARDED_STORAGE | _TIF_PER_TRAP); void do_per_trap(struct pt_regs *regs);; static __always_inline void arch_enter_from_user_mode(struct pt_regs *regs); #define arch_enter_from_user_mode arch_enter_from_user_mode; static __always_inline void arch_exit_to_user_mode_work(struct pt_regs *regs,; unsigned long ti_work); #define arch_exit_to_user_mode_work arch_exit_to_user_mode_work; static __always_inline void arch_exit_to_user_mode(void); #define arch_exit_to_user_mode arch_exit_to_user_mode.

Control flow: Entry code marks context tracking transitions, handles guarded-storage/per-event trap work before returning to user mode, and exposes RCU EQS state tests.

State and persistence behavior: State is task thread flags, context tracking/RCU state, and pt_regs for the current transition.

Dependencies and integration points: Direct includes are #include <linux/sched.h>, #include <linux/audit.h>, #include <linux/randomize_kstack.h>, #include <linux/processor.h>, #include <linux/uaccess.h>, #include <asm/timex.h>, #include <asm/fpu.h>, #include <asm/pai.h>. Integrated with Integrates generic entry code, RCU/context tracking, guarded storage, PER tracing, and syscall/interrupt exit paths..

Risks: Ordering with RCU and thread flag clearing is critical; missed PER/GS work leaks traps to the wrong user context.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 64 lines, 1409 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/entry-common.h -->
