# sources/distributed-fs/ceph-client/tools/perf/arch/arm/tests/vectors-page.c

Purpose: ARM perf test for kernel vectors page symbolization/mapping behavior.

Important APIs/types/functions: `test__vectors_page`, `VECTORS__MAP_NAME`.

Control flow: Exercises perf machine/map logic for ARM exception vector addresses.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on ARM-specific maps and perf test infrastructure.

Risks: Kernel mapping layout changes can make hard-coded expectations stale.

Test signals: Run ARM perf test suite on kernels with and without vectors page mappings.

Source coverage: researched from the complete local file (26 lines, 564 bytes).
