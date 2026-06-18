# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/header.c

Purpose: Architecture perf header helper that derives CPU identification or runtime PMU parameters for perf.data metadata and event-map lookup.

Important APIs/types/functions: `_get_cpuid`, `get_cpuid`, `strcmp_cpuid_str`, `MIDR`, `MIDR_SIZE`, `MIDR_REVISION_MASK`, `MIDR_VARIANT_MASK`.

Control flow: Reads sysfs, `/proc/cpuinfo`, auxv, `/proc/sysinfo`, or service-level files; formats CPU IDs; and exposes comparison/runtime parameter helpers where needed.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture kernel proc/sysfs ABI, perf CPU maps, cpuid override helpers, and metric code.

Risks: Parsing fixed field names is brittle across kernel/userland variants; buffer sizes must fit formatted IDs.

Test signals: Unit tests for parser helpers plus perf record/report on representative hardware or fixture files.

Source coverage: researched from the complete local file (126 lines, 2970 bytes).
