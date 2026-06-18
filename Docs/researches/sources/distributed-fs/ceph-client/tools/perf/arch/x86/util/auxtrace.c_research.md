# sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/auxtrace.c

Purpose: This x86-specific AUX tracing entry point selects the appropriate Intel AUX trace recorder for `perf record`. It recognizes Intel PT and Intel BTS PMU selections and returns an initialized `struct auxtrace_record` for the active tracing mode.

Important APIs, types, and functions: `auxtrace_record__init()` is the exported arch hook. It obtains the minimum CPU from the evlist's CPU map, calls `get_cpuid()`, and dispatches only for CPUID strings beginning with `GenuineIntel,`. `auxtrace_record__init_intel()` finds `intel_pt` and `intel_bts` PMUs, scans evsels for matching PMU types, rejects simultaneous PT and BTS use, and calls `intel_pt_recording_init()` or `intel_bts_recording_init()`.

Control flow: Initialization starts with `*err = 0`. CPUID failure propagates through `*err` and returns NULL. Non-Intel CPUs return NULL with no error. Intel systems scan the evlist, set `found_pt` and `found_bts`, reject the invalid combination with `-EINVAL`, then return the chosen recorder or NULL if no supported AUX PMU was selected.

State and persistence: The function does not persist state. It returns an allocated recorder object from the Intel PT/BTS subsystem when tracing is active. Error state is reported through the caller-provided `int *err`.

Dependencies and integration points: It integrates with generic `util/auxtrace.h`, `builtin-record.c` via `auxtrace_record__init()`, PMU discovery through `perf_pmus__find()`, CPUID formatting from `header.c`, and Intel PT/BTS recorder implementations. It depends on evsel `core.attr.type` matching PMU type numbers.

Risks: Vendor detection is a string prefix check and therefore depends on x86 `get_cpuid()` formatting. Mixed Intel PT and BTS selection is explicitly unsupported. If evlist CPU maps are empty or CPUID on the minimum CPU fails, AUX trace initialization is skipped with an error. Non-Intel future AUX providers require new dispatch logic.

Test signals: Parsing and recording commands using `intel_pt//` or `intel_bts//` should initialize AUX tracing on Intel systems. Combining both should emit "intel_pt and intel_bts may not be used together" and fail with `EINVAL`.
