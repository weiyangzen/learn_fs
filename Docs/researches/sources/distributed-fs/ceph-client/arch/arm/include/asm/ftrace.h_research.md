# sources/distributed-fs/ceph-client/arch/arm/include/asm/ftrace.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/ftrace.h` declares ARM ftrace patching
types and graph tracing hooks. It is part of the ARM kernel-architecture compatibility layer
imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ASM_ARM_FTRACE`, `HAVE_FUNCTION_GRAPH_FP_TEST`, `ARCH_SUPPORTS_FTRACE_OPS`, `MCOUNT_ADDR`,
`MCOUNT_INSN_SIZE`, `ftrace_return_address`, `ARCH_HAS_SYSCALL_MATCH_SYM_NAME`; types:
`dyn_arch_ftrace`, `module`; functions/prototypes: `__gnu_mcount_nc`, `return_address`,
`strcasecmp`. The file is 84 lines / 2006 bytes, and the exported surface is primarily an include-
time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `dyn_arch_ftrace`, `module`. External state or implementation
hooks include `__gnu_mcount_nc`. There is no userspace filesystem persistence in this file;
persistence is either kernel memory, CPU register state, hardware register state, or generated ABI
values. It integrates with generic Linux ARM architecture code through include-time contracts rather
than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `ftrace.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
