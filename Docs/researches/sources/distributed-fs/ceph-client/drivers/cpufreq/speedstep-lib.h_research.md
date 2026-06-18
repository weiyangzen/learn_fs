# sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-lib.h

Purpose: declares the shared SpeedStep processor IDs, binary state constants, and exported helper prototypes consumed by legacy Intel SpeedStep CPUFreq drivers.

Important APIs and types: `enum speedstep_processor` identifies auto-detected PIII/P4-M processors and frequency-decodable non-autodetected Pentium M/P4D/Core values. `SPEEDSTEP_HIGH` is state 0 and `SPEEDSTEP_LOW` is state 1, matching the CPUFreq table indices used by the ICH and SMI drivers. Prototypes expose `speedstep_detect_processor()`, `speedstep_get_frequency()`, and `speedstep_get_freqs()`.

Control flow and state: this header has no runtime state; it fixes the ABI contract between transition-capable drivers and the library. Callers pass a `set_state()` callback to `speedstep_get_freqs()`, which probes both hardware states.

Dependencies and integration points: integrates only with `speedstep-lib.c` and SpeedStep CPUFreq drivers. It assumes consumers include CPUFreq-visible types before or alongside it.

Risks and test signals: risks include the semantic dependency that high/low constants equal table indices, stale enum values for obsolete x86 CPUs, and comments referring to an older callback signature. Test signals are clean compile for both consumers, CPUFreq index 0 mapping to high state, and no enum mismatches in detection switch statements.
