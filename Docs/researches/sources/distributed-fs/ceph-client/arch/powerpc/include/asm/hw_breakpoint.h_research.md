# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hw_breakpoint.h

Purpose: Defines PowerPC hardware breakpoint/watchpoint architecture state and helper contracts for perf and ptrace watchpoints.

Important APIs, types, and functions: `struct arch_hw_breakpoint` records address, type, requested and hardware length, flags, and perf single-step state. Defines read/write/translate/user/kernel/hypervisor/extraneous type bits, disabled flag, DABR/DAWR length limits, `HW_BREAKPOINT_SIZE`, `nr_wp_slots()`, `wp_check_constraints()`, and `wp_get_instr_detail()`.

Control flow: Breakpoint setup validates address/type/length against DABR/DAWR constraints, programs one or two watchpoint slots depending on CPU features, and exception handling decodes the faulting instruction/effective address for constraint checks.

State and persistence: Per-task/perf breakpoint state is stored outside the header. Hardware DAWR/DABR registers hold volatile watchpoint state.

Dependencies and integration points: Depends on CPU feature detection, instruction decoding, perf hardware breakpoint core, ptrace/debug exception paths, and PowerPC Book3S/8xx differences.

Risks: Slot count changes with `CPU_FTR_DAWR1`. Length granularity differs for DABR/DAWR and 8xx. Mis-decoding instructions can cause false positives or missed watchpoints.

Test signals: Read/write watchpoints, user/kernel privilege filters, DAWR1-capable CPUs, DABR fallback, 8xx granularity, perf single-step reinstall, and extraneous IRQ handling.
