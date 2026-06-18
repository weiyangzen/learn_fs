# File Research: sources/cow-pools/bcachefs-tools/src/commands/mount.rs

## Purpose
Implements `bcachefs mount`, including device discovery by UUID/device string, encrypted filesystem unlocking, kernel module probing, mount-option splitting, direct kernel mount, and delegation to FUSE mounting for `-t bcachefs.fuse`.

## Main Interfaces
- CLI struct: `Cli`
- Command export: `CMD`
- Key functions:
  - `mount`
  - `cmd_mount_inner`
  - `mount_inner`
  - `parse_mountflag_options`
  - `handle_unlock`
  - `check_bcachefs_module`

## Behavior
- Splits comma-separated mount options into Linux mount flags and bcachefs-specific options.
- Scans superblocks and joins member devices into the mount source string.
- Detects encrypted superblocks and unlocks using explicit policy, passphrase file, keyring search, or prompt.
- If mountpoint is absent, performs discovery/unlock but does not call `mount`.
- Calls `libc::mount` with filesystem type `bcachefs`.
- If write mount fails with `EACCES` or `EROFS`, retries read-only.
- If `--type bcachefs.fuse` is requested, constructs a `fusemount::Cli` and calls `cmd_fusemount`.
- Logs failure and hints when the bcachefs module was not loaded.

## Dependencies and Coupling
- Uses `device_scan::scan_sbs` and `joined_device_str`.
- Uses `KeyHandle`, `Keyring`, `Passphrase`, and `UnlockPolicy`.
- Uses `bch2_sb_is_encrypted` C helper.
- Delegates FUSE path to `commands::fusemount`.
- Uses `logging::setup` for color/verbosity.

## Important Implementation Notes
- Mount flags recognized include standard VFS flags and ignored userspace/fstab-only options.
- Unknown mount options are passed through to bcachefs as filesystem-specific option string.
- `CString`s are held in local bindings through the `mount` syscall.
- `check_bcachefs_module` attempts `modprobe bcachefs`.

## Risks and Edge Cases
- FUSE mode uses an empty mountpoint string if none is supplied, likely causing a later mount failure.
- Mountinfo and device scanning behavior live outside this file.
- The `fs_type` argument is accepted but only special-cases `bcachefs.fuse`; normal path always mounts as `bcachefs`.
