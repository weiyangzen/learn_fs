# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/intel.c

Purpose: implements Intel/Zhaoxin MCE vendor features, especially CMCI ownership/discovery, local machine-check enablement, memory-controller logging, vendor quirks, filtering, and usable-address validation.

Important APIs and flow: `mce_intel_feature_init()` applies bank quirks, initializes CMCI, enables LMCE, and enables selected integrated memory controller logs. `cmci_supported()` validates configuration, APIC, vendor, and `MCG_CMCI_P`. `cmci_discover()` scans banks under a raw lock, skips firmware-owned or already-owned banks, chooses thresholds, claims banks by setting `MCI_CTL2_CMCI_EN`, clears polled banks, and handles inherited storm thresholds. `intel_threshold_interrupt()` polls owned banks. CPU hotplug paths call `cmci_clear()`, `cmci_rediscover()`, and `cmci_reenable()` through core callbacks. `intel_init_lmce()` gates LMCE on MCG_CAP and locked `IA32_FEAT_CTL`; `intel_filter_mce()` filters known erratum signatures; `intel_mce_usable_address()` accepts only page-granularity physical-address reports.

State and persistence: per-CPU owned-bank masks, global CMCI threshold defaults, storm state in common threshold code, and hardware MCi_CTL2/MCG_EXT_CTL MSRs. State is reestablished on CPU hotplug/resume.

Dependencies and integration: depends on common MCE polling, APIC CMCI vector, threshold storm handling, feature-control setup, CPU hotplug, and Intel model tables.

Risks and test signals: shared-bank ownership and storm thresholds are race-sensitive. Signals include CMCI interrupt delivery, shared-bank rediscovery after hotplug, `mce=no_cmci`/`ignore_ce`, LMCE enable bits, storm begin/end logs, and injection/filter tests for known errata.
