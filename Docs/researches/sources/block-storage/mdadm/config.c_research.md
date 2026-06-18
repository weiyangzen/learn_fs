# File Research: sources/block-storage/mdadm/config.c

## Purpose
`config.c` parses mdadm configuration files and exposes configuration-derived device lists, array identities, monitor settings, create defaults, homehost/homecluster, auto-assembly policy, probing flags, and encryption verification settings.

## Main Flow
`load_conffile()` loads the selected config file, fallback Debian config, and `.d` directory entries. `conf_file_or_dir()` handles a regular file or sorted `.conf` directory entries. `conf_file()` reads logical lines through `conf_line()` and dispatches by keyword.

Line handlers parse:
- `DEVICE` into scan patterns, `partitions`, or `containers`.
- `ARRAY` into `mddev_ident` entries with UUID, device name, metadata, bitmap, devices pattern, spare group, container/member, and compatibility fields.
- `CREATE` into ownership, mode, metadata, names, and bad-block defaults.
- `AUTO` into metadata auto-assembly policy rules.
- monitor mail/program/from/delay settings.
- `HOMEHOST`, `HOMECLUSTER`, `POLICY`, `PART-POLICY`, `SYSFS`, `ENCRYPTION_NO_VERIFY`, and `PROBING`.

## Key Behavior
- Device-name validation accepts md numbered devices, `/dev/md/<name>`, `md_<name>`, bare names, and config-only `<ignore>`.
- `conf_get_devs()` defaults to `/proc/partitions` plus external containers when no DEVICE lines exist, otherwise expands configured globs.
- `conf_test_metadata()` evaluates auto-assembly policy with `yes`, `no`, and `homehost` precedence.
- `conf_match()` matches loaded superblock info against ARRAY lines by UUID, device patterns, super-minor, and identity presence, rejecting ambiguous matches.
- `conf_verify_devnames()` detects duplicate configured md names.

## Integration Notes
The file uses the local `dlink` word-list abstraction from `lib.c` tokenization, global policy helpers, metadata supertype matchers, mdstat/map helpers, glob/fnmatch, `/proc/partitions`, and external container discovery.

## Risks
Configuration state is stored globally and loaded once. Parser leniency preserves compatibility but can hide bad lines. `AUTO` policy ordering is significant, and config/device glob expansion affects assembly behavior system-wide.
