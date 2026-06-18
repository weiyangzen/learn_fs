## sources/distributed-fs/ceph-client/arch/mips/kernel/unaligned.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/unaligned.c` handles MIPS address error exceptions caused by unaligned data accesses. It can signal the task or emulate many load/store instructions for normal MIPS, microMIPS, and MIPS16e instruction encodings, with optional debugfs counters and policy control.

### Important APIs, Types, And Functions
The main handlers are `emulate_load_store_insn()`, `emulate_load_store_microMIPS()`, `emulate_load_store_MIPS16e()`, and `do_ade()`. Debugfs setup is `debugfs_unaligned()`. State includes `unaligned_instructions`, `unaligned_action`, and register recode tables `reg16to32` and `reg16to32st`. It uses access macros such as `LoadW`, `StoreW`, `LoadDW`, EVA variants, FPU emulator calls, MSA register helpers, and CU2 notifier calls.

### Control Flow
`do_ade()` enters exception context, records an alignment fault perf event, handles special 64-bit bad-address fixups, rejects instruction-fetch alignment faults, honors per-thread `TIF_FIXADE`, and applies debugfs policy. It then selects microMIPS, MIPS16e, or normal MIPS decoding based on ISA16 mode and CPU features. Emulators decode the faulting instruction, validate user access ranges, perform the unaligned load/store in software, update target registers or memory, advance EPC including branch/delay-slot behavior, and count successful emulations. Fault paths roll back EPC/RA, try `fixup_exception()`, or force `SIGSEGV`, `SIGBUS`, or `SIGILL`.

### State, Persistence, And Dependencies
Per-task state includes `TIF_FIXADE`, `TIF_LOGADE`, pt_regs, FPU/MSA state, and user memory. Global state is debugfs policy and counters. Dependencies include `asm/branch.h`, `asm/inst.h`, `asm/unaligned-emul.h`, FPU emulator, MSA, CU2 notifier chain from `traps.c`, `access-helper.h`, perf software events, and debugfs.

### Integration Points
`syscall.c` exposes `sysmips(MIPS_FIXADE)` to control per-task unaligned emulation. `traps.c` installs address error exception vectors and provides `show_registers()`, `process_fpemu_return()`, and CU2 notifier behavior. MM exception tables allow kernel unaligned user-copy faults to be fixed up.

### Risks
Instruction decoding is broad and architecture-specific. Emulating stores that cross page boundaries can partially modify memory, a TODO called out in the file. Branch delay handling must preserve original EPC/RA on faults. Unsupported LL/SC, byte operations, kernel accesses, coprocessor loads, and unsupported 64-bit instructions must signal rather than silently emulate. MSA and FPU paths must not leak register state or clobber live context.

### Test Signals
Test user unaligned halfword/word/doubleword loads and stores, disabled `TIF_FIXADE`, debugfs `unaligned_action` signal/show modes, MIPS16e and microMIPS load/store encodings, branch delay slot cases, page-crossing faults, FPU and MSA unaligned accesses, kernel fixup-table cases, and perf/debugfs counters.
