# sources/distributed-fs/ceph-client/arch/sh/kernel/traps_32.c

Purpose: handles 32-bit SuperH trap dispatch after low-level entry code has saved register state, with emphasis on unaligned access emulation, reserved/illegal-slot instruction handling, SH-DSP enablement, SH2A divide exceptions, and exception-vector setup.

Important APIs and functions: `handle_unaligned_access`, `do_address_error`, `do_reserved_inst`, `do_illegal_slot_inst`, `do_exception_error`, `per_cpu_trap_init`, `set_exception_table_vec`, and `trap_init`. Internal helpers include `handle_unaligned_ins`, `handle_delayslot`, endian-aware `sign_extend`, and kernel/user `mem_access` wrappers.

Control flow: address errors fetch the faulting instruction from user or kernel space, consult unaligned policy, emulate supported SH load/store forms, and advance `regs->pc` or branch target state. Delay-slot branches are specially decoded so fixups preserve SH branch semantics. Reserved-instruction traps first try FPU emulation, then DSP mode activation, then signal or die paths. `trap_init` installs handlers by trap vector/EVT based on CPU/FPU configuration.

State and persistence: mutates `pt_regs` (`pc`, `pr`, general registers, and `sr`), current thread DSP status, and alignment counters in `arch/sh/mm/alignment.c`. No persistent storage exists, but exception-table entries and VBR setup are boot/runtime global state.

Dependencies and integration: depends on uaccess/no-fault copy helpers, `asm/alignment.h`, FPU/DSP support, kprobes illegal-slot hooks, perf software events, exception-vector lookup, and low-level SH entry/vector tables.

Risks: instruction decoding covers selected 16-bit SH instructions only and rejects mixed 16/32-bit instructions. Incorrect branch-delay PC updates can silently resume at the wrong address. Kernel fixup paths can die if the instruction fetch or emulated memory access faults without an exception-table recovery.

Test signals: best tested through architecture boot tests, unaligned user/kernel access cases, FPU-emulation traps, illegal slot/kprobe cases, and perf/alignment counter observation; no local unit test is present.
