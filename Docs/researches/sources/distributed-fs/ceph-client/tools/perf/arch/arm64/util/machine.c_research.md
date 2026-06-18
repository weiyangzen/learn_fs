# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/machine.c

Purpose: Architecture perf machine customization for callchain or module text handling.

Important APIs/types/functions: `arch__add_leaf_frame_record_opts`, `SMPL_REG_MASK`.

Control flow: Adjusts record options or module text start/size based on architecture-specific kernel mapping rules.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf machine/module APIs and architecture proc/sysfs module layout.

Risks: Wrong text start correction mis-symbolizes samples.

Test signals: Perf report on kernel modules and leaf-frame callchains for the target architecture.

Source coverage: researched from the complete local file (13 lines, 322 bytes).
