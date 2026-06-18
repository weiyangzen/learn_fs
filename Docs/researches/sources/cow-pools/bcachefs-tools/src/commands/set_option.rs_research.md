# File Research: sources/cow-pools/bcachefs-tools/src/commands/set_option.rs

## Purpose
Implements `bcachefs set-fs-option`, allowing filesystem and device options to be changed either online through sysfs or offline by editing superblock options.

## Main Interfaces
- Command export: `CMD = raw_cmd!("set-fs-option", ...)`
- Main functions:
  - `set_option_cmd`
  - `cmd_set_option`
  - `set_option_online`
  - `set_option_offline`
  - `name_to_dev_idx`

## Behavior
- Dynamically builds clap arguments for all filesystem/device options using `bch_option_args`.
- Requires at least one device path and at least one option.
- Detects online mode if any supplied device is mounted through sysfs.
- Online mode opens the first device as a mounted filesystem handle, verifies additional devices are members by UUID, then writes fs options to `options/<name>` and device options to `dev-<idx>/<name>`.
- Offline mode opens devices with `nostart`, parses option values with filesystem context, runs pre-set hooks, and writes fs/device values into the superblock.
- Device option targeting can be explicit with `--dev-idx` or inferred from supplied device names.

## Dependencies and Coupling
- Uses shared option helpers from `commands::opts`.
- Uses `BcachefsHandle` and sysfs write helpers for online changes.
- Uses C functions:
  - `bch2_opt_parse`
  - `bch2_opt_hook_pre_set`
  - `bch2_opt_set_sb`
- Uses raw `(*fs.raw).devs` traversal for device lookup.

## Important Implementation Notes
- Online device-scoped writes open each device to discover its device index, then write through the first filesystem handle’s sysfs fd.
- Offline `name_to_dev_idx` compares the bcachefs device name field, not necessarily the path.
- Errors for individual invalid/unsupported options are printed and processing continues.

## Risks and Edge Cases
- If any device is mounted, the command treats the whole operation as online.
- Offline device inference by internal device name may not match user-supplied paths.
- Online writes ignore return values from `sysfs_write_str`.
- Superblock writes are not followed by an explicit `fs.write_super()` in this file after offline option mutation, so persistence depends on wrapper/drop behavior or C side effects.
