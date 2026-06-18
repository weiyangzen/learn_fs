# sources/distributed-fs/ceph-client/tools/perf/arch/s390/util/machine.c

Purpose: Architecture perf machine customization for callchain or module text handling.

Important APIs/types/functions: `arch__fix_module_text_start`.

Control flow: Adjusts record options or module text start/size based on architecture-specific kernel mapping rules.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf machine/module APIs and architecture proc/sysfs module layout.

Risks: Wrong text start correction mis-symbolizes samples.

Test signals: Perf report on kernel modules and leaf-frame callchains for the target architecture.

Source coverage: researched from the complete local file (38 lines, 1104 bytes).
