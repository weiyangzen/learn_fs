# sources/distributed-fs/ceph-client/drivers/md/dm-ioctl.c

### Purpose
`dm-ioctl.c` implements the `/dev/mapper/control` userspace ABI for Device Mapper. It creates/removes/renames mapped devices, loads and swaps mapping tables, reports status/dependencies/target versions, sends target messages, waits and polls for events, and supports early-boot mapped-device creation.

### Important APIs, Types, And Functions
External entry points include `dm_interface_init`, `dm_interface_exit`, `dm_deferred_remove`, `dm_copy_name_and_uuid`, and `dm_early_create`. The miscdevice file operations are `_ctl_fops`, using `dm_open`, `dm_release`, `dm_poll`, `dm_ctl_ioctl`, and optional compat ioctl.

Important internal types are `struct dm_file` for poll state, `struct hash_cell` for name/uuid/device tracking plus an inactive `new_map`, and `struct vers_iter` for target-version listing. The two rbtrees `name_rb_tree` and `uuid_rb_tree` are protected by `_hash_lock`; `dm_hash_cells_mutex` protects `mdptr` name/uuid access.

Core operations include hash lookup/insert/remove/rename helpers, `dev_create`, `dev_remove`, `dev_rename`, `do_suspend`, `do_resume`, `table_load`, `table_clear`, `table_deps`, `table_status`, `target_message`, `lookup_ioctl`, `check_version`, `copy_params`, `validate_params`, and `ctl_ioctl`.

### Control Flow
`ctl_ioctl` requires `CAP_SYS_ADMIN`, validates the ioctl type, checks userspace ABI version while copying the kernel version back, maps the command number through `lookup_ioctl`, copies parameters into kernel memory, validates names/uuids and flags, calls the selected handler, optionally issues a global event, copies results back to userspace, and wipes secure buffers when requested.

Device creation validates names, optionally uses a persistent minor, calls `dm_create`, inserts a hash cell, and returns status. Removal locks a device for deletion, unlinks the hash cell, destroys any inactive table, emits IMA and uevents, and destroys the mapped device. Rename changes name or sets a UUID under the hash lock, emits table events and uevents, and measures through IMA.

Table load creates a `dm_table`, parses each `dm_target_spec` with strict alignment and NUL-termination checks, completes the table, checks immutable target and queue type constraints, sets up the queue on first load, and stages the table as `hc->new_map`. Resume optionally suspends, swaps `new_map` into the live table, updates disk read-only state, resumes the device, emits resize/change events, and destroys the old table after synchronization. Status and deps acquire live or inactive tables via SRCU and serialize results into the ioctl buffer.

### State And Persistence Behavior
The control plane maintains in-kernel rbtrees by name and uuid, references on `mapped_device`, inactive tables staged per hash cell, per-open poll event snapshots, and global event notifications. It does not persist mappings by itself; persistence is userspace policy. `DM_SECURE_DATA_FLAG` causes copied ioctl buffers to be wiped before return/free. Early boot creation bypasses normal serialized ioctl payloads by accepting prebuilt target spec/parameter arrays, but still creates a device, inserts it in the hash, builds a table, swaps it live, and resumes it.

### Dependencies And Integration Points
This file integrates with DM core (`dm_create`, `dm_destroy`, `dm_suspend`, `dm_resume`, `dm_table_*`, `dm_swap_table`, `dm_get_live_table`, `dm_get_mdptr`), target registry iteration, DM stats messages, IMA measurement hooks, kobject uevents, miscdevice registration, Linux usercopy, capabilities, polling, SRCU table lifetime rules, and block device geometry/read-only state.

### Risks And Edge Cases
The ABI parser is security-sensitive: `data_size`, `data_start`, target `next` offsets, alignment, and NUL termination must be checked exactly to avoid overreads or corrupt target loading. Hash locking is subtle because table destruction waits for live table references and must not happen under `_hash_lock` in paths that could deadlock. `find_device` returns an `md` with a reference acquired by hash lookup; every path must balance `dm_put`. `DM_SECURE_DATA_FLAG` must wipe both user and kernel buffers. Race-prone areas include deferred removal, rename versus lookup, inactive table replacement, suspend failure rollback, and uevent/global-event generation.

### Test Signals
Tests should cover all ioctl commands, invalid version negotiation, invalid names and uuid/name conflicts, buffer-full reporting, secure-data wiping, target spec alignment and missing NULs, inactive table load/clear/resume rollback, immutable target rejection, deferred remove cancellation, event wait/poll behavior, status/deps output against live and inactive tables, target messages with DM-core `@` commands, compat ioctl paths, and early boot create failure cleanup.
