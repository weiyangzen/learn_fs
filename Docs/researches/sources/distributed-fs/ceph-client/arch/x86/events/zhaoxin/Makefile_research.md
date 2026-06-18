## `sources/distributed-fs/ceph-client/arch/x86/events/zhaoxin/Makefile`

Purpose: builds the Zhaoxin x86 PMU backend object.

Important APIs and build rules: `obj-y += core.o` unconditionally includes `core.o` when the parent Kbuild selects this directory.

Control flow: no runtime control flow. Build selection happens in the parent perf-event Makefile and CPU vendor config; this file only contributes the implementation object.

State and persistence: no runtime state.

Dependencies and integration points: the object depends on `core.c`, shared x86 perf symbols, and config paths that include the Zhaoxin events directory.

Risks: because the file is minimal, risks are selection-related: a wrong parent Kbuild condition could omit or include the backend unexpectedly.

Test signals: kernel build with `CONFIG_CPU_SUP_ZHAOXIN` or related vendor support; link succeeds and `zhaoxin_pmu_init()` is available when expected.
