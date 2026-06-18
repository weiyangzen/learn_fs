# File Research: sources/block-storage/lvm2/lib/lvmpolld/polldaemon.h

Purpose: defines shared polling abstractions for long-running LVM operations, including progress states, operation identity, daemon parameters, and callbacks used by foreground or daemon-backed polling.

Read coverage: complete file read, 77 lines.

Key contents:
- Defines `progress_t` states: failed, unfinished, finished current segment, and finished all.
- Defines `struct poll_functions`, the operation-specific callbacks for copy-name lookup, progress polling, metadata update, and finalization.
- Defines `struct poll_operation_id` with VG name, LV name, display name, and UUID.
- Defines `struct daemon_parms` with polling interval, delay behavior, abort/background flags, outstanding count, progress-display fields, LV type flags, callback table, and devicesfile name.
- Declares `poll_daemon()`, `poll_mirror_progress()`, and `wait_for_single_lv()`.

Dependencies:
- Includes `metadata-exported.h` for `logical_volume`, `volume_group`, LV type flags, and LVM metadata types.
- Used by lvmpolld client code and local polling code.

Risk and edge cases:
- `daemon_parms.devicesfile` has a fixed 128-byte buffer, so callers must preserve truncation/validation guarantees before populating it.
- Callback implementations must follow the progress-state contract so poll loops know whether to continue, update metadata, or finish.
- Operation IDs require stable UUID/name values because daemon requests and local status messages depend on them.
