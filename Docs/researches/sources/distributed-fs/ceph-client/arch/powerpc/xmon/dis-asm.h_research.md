# sources/distributed-fs/ceph-client/arch/powerpc/xmon/dis-asm.h

## Purpose
`dis-asm.h` declares the small disassembler interface used by xmon and provides fallback instruction printing when full xmon disassembly is disabled.

## Important APIs, Types, And Functions
It declares `print_address`. Under `CONFIG_XMON_DISASSEMBLY`, it declares `print_insn_powerpc` and `print_insn_spu`. Otherwise it defines inline fallbacks that print the instruction word as eight hex digits and return zero.

## Control Flow
Callers can use the same print functions regardless of configuration. With disassembly enabled, calls resolve to real decoder implementations; without it, the inline fallback emits raw words.

## State And Persistence
The header carries no state. Output goes through `printf`, which xmon maps to `xmon_printf`.

## Dependencies And Integration Points
It depends on the xmon `printf` environment and on `CONFIG_XMON_DISASSEMBLY`. It is implemented by `ppc-dis.c` and used by xmon command paths that display instructions.

## Risks
The disabled fallback returns zero, while real disassemblers return instruction lengths; callers must tolerate both. The header assumes `printf` is available through xmon's nonstdio layer.

## Test Signals
Builds with `CONFIG_XMON_DISASSEMBLY=y` should link real functions. Builds without it should still allow xmon to display raw instruction words.
