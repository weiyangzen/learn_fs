<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/trace.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/trace.h

Purpose: Defines PowerPC tracepoints for hypervisor, OPAL, RTAS, interrupt, and exception events.

Important APIs/types/functions: `TRACE_EVENT` definitions, hcall/opal tracepoint registration hooks, RTAS event structures, and trace include metadata. Source-visible declarations include: #define TRACE_SYSTEM powerpc; #define _TRACE_POWERPC_H; struct pt_regs;; extern int hcall_tracepoint_regfunc(void);; extern void hcall_tracepoint_unregfunc(void);; extern int opal_tracepoint_regfunc(void);; extern void opal_tracepoint_unregfunc(void);; #define TRACE_INCLUDE_PATH asm.

Control flow: tracepoint users register probes and instrumentation records arguments when firmware or exception paths call tracepoints. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: tracepoint enable state is managed by tracing core; event payloads are transient. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/tracepoint.h>, #include <asm/rtas-types.h>, #include <trace/define_trace.h>. Integrated with ftrace/perf, hypervisor calls, OPAL, RTAS, interrupt, and exception diagnostics.

Risks: tracepoint argument layouts become tooling ABI and must not add heavy work to hot paths. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 347 lines, 7436 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/trace.h -->
