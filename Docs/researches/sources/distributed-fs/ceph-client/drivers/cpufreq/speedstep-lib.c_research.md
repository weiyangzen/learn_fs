# sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-lib.c

Purpose: supplies shared Intel SpeedStep v1/v2 helpers for legacy CPUFreq drivers. It detects supported mobile Pentium III/Pentium 4 processors, decodes current frequencies from MSRs, and probes the two SpeedStep rates by executing a caller-supplied state transition callback.

Important APIs and functions: `speedstep_get_frequency()` dispatches to `pentium3_get_frequency()`, `pentiumM_get_frequency()`, `pentium_core_get_frequency()`, or `pentium4_get_frequency()`. `speedstep_detect_processor()` uses `boot_cpu_data`, CPUID EBX, model IDs, platform MSRs, and optional `relaxed_check` to distinguish mobile SpeedStep-capable processors. `speedstep_get_freqs()` records the current speed, switches to low then high state with interrupts and preemption disabled, measures transition latency with `ktime_get()`, restores the previous state when needed, and exports low/high kHz values.

Control flow and state: the library is mostly stateless, with only the optional `relaxed_check` module parameter. Frequency decoding is table-driven for PIII multipliers/FSB values and switch-driven for Pentium M/Core/P4 FSB encodings. `speedstep_get_freqs()` serializes with local IRQ/preemption control because the transition callback may be chipset or SMI sensitive.

Dependencies and integration points: depends on x86 MSR access, CPUID helpers, `cpu_khz`, CPUFreq definitions, and callers that provide safe `set_state(SPEEDSTEP_LOW/HIGH)` callbacks. It exports GPL symbols used by `speedstep-ich` and `speedstep-smi`.

Risks and test signals: risks include undocumented CPU heuristics, fallback to measured `cpu_khz` for early P4, potentially long interrupts-off windows while probing transitions, inexact latency safety clamping, and the relaxed capability knob admitting unsafe hardware. Test signals include nonzero decoded frequency on every supported enum, correct rejection of desktop Coppermine/Celeron cases, low/high rates differing, latency clamped to sane bounds, and successful symbol linkage for both consumers.
