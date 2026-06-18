# File Research: sources/block-storage/mdadm/mdadm.c

## Role

`mdadm.c` is the main command-line entry point for mdadm. It parses global and mode-specific options, validates cross-option constraints, initializes context/shape/identity state, opens target md devices where needed, checks privilege and cluster locks, and dispatches to the mode implementations in other source files.

## Primary State

`main()` builds and mutates these central objects:

- `mode`, selected from assemble/build/create/manage/monitor/grow/incremental/misc/autodetect.
- `struct context c`, holding runtime policy such as verbosity, scan, force, readonly, run/stop, homehost, homecluster, metadata, update, backup file, delay, export, test, and cluster nodes.
- `struct shape s`, holding array geometry and creation/grow parameters such as level, layout, chunk, size, raid/spare/journal disks, bitmap type/chunk, consistency policy, data offset, write-behind, write-zeroes, and logical block size.
- `struct mddev_ident ident`, holding target array identity.
- `struct mddev_dev *devlist`, the ordered devices and per-device dispositions accumulated from CLI arguments.

## Helper Functions

- `set_bitmap_value()` validates `--bitmap=` values and sets bitmap type, including cluster defaults.
- `shape_set_logical_block_size()` parses and range-checks `--logical-block-size=`.
- `scan_assemble()` assembles arrays from config, repeatedly handling dependency/stacking cases, and optionally auto-assembles homehost arrays.
- `misc_scan()` applies detail or wait-clean to mdstat-listed arrays, including external metadata member ordering and mapfile path lookup.
- `stop_scan()` repeatedly stops mdstat-listed arrays until no progress is possible, supporting stacked devices.
- `misc_list()` dispatches per-device misc operations.
- `SetAction()` writes a requested sysfs `sync_action`.

## Option Parsing

The parser first handles mode-independent options, then determines or verifies the command mode, then processes mode-specific options using `O(mode,opt)` pairs. It enforces single-use options, validates numeric ranges, maps textual values through `maps.c`, and rejects invalid combinations early.

Notable validations include:

- Mode conflicts are fatal.
- A second undecorated device before selecting a mode is rejected.
- Build mode only permits specific RAID levels.
- Layout parsing depends on level.
- `--update=` is restricted differently for assemble, misc subarray updates, and manage re-add.
- `--backup-file` conflicts with `--data-offset`.
- Logical block size is supported only for metadata 1.x.
- Write journal requires RAID4/5/6 and compatible consistency policy.
- PPL is restricted to RAID5.
- Bitmap and consistency-policy combinations are checked.
- Superuser privileges are required except examine and monitor no-sharing cases.

## Mode Dispatch

- `MANAGE`: applies readonly state, subdevice operations, run/stop.
- `ASSEMBLE`: handles direct assembly, config-derived single-device assembly, listed scan assembly, or full config/auto scan.
- `BUILD`: validates no bitmap/write-behind misuse and calls `Build()`.
- `CREATE`: validates clustered bitmap/node restrictions, default bitmap prompting, and calls `Create()`.
- `MISC`: dispatches examine, detail-platform, scan stop/detail/wait-clean, udev rules, or per-device misc operations.
- `MONITOR`: validates devices or scan, daemon/pid constraints, default delay from config, and calls `Monitor()`.
- `GROW`: handles apparent array-size changes, add-device grow, bitmap changes, continue, reshape, and consistency-policy changes.
- `INCREMENTAL`: handles map rebuild, scan/run, fail/remove, or normal incremental add.
- `AUTODETECT`: calls kernel autodetect.

It frees any selected supertype, releases cluster DLM locks, closes the md fd, and exits with the mode return value.

## Dependencies

`mdadm.c` depends on almost every major mdadm subsystem: option tables/help text from common headers, metadata supertype registry, md device open/stat helpers, config parsing, mapfile locking, create/build/assemble/manage/grow/incremental/monitor/misc implementation files, cluster locking, sysfs helpers, and kernel ioctl structures from `md_u.h`/`md_p.h`.

## Important Invariants

- Mode must be known before interpreting most options.
- The first device is the md array for manage/build/create/grow and non-scan assemble.
- Device dispositions are stateful: options such as `--add`, `--fail`, `--remove`, `--replace`, and `--with` affect following device arguments.
- `--scan` implies brief output unless verbosity is high.
- Clustered arrays require DLM locking before create/manage/grow/incremental operations that can affect clustered state.
- Many high-risk operations are blocked unless force, backup files, or staged size changes are provided.

## Risks

This file is a dense compatibility parser. Small changes can alter longstanding CLI behavior, implicit mode selection, or dangerous-operation safeguards. Any new option needs updates across long option tables, short option mode sets, parser validation, dispatch code, mappings if textual, and `mdadm.8.in`.
