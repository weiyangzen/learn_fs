<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power9-events-list.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/power9-events-list.h

Purpose: centralizes POWER9 event mnemonic-to-raw-code definitions consumed by `power9-pmu.c` through the caller-defined `EVENT()` macro.

Important APIs/types/functions: this header has no standalone declarations; its API is the `EVENT(name, code)` expansion contract. It defines generic aliases such as `PM_CYC`, `PM_INST_CMPL`, cache/TLB/branch events, alternate codes such as `PM_RUN_CYC_ALT`, POWER9 DD2.1/DD2.2 blacklisted event identifiers, and synthetic memory profiling encodings `MEM_LOADS` and `MEM_STORES`.

Control flow: inclusion inside an enum in `power9-pmu.c` turns every `EVENT()` row into an enum constant. The same constants are then used in sysfs attributes, generic/cache mapping arrays, alternate-event lookup tables, blacklist arrays, and raw memory-profiling event aliases.

State and persistence: no runtime state. The file persists a compile-time event catalog and therefore affects the ABI values shown under perf PMU sysfs events.

Dependencies and integration: depends on its includer defining `EVENT()`. It is tightly coupled to POWER9 PMU raw encoding, `power9_check_attr_config()`, and perf's exposed event names.

Risks and test signals: a wrong constant produces plausible but incorrect counts; blacklist constants must match DD-level errata; memory event encodings combine base event and MMCRA sampling/threshold bits. Test by building POWER9 perf support, checking `perf list`, verifying blacklist behavior on DD2.1/DD2.2, and comparing memory load/store sampling against architecture documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power9-events-list.h -->
