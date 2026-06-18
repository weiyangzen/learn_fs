# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/amd.c

Purpose: implements AMD/Hygon-style machine-check support: SMCA bank discovery, threshold and deferred-error interrupt setup, vendor errata filtering, memory-error classification, bank clearing, storm handling, and per-CPU threshold sysfs objects.

Important APIs and flow: `mce_amd_feature_init()` applies CPU quirks, enables AMD thresholding, sets SMCA interrupt vectors, configures each bank with `smca_configure()`, disables known-bad thresholding, walks threshold blocks, and initializes their limits/APIC routing. `smca_bsp_init()` installs AMD threshold and deferred interrupt vectors. `amd_filter_mce()`, `amd_mce_is_memory_error()`, and `amd_mce_usable_address()` feed the common MCE pipeline. `amd_clear_bank()` resets threshold limits and clears MCA_STATUS or SMCA DESTAT as appropriate. `sysvec_deferred_error` handles deferred-error APIC delivery by polling deferred banks. `mce_threshold_create_device()` and removal helpers create per-CPU machinecheck sysfs kobjects for bank/block threshold control.

State and persistence: maintains per-CPU AMD bank data, SMCA bank descriptors/counts, threshold-bank object pointers, bank maps, interrupt-bank bitmaps, threshold limit state in MCA_MISC/SMCA MSRs, and global vector function pointers. Sysfs changes immediately reprogram hardware threshold MSRs but are not persistent across reboot.

Dependencies and integration: depends on common MCE core, APIC extended LVT setup, CPU hotplug-created MCE devices, APEI threshold defaults, AMD NB/topology definitions, and SMCA MSR layouts.

Risks and test signals: risks include wrong SMCA bank naming, interrupt routing mistakes, stale sysfs objects during hotplug, and incorrect usable-address classification. Signals include AMD SMCA boot logs, threshold interrupt injection, deferred-error injection, sysfs threshold read/write tests, hotplug create/remove tests, and EDAC/RAS decoding of UMC memory errors.
