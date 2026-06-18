<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/unaligned_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/unaligned_64.c

## Purpose
Implements SPARC64 unaligned access handling and selected instruction emulation, including kernel integer unaligned loads/stores, POPC emulation, no-fault loads, and user floating-point quad/double unaligned handling.

## Important APIs, Types, And Functions
Key routines include `decode_direction`, `decode_access_size`, `decode_asi`, `fetch_reg`, `fetch_reg_addr`, exported `compute_effective_address`, `kernel_unaligned_trap`, `handle_popc`, `handle_ldf_stq`, `handle_ld_nf`, `handle_lddfmna`, and `handle_stdfmna`. It calls assembly helpers `do_int_load` and `__do_int_store`, and trap handlers in `traps_64.c`.

## Control Flow
Kernel MNA traps store current unaligned context in `thread_info`, decode ASI and direction, immediately route `ASI_AIUS` uaccess faults to exception-table fixup, reject unsupported kernel FP/atomic traps, and otherwise emulate integer access. Successful emulation advances TPC/TNPC; faults search exception tables and may set the ASI in `tstate` for the fixup path. Illegal-instruction and no-fault paths use `handle_popc`, `handle_ldf_stq`, and `handle_ld_nf` to emulate missing or special SPARC64 instructions. User FP MNA handlers load/store FPU state with ASI validation and endian conversion, or delegate to data-access exception handlers.

## State And Persistence
State changes include `pt_regs` PC updates, destination integer registers or user stack register windows, FPU saved state, `thread_info` `kern_una_regs`/`kern_una_insn`, `xfsr`, `fpsaved`, and `gsr`. No durable storage is created beyond perf events and ratelimited logs.

## Dependencies And Integration Points
Used by `traps_64.c` unaligned, illegal-instruction, and no-fault handlers. It depends on FPU state helpers, register-window flushing, alternate ASI definitions, exception tables, perf counters, ratelimit logging, Sun4v versus Spitfire data-access handling, and `una_asm_64.S`.

## Risks And Edge Cases
ASI and endian handling are subtle; the code strips little-endian ASI bits for byte emulation and then swaps values in C. Register-window flushing differs for kernel and user contexts. No-fault loads must return zero without signaling. Floating-point quad register alignment and FPRS flags must be exact or user FP state is corrupted.

## Test Signals
Signals include unaligned integer kernel access, faulting `get_user`/`put_user` exception-table paths, user `SIGBUS` for normal MNA, POPC emulation, LDQ/STQ and no-fault load emulation, FP unaligned load/store behavior, perf alignment/emulation counters, and 32-bit compat register-window cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/unaligned_64.c -->
