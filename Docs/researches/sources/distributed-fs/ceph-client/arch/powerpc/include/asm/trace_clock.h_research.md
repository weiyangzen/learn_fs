<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/trace_clock.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/trace_clock.h

Purpose: Registers the PowerPC timebase trace clock.

Important APIs/types/functions: `trace_clock_ppc_tb()` and `ARCH_TRACE_CLOCKS` entry. Source-visible declarations include: #define _ASM_PPC_TRACE_CLOCK_H; extern u64 notrace trace_clock_ppc_tb(void);; #define ARCH_TRACE_CLOCKS { trace_clock_ppc_tb, "ppc-tb", 0 },.

Control flow: tracing can select a raw timebase-backed clock for event timestamps. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: clock state is hardware timebase plus tracing selection. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/compiler.h>, #include <linux/types.h>. Integrated with ftrace/perf timestamping and PowerPC timebase.

Risks: timestamp interpretation depends on stable timebase frequency and notrace recursion safety. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 17 lines, 372 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/trace_clock.h -->
