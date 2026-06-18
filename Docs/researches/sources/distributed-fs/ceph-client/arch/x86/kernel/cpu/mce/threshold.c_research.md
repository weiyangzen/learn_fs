# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/threshold.c

Purpose: provides common threshold interrupt handling and CMCI/threshold storm tracking for corrected machine-check events.

Important APIs and flow: `mce_save_apei_thr_limit()` stores a firmware-provided corrected-error threshold limit for AMD threshold setup. `sysvec_threshold()` dispatches the threshold APIC vector through `mce_threshold_vector`, defaulting to a warning until a vendor installs a handler. Per-CPU `storm_desc` tracks bank histories, storm counts, and poll mode. `mce_track_storm()` shifts per-bank history by elapsed seconds, records corrected errors, starts storm mode when recent errors exceed `STORM_BEGIN_THRESHOLD`, and ends it after enough clean polls. `cmci_storm_begin()` enables polling and kicks the MCE timer; `cmci_storm_end()` restores normal polling ownership. `mce_handle_storm()` delegates threshold changes to Intel or AMD vendor code.

State and persistence: state is the APEI threshold limit, vector function pointer, and per-CPU storm descriptors. It is runtime-only and rebuilt after boot/hotplug.

Dependencies and integration: used by Intel CMCI, AMD thresholding, common polling timers, APIC vector entry code, and APEI HEST threshold reporting.

Risks and test signals: storm transitions can suppress or duplicate corrected error reporting if thresholds are wrong. Signals include corrected-error flood injection, storm begin/end logs, timer interval behavior, and vendor threshold restoration after storms.
