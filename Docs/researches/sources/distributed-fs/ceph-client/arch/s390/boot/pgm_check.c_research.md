<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/pgm_check.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/pgm_check.c

Purpose: Implements early program-check reporting and fixup handling for the s390 boot decompressor. On unrecoverable faults it prints version, command line, KASLR offsets, PSW state, GPRs, stack trace, and last breaking-event address, then converts the faulting PSW to a disabled-wait PSW.

Important APIs/types/functions: Provides `print_stacktrace()` and `do_pgm_check()`. Internal helpers are `extable_insn()` and `ex_handler()`, using `__start___ex_table`, `__stop___ex_table`, `struct exception_table_entry`, `extable_fixup()`, `struct pt_regs`, `struct stack_frame`, and PSW bit accessors.

Control flow: `do_pgm_check()` first scans the early exception table; matching `EX_TYPE_FIXUP` entries redirect `regs->psw.addr` and return. Otherwise it optionally dumps the boot ring buffer, prints diagnostic context via `boot_emerg()`, walks the current boot stack from GPR15, and disables I/O and external interrupts before setting wait state.

State and persistence: It reads `kernel_version`, `early_command_line`, KASLR offsets, and boot debug flags. It mutates only the supplied `pt_regs` PSW to drive disabled wait after returning to low-level code.

Dependencies and integration points: Integrated with early exception vectors, exception-table annotations in boot code, `printk.c`, stack bounds `_stack_start/_stack_end`, lowcore state, protected-virtualization checks, and `kaslr.c` state.

Risks: Fault reporting itself must avoid additional faults. Symbol lookup and stack walking rely on decompressor symbol tables and valid stack-frame layout. Printing the command line is suppressed for protected-virtualization guests to avoid leaking protected inputs; future additions must preserve that property.

Test signals: Deliberate early exception-table fixups, injected boot program checks, KASLR-enabled and protected-guest crash logs, and stack trace correctness in decompressor symbols.

Source read size: 92 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/pgm_check.c -->
