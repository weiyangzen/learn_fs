# sources/distributed-fs/ceph-client/tools/perf/util/event.h

Purpose: Declares perf record utility APIs, sample constants, synthesized event formats, branch flag masks, stat round constants, guest helpers, and formatting/processing prototypes.

Important APIs and types: Defines `PERF_SAMPLE_MASK`, `PERF_SAMPLE_MAX_SIZE`, `struct ip_callchain`, branch flag bits and masks, `PERF_TYPE_SYNTH`, `enum perf_synth_id`, Intel PT synthesized raw payload structs, PowerPC VPA DTL struct, raw-data helpers, event processing/printing prototypes, kallsyms lookup prototypes, paranoid/sysctl helpers, page-size naming, and guest cpumode inline helpers.

Control flow and state: Header-only inline logic includes raw-data offset helpers and guest cpumode checks. The synthesized raw structs intentionally include 4 bytes of padding so raw data lines up with `PERF_SAMPLE_RAW` expectations.

Dependencies and integration: Includes kernel/perf event ABI headers, libperf event definitions, Linux types, and forward declarations for perf core structs. Used by event processing, auxtrace, Intel PT, PowerPC DTL, stat, report, and record code.

Risks: Struct packing and padding are ABI-sensitive; changing synthesized event layouts can break decoding. Format macros differ by LP64 to satisfy printf type checking. Branch flag character order must remain aligned with bit definitions.

Test signals: Compile-time size/layout checks for synth structs, raw-size helper tests, sample-size guard tests, guest cpumode helper tests, and decoder tests for Intel PT/PowerPC synthesized records.
