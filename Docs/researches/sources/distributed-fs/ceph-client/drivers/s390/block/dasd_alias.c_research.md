# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_alias.c

## Purpose

`dasd_alias.c` manages Parallel Access Volume alias devices for the DASD ECKD discipline. It keeps a server/LCU/PAV-group model, connects devices to LCUs as they are discovered, moves serviceable devices into active PAV groups, selects alias devices for I/O load distribution, refreshes unit-address configuration, and handles summary unit check recovery.

## Important APIs, Types, and Functions

- The file-level `aliastree` is an `alias_root` containing all known storage servers and protected by a spinlock.
- `_find_server()`, `_find_lcu()`, and `_find_group()` locate the storage server, logical control unit, and PAV group matching a DASD UID.
- `_allocate_server()`, `_allocate_lcu()`, `_free_server()`, and `_free_lcu()` allocate and release alias-management structures and embedded work/CQR resources.
- `dasd_alias_make_device_known_to_lcu()` creates or reuses the server and LCU for a device and links the device into the LCU inactive list.
- `dasd_alias_disconnect_device_from_lcu()` cancels pending workers that reference the device, unlinks the device, and frees empty LCU/server structures.
- `dasd_alias_add_device()`, `dasd_alias_update_add_device()`, and `dasd_alias_remove_device()` mark devices active or inactive for PAV use.
- `read_unit_address_configuration()` sends PSF/RSSD commands to populate the LCU unit-address configuration (`uac`).
- `_lcu_update()`, `lcu_update_work()`, and `_schedule_lcu_update()` refresh PAV mode and group membership asynchronously.
- `dasd_alias_get_start_dev()` selects a usable alias for a base device.
- `dasd_alias_handle_summary_unit_check()` and `summary_unit_check_handling_work()` stop devices, flush alias queues, reset summary unit check, restart base devices, and trigger an LCU refresh.

## Control Flow

Discovery calls `dasd_alias_make_device_known_to_lcu()`. The function reads the device UID via the ECKD discipline, creates the server and LCU outside the global lock when needed, then rechecks under lock to handle races. The device is initially linked into `lcu->inactive_devices` and records the LCU in its private data.

When a device becomes serviceable, `dasd_alias_add_device()` checks whether the device UID type matches the current LCU unit-address data. If the LCU is current, `_add_device_to_lcu()` updates the device UID from `uac`, determines the LCU PAV mode, creates/fetches a PAV group, and moves the device into a base or alias list. If the LCU data is stale, the device goes to `active_devices`, `UPDATE_PENDING` is set, and `_schedule_lcu_update()` queues a delayed worker using a referenced device.

The update worker first dissolves existing PAV groups back into `active_devices`, reads UAC data using PSF/RSSD, determines `NO_PAV`, `BASE_PAV`, or `HYPER_PAV`, and rebuilds groups. Hyper PAV uses a single group, while base PAV groups by base unit address and VDUIT. If another update is requested during the read, the worker leaves grouping incomplete and retries later.

For each I/O, `dasd_alias_get_start_dev()` checks that PAV is enabled and not pending update, verifies prefix support, finds the base device's PAV group, advances the round-robin `group->next` pointer, and returns an alias only if its outstanding count is lower than the base, it is not stopped, and it is not offline.

Summary unit check recovery is a separate work path. The entry function sets `DASD_STOPPED_SU` on all LCU devices, marks UAC update pending, stores the reason, and schedules work. The worker flushes alias queues without holding the LCU lock during blocking flushes, clears stop bits on the reporting device to issue RSCK, unstops devices, restarts base devices, and schedules a UAC refresh.

## State and Persistence Behavior

All state is in memory. Important state includes the global alias tree, LCU flags (`NEED_UAC_UPDATE`, `UPDATE_PENDING`), the LCU `uac` table, PAV mode, active/inactive device lists, PAV group base/alias lists, per-device `private->lcu` and `private->pavgroup`, worker-owned referenced devices, and summary unit check reason. The code uses reference counts (`dasd_get_device`/`dasd_put_device`) around asynchronous workers and cancels workers during disconnect to avoid use-after-free.

## Dependencies and Integration Points

The implementation depends on ECKD-specific UID and CCW definitions from `dasd_eckd.h`, core request allocation/sleep helpers, Linux workqueues, spinlocks, CCW device locks, and DASD scheduling helpers. It is used by the ECKD discipline during check/add/remove and by the ERP code when an alias request must recover on the base device. It also coordinates with device stop bits and block/device bottom halves to pause and restart I/O.

## Risks

The highest risks are concurrency and lifetime issues: devices can go offline while update or summary-unit-check work is pending, and list membership changes while queues are flushed unlocked. UAC reads can fail transiently or be unsupported; the code must distinguish retryable failure from `-EOPNOTSUPP`. Alias selection is intentionally simple and can underutilize aliases if `count`, stop bits, or offline flags lag. Stale dynamic PAV mappings can route work to the wrong alias until a reload/update path runs.

## Test Signals

Important signals include correct server/LCU/group construction for base PAV and Hyper PAV, worker cancellation on disconnect, no leaked references after update and summary-unit-check paths, alias selection only returning online unstopped aliases with lower load, recovery from UAC mismatch, and RSCK/UAC refresh after summary unit check. DBF warnings, stop-bit state, list membership, and device reference counts are the main runtime evidence.
