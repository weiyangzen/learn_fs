# sources/distributed-fs/ceph-client/arch/powerpc/xmon/Makefile

## Purpose
This Makefile builds the PowerPC xmon debugger components while disabling instrumentation that is unsafe or noisy inside low-level debug code.

## Important APIs, Types, And Functions
It disables GCOV, KCOV, UBSAN, KASAN, and KCSAN for the directory, removes ftrace flags when function tracing is enabled, adds a Clang-specific larger frame warning threshold, always builds `xmon.o`, `nonstdio.o`, `spr_access.o`, and `xmon_bpts.o`, and conditionally builds `ppc-dis.o` and `ppc-opc.o` for `CONFIG_XMON_DISASSEMBLY`.

## Control Flow
Kbuild evaluates instrumentation variables and object lists based on configuration, then compiles xmon code with tracing and sanitizers disabled.

## State And Persistence
The Makefile creates normal object files in the build tree and no runtime persistent state.

## Dependencies And Integration Points
It depends on Kbuild, `CONFIG_FUNCTION_TRACER`, `CONFIG_CC_IS_CLANG`, and `CONFIG_XMON_DISASSEMBLY`. It integrates xmon with low-level SPR access, breakpoint support, and optional disassembly tables.

## Risks
Re-enabling tracing or sanitizers in this directory can recurse into debugging paths or break fragile low-level contexts. Optional disassembly objects must remain paired with declarations in `dis-asm.h`.

## Test Signals
Builds with and without `CONFIG_XMON_DISASSEMBLY`, GCC and Clang builds, and entering xmon during boot or crash paths are the main validation signals.
