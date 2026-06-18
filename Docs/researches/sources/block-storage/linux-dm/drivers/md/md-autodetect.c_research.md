# File Research: sources/block-storage/linux-dm/drivers/md/md-autodetect.c

## Purpose
Implements built-in-kernel MD boot-time array setup and RAID autodetection for `raid=` and `md=` kernel command-line parameters.

## Main Interfaces
- Boot parameter parsers: `raid_setup()` for `raid=`, `md_setup()` for `md=`.
- Setup execution: `md_run_setup()`.
- Autodetect path: `autodetect_raid()` and `md_autostart_arrays()`.
- Explicit array assembly: `md_setup_drive()`.

## Control Flow
`md_setup()` records up to 256 requested MD arrays in `md_setup_args`, parsing optional partitionable-device syntax (`mdd`), MD minor, optional RAID level/chunk/fault fields for non-persistent linear or RAID0, and a comma-separated component-device list. It only stores the command-line intent; actual assembly waits until device probing has completed.

`md_run_setup()` first optionally waits for device probing and starts autodetected arrays unless `raid_noautodetect` is set. It then iterates recorded `md=` entries and calls `md_setup_drive()`. That function resolves component names to device numbers, opens the target MD block device, verifies it is backed by `md_fops`, locks the `mddev`, skips already configured arrays, optionally initializes non-persistent array info, adds each component with `md_add_new_disk()`, and calls `do_md_run()`.

## State And Synchronization
Boot-time state is stored in `__initdata` globals: `raid_noautodetect`, `raid_autopart`, `md_setup_args`, and `md_setup_ents`. Runtime MD state is protected by `mddev_lock()` while array info and disk membership are configured.

## Integration Points
Uses kernel boot `__setup()` parsing, `wait_for_device_probe()`, `name_to_dev_t()`, `init_stat()` for `/dev` path resolution, MD array management functions (`md_set_array_info()`, `md_add_new_disk()`, `do_md_run()`), and MD major/minor conventions including partitionable MD devices.

## Notable Behaviors
- `CONFIG_MD_AUTODETECT` controls the default for `raid_noautodetect`; without it autodetection is disabled by default.
- Duplicate `md=` definitions for the same minor and partitionable flag replace earlier definitions.
- Non-persistent `md=n,0,...` and `md=n,-1,...` paths synthesize array info for RAID0 or linear.
- Persistent-superblock arrays are started by supplying only the device list and letting MD inspect component metadata.
- The parser supports `raid=autodetect`, `raid=noautodetect`, `raid=partitionable`, and `raid=part`.

## Risks And Review Focus
- This code mutates the command-line device list in place by replacing commas with NULs.
- Device-name resolution combines `name_to_dev_t()` with `/dev` stat probing, so boot environment naming behavior is correctness-sensitive.
- Explicit setup skips arrays already autodetected, which can surprise boot configurations unless `raid=noautodetect` is used.
