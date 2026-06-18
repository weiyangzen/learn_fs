# sources/distributed-fs/ceph-client/arch/alpha/kernel/traps.c

## Purpose
Alpha trap initialization and core exception handlers for arithmetic traps, instruction faults, debug traps, kernel/user unaligned accesses, stack/register dumps, and PAL entry registration. The source was read as part of `subset-b-000628` and contains 929 lines.

## Important APIs, Types, and Functions
Provides `dik_show_regs`, `show_stack`, `die_if_kernel`, `do_entArith`, `do_entIF`, `do_entDbg`, `do_entUna`, `do_entUnaUser`, and `trap_init`. Exports or defines FP emulation hooks `alpha_fp_emul_imprecise` and `alpha_fp_emul` when math emulation is modular/absent. Uses `struct allregs`, `struct unaligned_stat`, and the `unaligned[2]` counters.

## Control Flow
Trap init writes the kernel global pointer to PALcode and registers entry points with `wrent`. Arithmetic traps optionally invoke FP emulation before sending `SIGFPE`. Instruction faults handle FEN re-enable, kernel bug/wtint special cases, user breakpoints/gentraps, and SIGILL/SIGTRAP/SIGFPE delivery. Kernel unaligned traps emulate selected loads/stores or forward to exception-table fixups; user unaligned traps honor UAC flags, emulate integer and FP load/store opcodes, and otherwise send SIGSEGV or SIGBUS.

## State and Persistence Behavior
Runtime state includes unaligned access counters/last addresses, current task thread flags/status, FP emulation function pointers, PAL entry vectors, signal delivery state, exception-table fixups, and diagnostic printk output. No filesystem persistence is performed.

## Dependencies
Depends on Alpha PAL entry assembly symbols, `pt_regs`, signal helpers, ptrace breakpoint logic, exception tables, FP register helpers, uaccess, HWRPB/sysinfo, scheduler/task structures, and memory-map locking for user fault classification.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Trap handlers run in fragile contexts; incorrect PC adjustment or register offset mapping can corrupt user state. User unaligned emulation is intentionally slow and must avoid reading past user mappings. Kernel unaligned fixup must preserve exception-table semantics. Signal codes are ABI-visible.

## Test Signals
Run Alpha boot smoke tests, ptrace breakpoint tests, deliberate illegal instruction/gentrap cases, user unaligned access tests with UAC flags, FP load/store unaligned tests, exception-table copy fault tests, and kernel oops stack-dump validation.
