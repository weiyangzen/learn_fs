# File Research: sources/block-storage/mdadm/mdmonitor.c

## Role

`mdmonitor.c` implements the user-facing mdadm monitor mode. It watches md arrays for state changes, emits alerts through stderr, syslog, mail, or an external program, discovers new arrays in scan mode, supports spare migration across spare groups/domains, and implements `Wait`/`WaitClean`.

## Monitor State

`struct state` records one monitored md device: full `/dev/md/...` name, kernel devnm, parent container devnm, subarray/container links, spare group, active/working/failed/spare/raid counts, per-slot device state and `dev_t`, rebuild percent, expected spares, metadata supertype, and error counters.

`struct alert_info` holds hostname, mail settings, alert command, syslog flag, and test flag.

## Events

Events are mapped by `events_map` and include:

- `SpareActive`, `NewArray`, `MoveSpare`, `TestMessage`
- `RebuildStarted`, progress `RebuildNN`, `RebuildFinished`
- `SparesMissing`, `DeviceDisappeared`, `Fail`, `FailSpare`, `DegradedArray`

Priority markers split events into info, warning, and critical syslog severities.

## Main Monitor Flow

`Monitor()`:

- Rejects incompatible explicit device list plus `--scan`.
- Loads mail/program defaults from config when not supplied.
- Requires at least mail, alert command, or syslog in scan mode.
- Creates `MDMON_DIR`, optionally daemonizes, optionally enforces single autorebuild process, and builds an initial `statelist` from mdadm.conf or explicit devices.
- Loops over `/proc/mdstat`, calls `check_array()` for each known array, auto-adds new arrays in scan mode, attempts spare migration when enabled and arrays are degraded, waits for udev events or mdstat events, and prunes repeatedly failing auto-added arrays.

## Alerting

- `alert()` builds a standardized message, writes it with `pr_err()`, optionally executes the configured alert command, sends email for selected events, and logs to syslog.
- Email includes current `/proc/mdstat` content.
- Alert command is invoked as `alert_cmd event dev disc`.

## Array Checking

`check_array()`:

- Opens the md device, maps it to a devnm, matches it with mdstat, detects containers, validates active arrays, and reads ioctl/sysfs state.
- Detects new arrays, degraded startup, missing expected spares, rebuild start/progress/finish, mismatch count after checks, device failure, failed spare, spare activation, and disappearance.
- Tracks per-disk state with `md_get_disk_info()` and preferred device paths.
- Stores container/subarray parent relationships from external metadata strings.
- Loads metadata with `super_by_fd()` for top-level arrays/containers when needed for spare migration.

## Spare Migration

- `try_spare_migration()` links containers to subarrays, finds degraded arrays without spares, builds policy domains, obtains spare criteria, and searches donor arrays/containers.
- Native arrays choose spares from per-slot md state.
- External containers reload metadata and use `container_choose_spares()`.
- Moves a spare with `move_spare()` and emits `MoveSpare`.

## Wait Helpers

- `Wait()` waits until mdstat no longer reports a resync/recovery/check/reshape for a device, pings mdmon for external arrays, and handles brief frozen states.
- `WaitClean()` waits for external subarrays to become clean, temporarily lowers safemode delay, polls `array_state`, pings mdmon so metadata is marked clean, and restores safemode delay.

## Invariants and Risks

- Scan mode depends on `/proc/mdstat` plus optional udev wait; fallback wait shortens delay after mdstat events.
- External metadata spare migration must coordinate container/subarray relationships and domain policy to avoid stealing unsuitable spares.
- `struct state` metadata is freed only partially in `free_statelist()`; metadata lifetimes mostly follow monitor loop usage and mdadm process lifetime.
- Only redundant arrays are kept under monitoring; if no redundant array remains, monitor exits.
