# sources/distributed-fs/ceph-client/arch/x86/kernel/umip.c

Purpose: emulates a limited set of UMIP-protected user-mode instructions so applications receive safe dummy values instead of kernel address leaks or fatal general-protection faults.

Important APIs/functions: main external entry is `fixup_umip_exception(struct pt_regs *regs)`. Internal helpers are `identify_insn()`, `emulate_umip_insn()`, `force_sig_info_umip_fault()`, and rate-limited `umip_printk()`. Supported instructions are SGDT, SIDT, SMSW, SLDT, and STR.

Control flow: on a user #GP, `fixup_umip_exception()` checks UMIP support, fetches and decodes the faulting user instruction from `regs`, identifies whether it is an emulatable UMIP instruction, builds dummy data, and writes the result either into the saved register image or user memory. Successful emulation advances `regs->ip`; failed memory copy synthesizes a SIGSEGV while reporting the exception as fixed.

State and persistence: there is no durable kernel state except rate-limit state for logging. For SLDT, the code reads the current mm LDT state under `ldt_usr_sem`. It mutates only the faulting task's saved registers or user memory and signal state.

Dependencies and integration: depends on x86 instruction decoding/evaluation helpers, user access helpers, `pt_regs`, signal delivery, GDT/TSS/LDT constants, CR0 boot state, and the #GP handler path that calls this fixup.

Risks: instruction decoding, operand-size, segmentation, and register-offset handling must match user mode exactly. A wrong copy target could corrupt user state, and excessive fidelity could leak protected kernel layout. LDT locking must be correct under concurrent modify_ldt users.

Test signals: user programs executing SGDT/SIDT/SMSW/SLDT/STR under UMIP should continue with documented dummy results. Negative tests include bad user destinations, register operands, 32-bit compatibility mode, LDT-present and LDT-absent cases, and unsupported encodings that should fall through to normal fault handling.
