# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_tabletsw.c

## Purpose
Implements SSAM tablet-mode switch devices. It supports KIP cover-state based tablet mode and POS posture-source based tablet mode, reports `SW_TABLET_MODE` through the input subsystem, and exposes the current textual state via sysfs.

## Important APIs, Types, And Functions
Generic framework types are `struct ssam_tablet_sw_state`, `struct ssam_tablet_sw_ops`, `struct ssam_tablet_sw`, and `struct ssam_tablet_sw_desc`. Core lifecycle functions are `ssam_tablet_sw_probe()`, `ssam_tablet_sw_remove()`, `ssam_tablet_sw_update_workfn()`, resume handling, and `state_show()`. KIP-specific functions map cover states and query command `0x1d`. POS-specific functions query source lists, select a source, query posture for that source, map cover/SLS postures, and handle posture-change events. The module parameter `tablet_mode_in_slate_state` controls SLS slate behavior.

## Control Flow
Probe gets descriptor match data, allocates state, reads initial state through descriptor ops, allocates/registers an input device, registers a sequenced SSAM event notifier, creates the `state` sysfs attribute, and schedules an update to catch missed setup-time events. Notifier callbacks validate command IDs and schedule update work. Update work re-queries firmware, compares source/state with cached values, updates state, maps it to tablet mode, and reports/input-syncs `SW_TABLET_MODE`.

## State And Persistence Behavior
Runtime state caches the latest source and state values plus input device and notifier registration. No persistent storage exists. Sysfs reads return the cached state name, not a fresh firmware query. Work is canceled and notifier/sysfs removed on driver remove.

## Dependencies And Integration Points
Depends on SSAM device/controller APIs, synchronous request helpers, SSAM event notifiers, input subsystem, sysfs attribute groups, unaligned access, and module parameters. It binds `SSAM_SDEV(KIP, SAM, 0x00, 0x01)` and `SSAM_SDEV(POS, SAM, 0x00, 0x01)`, which are instantiated by the registry for relevant models.

## Risks
Unknown posture/source values default to tablet mode for safety but may produce unexpected userspace behavior. POS currently warns if more than one posture source exists and uses the first source; future multi-source devices need policy changes. Event payload-size mismatches only warn, because state is always re-queried. Sysfs state can be stale if a firmware query fails during update.

## Test Signals
Test KIP states disconnected/closed/laptop/folded/book, POS cover and SLS states, module parameter behavior for slate, event-triggered updates, resume re-query, sysfs state output, unknown states, malformed event payload lengths, and probe/remove notifier cleanup.
