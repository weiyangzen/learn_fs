# sources/distributed-fs/ceph-client/arch/s390/include/asm/ftrace.lds.h

Purpose: This linker-script helper reserves s390 ftrace hotpatch trampoline text proportional to the number of mcount locations.

Important APIs/types/functions: `SIZEOF_MCOUNT_LOC_ENTRY`, `SIZEOF_FTRACE_HOTPATCH_TRAMPOLINE`, `FTRACE_HOTPATCH_TRAMPOLINES_SIZE(n)`, and `FTRACE_HOTPATCH_TRAMPOLINES_TEXT` are the main definitions; the latter emits start/end symbols only under `CONFIG_FUNCTION_TRACER`.

Control flow: The architecture linker script expands `FTRACE_HOTPATCH_TRAMPOLINES_TEXT`, aligns the location to eight bytes, computes space from `__start_mcount_loc` and `__stop_mcount_loc`, and advances the location counter to reserve trampoline bytes.

State and persistence: State is persistent kernel text layout rather than runtime data. The generated `__ftrace_hotpatch_trampolines_start` and end symbols delimit space consumed by the ftrace hotpatch implementation.

Dependencies and integration points: It integrates with ftrace record emission in `ftrace.h`, module ftrace trampoline accounting, and the final vmlinux linker script.

Risks and test signals: A wrong size formula can under-reserve text and overlap later sections, while over-reserving wastes executable memory. Build/link tests with and without `CONFIG_FUNCTION_TRACER`, plus runtime dynamic ftrace patching, are the primary signals.
