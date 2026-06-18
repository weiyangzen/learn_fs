# File Research: sources/block-storage/mdadm/mdopen.c

## Role

`mdopen.c` creates, names, opens, and validates md devices for assemble/build/create workflows.

## Key Functions

- `create_named_array()` writes an md kernel devnm to `/sys/module/md_mod/parameters/new_array`.
- `find_free_devnm()` searches for an unused `mdN`, preferring high minor numbers and avoiding mdstat, config name conflicts, and existing `/dev` nodes when udev is unavailable.
- `create_mddev()` is the main allocator/creator for a new md device.
- `open_mddev()` opens a path and verifies it is an md array with `md_array_valid()`.
- `is_mddev()` wraps `open_mddev()` as a boolean path check.

## create_mddev Behavior

`create_mddev()`:

- Initializes md module parameters and optionally blocks udev for the chosen devnm.
- Accepts user names from `/dev/md/<name>`, `/dev/mdN`, `/dev/md_dN`, bare names, metadata-provided names, or no name.
- Sanitizes metadata names by replacing `/` with `-` and whitespace with `_`.
- Resolves conflicts through map lookup and numeric suffixes.
- Creates named arrays via sysfs when supported.
- Falls back to choosing a free number when explicit creation fails or no number/name is supplied.
- When udev is unavailable, creates block nodes and `/dev/md/<name>` symlinks directly using configured uid/gid/mode.
- Returns an exclusive md device fd via `open_dev_excl()`.

## Invariants and Risks

- User-supplied `/dev/...` names must be standard md names unless represented through `/dev/md/<name>`.
- `chosen` is updated to the preferred user-visible path, falling back to `/dev/mdN` when a requested symlink cannot be used.
- Direct node creation path must verify existing nodes match the expected block device to avoid using stale/wrong nodes.
- Udev blocking is only attempted when udev is available; otherwise mdadm owns node/symlink creation.
