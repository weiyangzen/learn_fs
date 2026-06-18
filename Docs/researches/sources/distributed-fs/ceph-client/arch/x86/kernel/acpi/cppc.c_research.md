# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/cppc.c

## Purpose
`cppc.c` provides x86-specific ACPI CPPC FFH support and AMD performance-capability helpers. It decides whether CPPC is supported by the current CPU family, implements FFH reads/writes through model-specific registers, initializes scheduler frequency invariance from CPPC performance data, and exports AMD helpers for preferred-core detection and boost-ratio scaling.

## Important APIs, Types, and Functions
- `cpc_supported_by_cpu()` recognizes AMD/Hygon CPPC support by family/model exceptions and `X86_FEATURE_CPPC`.
- `cpc_ffh_supported()` advertises FFH support for x86.
- `cpc_read_ffh()` and `cpc_write_ffh()` access `struct cpc_reg` bitfields through `rdmsrq_safe_on_cpu()` and `wrmsrq_safe_on_cpu()`.
- `acpi_processor_init_invariance_cppc()` initializes frequency invariance if APERF/MPERF and AMD CPPC data are available.
- `amd_get_highest_perf()` reads either `MSR_AMD_CPPC_CAP1` or generic `cppc_get_highest_perf()`.
- `amd_detect_prefcore()` determines whether online CPUs expose different highest-performance values and caches the result in `amd_pref_core_detected`.
- `amd_get_boost_ratio_numerator()` returns the numerator used for boost-ratio scaling, with special handling for preferred cores, Zen4 model `0x70..0x7f`, and heterogeneous AMD core types.

## Control Flow
The ACPI CPPC core calls the `cpc_*` hooks when evaluating FFH register access. Reads mask and right-shift the requested bitfield from the MSR; writes read-modify-write the same bitfield to preserve neighboring fields. Frequency invariance initialization is guarded by `freq_invariance_lock` and a static `init_done`, then obtains CPPC performance caps, derives a midpoint between maximum boost and nominal performance, and calls `freq_invariance_set_perf_ratio()`.

AMD preferred-core detection is lazy. Callers ask `amd_detect_prefcore()`, which returns a cached supported/unsupported state if available, otherwise scans online CPUs until it sees either one highest-performance value or two distinct values. `amd_get_boost_ratio_numerator()` first forces detection, then chooses either the cached non-preferred-core numerator, a Zen4 constant, a performance-core constant, an efficiency-core actual highest-performance value, or the default preferred-core constant.

## State and Persistence Behavior
`amd_pref_core_detected` and `boost_numerator` persist the preferred-core probe result across callers. `freq_invariance_lock` and the static `init_done` prevent repeated scheduler-scale initialization. MSR writes persist in CPU hardware state according to the CPPC register being accessed; the helpers do not maintain rollback state.

## Dependencies and Integration Points
The file integrates ACPI CPPC (`acpi/cppc_acpi.h`), MSR access, x86 CPU feature flags, scheduler capacity scaling, topology core-type classification, and AMD P-state/CPU frequency consumers through exported GPL symbols. It assumes caller-side interpretation of CPPC performance registers and delegates generic ACPI object access to `drivers/acpi/cppc_acpi.c`.

## Risks
- Model-specific CPPC allow-list logic can misclassify AMD/Hygon systems and disable performance control or preferred-core hints.
- `amd_detect_prefcore()` scans only online CPUs and caches the result; CPU topology changes after first use may not alter the cached outcome.
- FFH bitfield masks rely on firmware-provided `bit_offset` and `bit_width`; invalid values could produce bad masks.
- Hardcoded numerator constants are sensitive to CPU family/model errata and heterogeneous-core policy.

## Test Signals
- Validate CPPC FFH reads/writes with ACPI CPPC tables on AMD/Hygon machines and with invalid MSR paths returning errors.
- Compare `amd_detect_prefcore()` results with known preferred-core systems and uniform-core systems.
- Exercise AMD P-state frequency invariance and scheduler capacity reporting across Zen generations, including Zen4 `0x70..0x7f` and AMD heterogeneous-core systems.
