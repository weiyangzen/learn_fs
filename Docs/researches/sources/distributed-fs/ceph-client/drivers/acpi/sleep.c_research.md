# sources/distributed-fs/ceph-client/drivers/acpi/sleep.c

## Purpose

`sleep.c` implements ACPI system sleep, hibernation, s2idle, and power-off integration. It maps Linux PM states to ACPI S-states, prepares firmware through ACPI methods and wake vectors, manages ACPI wake devices and GPEs, handles NVS save/restore quirks, and registers platform suspend/hibernation/sys-off operations.

## Important APIs, types, and functions

Important globals include `acpi_no_s5`, `sleep_states[]`, `acpi_target_sleep_state`, `pwr_btn_event_pending`, NVS and old-ordering quirk booleans, `s2idle_wakeup`, saved BM_RLD state, and hibernation FACS signature storage. Exported or externally used functions include `acpi_sleep_state_supported()`, `acpi_target_system_state()`, `acpi_nvs_nosave()`, `acpi_nvs_nosave_s3()`, `acpi_old_suspend_ordering()`, `acpi_sleep_no_blacklist()`, s2idle callbacks, `acpi_s2idle_wakeup()`, and `acpi_sleep_init()`. Platform PM callback tables define suspend, old suspend, s2idle, hibernation, and old hibernation behavior.

## Control flow

`acpi_sleep_init()` applies DMI quirks, marks S0, initializes syscore BM_RLD preservation, registers suspend and hibernation ops if ACPI supports those S-states, registers S5 sys-off handlers, prints supported states, and registers a reboot notifier for `_TTS`. Suspend begins by allocating NVS storage if required, checking sleep-state support, setting firmware suspend mode, calling `_TTS`, and taking `acpi_scan_lock`. Preparation sets the S3 wake vector when needed, enables wake devices, calls `acpi_enter_sleep_state_prep()`, disables GPEs, blocks EC transactions, and saves NVS. Enter executes S1 directly or calls architecture low-level S3 code, restores SCI/GPE programming, handles fixed power-button wake status, unblocks EC transactions, and restores NVS. Finish disables wake devices, calls ACPI leave-sleep, clears waking vector, resumes power resources, and emits a delayed power-button wakeup event. s2idle arms SCI wake, enables wake GPEs, differentiates fixed-event/custom-handler/non-EC/EC wake sources, rearms SCI if needed, then restores runtime GPE and EC state.

## State and persistence

Sleep support is initialized once and records supported ACPI states in `sleep_states[]`. The current target state is global across each PM transition and reset to S0 in finish/end paths. NVS memory snapshots are temporary per suspend/hibernate cycle. DMI and kernel command-line settings persist for the boot. Hibernation records FACS hardware signature for warning or swsusp validation. s2idle tracks whether ACPI wake configuration is armed.

## Dependencies and integration points

The file depends on ACPICA sleep methods/registers, architecture wakeup code (`acpi_suspend_lowlevel`, wakeup address), Linux suspend/hibernation/s2idle/sys-off frameworks, EC transaction blocking, GPE/event management, DMI quirks, reboot notifiers, syscore operations, and ACPI power-resource resume from `sleep.h`/power code.

## Risks

Ordering is critical: `_TTS`, `_PTS`/sleep prep, device suspend, GPE disabling, EC blocking, and NVS save/restore all interact with firmware expectations. Old-ordering and NVS DMI quirks are bug-compatibility paths and can regress specific machines if changed. s2idle wake detection must avoid treating stale SCI/EC activity as a real wake or losing genuine wakeups. Failure paths must release `acpi_scan_lock` and reset target state.

## Test signals

Test S1/S3 suspend-resume, s2idle cycles, S4 hibernation and restore, S5 poweroff, reboot prepare `_TTS`, DMI quirk coverage, NVS save/restore command-line modes, fixed power-button wake event generation, SCI/GPE wake source handling, EC transaction blocking/unblocking, and unsupported S-state reporting.
