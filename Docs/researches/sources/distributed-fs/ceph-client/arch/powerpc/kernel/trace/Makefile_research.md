# sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/Makefile

## Purpose
Selects and builds PowerPC tracing objects, particularly ftrace C/assembly variants and the trace clock.

## Important APIs, Types, and Functions
- Builds `ftrace.o`/`ftrace_entry.o` for PPC32 and for PPC64 when mprofile/patchable entry is used.
- Builds `ftrace_64_pg.o`/`ftrace_64_pg_entry.o` for older PPC64 profiling ABI cases.
- Builds `trace_clock.o` under `CONFIG_TRACING`.
- Removes ftrace instrumentation from ftrace implementation files and disables GCOV/KCOV/KCSAN/UBSAN on sensitive text-patching files.

## Control Flow and State
Pure build logic based on `CONFIG_FUNCTION_TRACER`, `CONFIG_MPROFILE_KERNEL`, `CONFIG_ARCH_USING_PATCHABLE_FUNCTION_ENTRY`, `CONFIG_PPC64`, and `CONFIG_PPC32`.

## State and Persistence Behavior
No runtime state. It controls which object files enter the kernel and which instrumentation is suppressed.

## Dependencies and Integration Points
Integrates with Kbuild, tracing/ftrace config options, sanitizer/gcov/kcov build flags, and architecture-specific ftrace variants.

## Risks
Selecting the wrong ftrace implementation for an ABI/compiler mode breaks dynamic ftrace patching. Instrumenting ftrace text-patching code can recurse or perturb sensitive code.

## Test Signals
Build matrix across PPC32/PPC64, mprofile, patchable function entry, function graph tracer, dynamic ftrace with regs/direct/call-ops, and sanitizer/kcov/gcov configs.
