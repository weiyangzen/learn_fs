# sources/distributed-fs/ceph-client/arch/x86/kernel/tsc_msr.c

Purpose: provides MSR-based CPU/TSC frequency enumeration for selected Intel Atom-family SoCs where PIT/HPET calibration may be unavailable or unreliable.

Important APIs/functions: exports `cpu_khz_from_msr()`. Key data types are `struct muldiv` and `struct freq_desc`, with per-family descriptors for Penwell, Clovertrail, Bay Trail, Cherry Trail, Merrifield, Moorefield, and Lightning Mountain. Matching is driven by `tsc_msr_cpu_ids[]`.

Control flow: `cpu_khz_from_msr()` matches the boot CPU against supported models, reads either `MSR_PLATFORM_INFO` or `MSR_IA32_PERF_STATUS` for the CPU ratio, reads `MSR_FSB_FREQ` for a frequency selector, computes the reference frequency from a multiplier/divider model or a fixed table, programs `lapic_timer_period` when local APIC support is enabled, and marks the TSC frequency known and reliable.

State and persistence: the function has no private mutable state, but it mutates global CPU feature state with `X86_FEATURE_TSC_KNOWN_FREQ` and `X86_FEATURE_TSC_RELIABLE`, and updates the APIC timer period. These decisions persist for the rest of boot.

Dependencies and integration: called by `native_calibrate_cpu_early()` in `tsc.c`. It depends on x86 CPU model matching, Intel-family model identifiers, MSR accessors, APIC timer globals, and `HZ`.

Risks: wrong model descriptors, bad MSR values, or unknown FSB selectors yield wrong CPU/TSC and APIC timing. The code deliberately trusts hardware-reported MSR data and disables the need for a watchdog by marking TSC reliable, so descriptor accuracy is critical.

Test signals: boot on each supported Atom family should show correct processor MHz and stable APIC timers. Failure signs include `Error MSR_FSB_FREQ index ... is unknown`, clock drift, bad delay loops, or APIC timer miscalibration.
