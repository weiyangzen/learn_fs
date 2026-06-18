# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/debugfs.c

## Purpose

This file implements debugfs presentation for legacy Intel SoC telemetry. It renders PSS/IOSS event logs, SoC power-state summaries, S0ix residency, and trace verbosity controls under `/sys/kernel/debug/telemetry`.

## Important APIs, Types, And Functions

`struct telemetry_debugfs_conf` holds event IDs, bitfield decode tables, debugfs dentry, and accumulated suspend S0ix stats. Show functions are `telem_pss_states_show()`, `telem_ioss_states_show()`, and `telem_soc_states_show()`. Trace controls use `telem_pss_trc_verb_*` and `telem_ioss_trc_verb_*`. PM notifier helpers `pm_suspend_prep_cb()` and `pm_suspend_exit_cb()` accumulate suspend-only S0ix counters.

## Control Flow

Late init matches Goldmont/Goldmont Plus CPUs, verifies telemetry platform data exists, validates table sizes, registers a suspend notifier, creates the debugfs directory, and adds files. Reads call telemetry core APIs to fetch event logs, decode named bitfields, and format tables. `soc_states` also walks all PCI devices and reports D3 state from PMCSR. Suspend prepare snapshots S0ix counters with raw reads; post-suspend reads them again, corrects stale telemetry counters with PMC GCR if needed, and accumulates suspend stats.

## State And Persistence

Global state includes `debugfs_conf`, suspend temporary counters, and accumulated `suspend_stats`. Data is volatile and reset on module unload. Trace verbosity writes are persistent only in firmware until reset or later write.

## Dependencies And Integration Points

The file depends on telemetry core APIs, debugfs, seq_file, PCI enumeration, suspend notifiers, Intel PMC BXT helpers, and CPU model matching. It assumes `telemetry_get_pltdata()` is already populated.

## Risks

Several local arrays in show functions are not explicitly zeroed before parsing; if a matching event is absent, output can include uninitialized stack values. Debugfs init returns `-ENODEV` if platform telemetry has not initialized, so module load order matters. The debugfs file comments include a typo for `ioss_race_verbosity` but the actual file is `ioss_trace_verbosity`. PCI PMCSR reads assume `dev->pm_cap` is usable.

## Test Signals

Signals include debugfs file creation, event-log rendering with correct names, SoC state decoding, S0ix residency read, trace verbosity read/write, suspend notifier accumulation, behavior when platform data is missing, and KASAN/KMSAN coverage for absent event IDs.
