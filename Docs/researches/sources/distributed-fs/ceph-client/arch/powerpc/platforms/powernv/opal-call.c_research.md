
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-call.c

Purpose: central low-level wrapper layer for OPAL firmware calls, including interrupt masking, real-mode handling, and optional tracepoints.

Important APIs/functions: `opal_call()` wraps the assembly `__opal_call()`. The `OPAL_CALL(name, opcode)` macro generates a large set of typed eight-argument firmware call entry points such as console, RTC, PCI/EEH, dump, elog, flash, HMI, NPU, XIVE, sensor, MPIPL, secure variable, and powercap calls. With tracepoints enabled, `opal_tracepoint_regfunc()`, `opal_tracepoint_unregfunc()`, `__trace_opal_entry()`, and `__trace_opal_exit()` manage a static key and recursion guard.

Control flow: `opal_call()` records SRR register clobbering, disables external interrupts in the MSR, calls firmware directly when already running with MMU off, otherwise saves local flags, hard-disables interrupts, optionally emits tracepoint entry/exit around `__opal_call()`, then restores flags. Generated wrappers only bind a function name to an OPAL opcode.

State and persistence: per-CPU `opal_trace_depth` prevents recursive trace emission. A static branch controls tracing overhead. No persistent data is written.

Dependencies and integration points: depends on OPAL ABI opcode definitions, assembly prototypes, interrupt/MSR helpers, tracepoint definitions, and every PowerNV subsystem that invokes OPAL.

Risks: this is a critical firmware ABI boundary. Interrupt and MMU state handling must match OPAL requirements. Tracepoints can themselves cause OPAL calls, so recursion protection is required. A wrong opcode mapping misroutes firmware operations globally.

Test signals: boot-time OPAL calls, ftrace/tracepoint enable-disable, no recursion warnings, OPAL consumers across PCI/RTC/console/dump paths, and real-mode callers that skip virtual-mode interrupt handling.
