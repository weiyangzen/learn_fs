# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/pmc-quirks.c

Purpose: `pmc-quirks.c` contains DMI-based workarounds for AMD PMC S2Idle firmware issues, primarily skipping a problematic NVMe SMI handler and disabling spurious IRQ1/i8042 wakeups on affected systems.

Important APIs, types, and functions: `struct quirk_entry` has `s2idle_bug_mmio` and `spurious_8042` fields. Static quirk instances are referenced by `fwbug_list`, a large DMI table. `amd_pmc_quirks_init()` applies default Cezanne IRQ1 behavior, looks up DMI quirks, and sets `dev->quirks` and `dev->disable_8042_wakeup`. `amd_pmc_process_restore_quirks()` calls `amd_pmc_skip_nvme_smi_handler()` when configured.

Control flow: PMC probe calls `amd_pmc_quirks_init()` unless workarounds are disabled. On S2Idle restore, the PMC core calls `amd_pmc_process_restore_quirks()` after SMU restore and STB logging. The MMIO workaround requests one byte at an FCH scratch address, maps it, clears bit 0, unmaps, and releases the region.

State and persistence: quirk state is stored in the runtime `amd_pmc_dev`. The MMIO workaround mutates platform firmware/FCH scratch state for the resume path but does not store driver-owned persistent data.

Dependencies and integration points: depends on DMI matching, FCH platform-data constants, MMIO resource claiming, and PMC core restore/suspend hooks. It coordinates with `amd_pmc_suspend_handler()` via `disable_8042_wakeup`.

Risks: DMI matching must be precise; too broad matches can alter wake behavior or MMIO bits on unaffected systems, while missing matches leave suspend/resume bugs. The MMIO workaround silently returns if the region cannot be requested or mapped. Default Cezanne IRQ1 workaround can be overridden only by DMI quirk data and module-level `disable_workarounds` in PMC core.

Test signals: DMI match logs, `dev->disable_8042_wakeup` set for expected systems, IRQ1 wake disabled during suspend, bit 0 cleared at the configured FCH scratch byte on restore, and no quirk activity when `disable_workarounds=1`.
