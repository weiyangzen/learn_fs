# sources/distributed-fs/ceph-client/arch/arm64/kernel/sigreturn32.S

Purpose: this assembly file provides the AArch32 signal-return code blob copied or mapped for compat tasks. It contains ARM and Thumb instruction sequences for `sigreturn` and `rt_sigreturn`.

Important symbols: `__aarch32_sigret_code_start` and `__aarch32_sigret_code_end` bracket the `.rodata` byte sequence. The sequence includes four variants: ARM `sigreturn`, Thumb `sigreturn`, ARM `rt_sigreturn`, and Thumb `rt_sigreturn`.

Control flow: for ARM state, bytes encode `mov r7, #__NR_compat32_sigreturn` or `#__NR_compat32_rt_sigreturn` followed by `svc`. For Thumb state, two 16-bit instructions load r7 and execute SVC with the corresponding syscall number. `signal32.c` selects the right offset based on `SA_SIGINFO` and handler Thumb bit when no user restorer is supplied.

Dependencies and integration: depends on `asm/unistd_compat_32.h` syscall numbers and the compat signal page setup. It intentionally does not support OABI userspace, matching the C-side comments.

Risks: byte ordering and offsets are ABI-visible; changing the order breaks `compat_setup_return()` indexing. The code must remain in read-only data and be copied/mapped exactly for compat userspace.

Test signals: compat signal return from ARM and Thumb handlers, RT and non-RT signals, and disassembly of the sigpage. Failures appear as bad syscall numbers in r7 or SIGILL/SIGSEGV when returning from compat handlers.
