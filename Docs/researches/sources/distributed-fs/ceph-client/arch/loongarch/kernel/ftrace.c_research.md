<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/ftrace.c

Purpose: provides LoongArch ftrace call-site support for function tracing.
Important APIs and types: implements architecture ftrace preparation, return address adjustment, and callsite validation hooks used by generic ftrace.
Control flow: ftrace core consults arch hooks when enabling tracing and when interpreting callsites/return addresses.
State and persistence: tracing state is maintained by ftrace core; this file supplies architecture glue.
Dependencies and integration: integrates with `inst.c` instruction generation/patching, module sections, dynamic ftrace, function graph tracing, and unwind metadata.
Risks and test signals: bad callsite interpretation can patch wrong text. Signals include ftrace selftests, function graph tracing, module tracing, and live ftrace enable/disable stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/ftrace.c -->
