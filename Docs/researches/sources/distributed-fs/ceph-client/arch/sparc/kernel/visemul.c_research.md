<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/visemul.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/visemul.c

## Purpose
Emulates selected VIS instructions not implemented in hardware on Niagara-class SPARC64 CPUs, allowing user programs to execute supported VIS operations through the illegal-instruction trap path.

## Important APIs, Types, And Functions
The public entry is `vis_emul`. Helpers include `maybe_flush_windows`, `fetch_reg`, `store_reg`, FPU register accessors `fpd_regval`, `fpd_regaddr`, `fps_regval`, `fps_regaddr`, and operation groups `edge`, `array`, `bmask`, `bshuffle`, `pdist`, `pformat`, `pmul`, and `pcmp`. OPF constants define pack, expand, merge, multiply, compare, edge, array, byte-mask, and shuffle instructions.

## Control Flow
`vis_emul` verifies it is not in privileged state, records a perf emulation fault, refetches the instruction from user PC, saves and clears live FPU state, decodes the OPF field, dispatches to the matching emulator, and advances TPC/TNPC. Integer-register VIS operations flush user register windows and read/write `pt_regs` or stack-resident windows. FP-register operations read/write saved `fpustate` and `thread_info` GSR fields.

## State And Persistence
The code mutates user integer registers, user stack register windows, saved FPU register state, `thread_info()->gsr[0]`, and condition-code bits in `regs->tstate` for edge instructions. It has no global persistent state beyond static lookup tables.

## Dependencies And Integration Points
Called from `do_illegal_instruction` in `traps_64.c` for hypervisor systems when the opcode matches VIS. It depends on FPU save helpers, SPARC register-window layout, user memory accessors, perf software events, and 32-bit compat register handling.

## Risks And Edge Cases
The emulation only supports listed OPFs and returns `-EINVAL` for the rest. Register-window stores to user stack can fault but are not deeply recovered here. VIS arithmetic has many saturating, rounding, endian, and packed-lane semantics that must match hardware. Privileged execution is treated as a bug.

## Test Signals
Signals include user VIS instruction suites on hardware lacking the operations, illegal-instruction fallback for unsupported OPFs, compare/pack/multiply/edge arithmetic conformance against hardware, GSR mask behavior for `bmask`/`bshuffle`, and 32-bit process coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/visemul.c -->
