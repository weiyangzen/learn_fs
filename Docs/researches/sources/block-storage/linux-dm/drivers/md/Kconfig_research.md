# File Research: sources/block-storage/linux-dm/drivers/md/Kconfig

## Purpose
Defines the Kconfig surface for the kernel multiple-device block stack: MD RAID personalities, bcache, and device-mapper core and targets.

## Main Interfaces
- Top-level `MD` menu depends on `BLOCK` and selects `SRCU`.
- MD options include `BLK_DEV_MD`, boot `MD_AUTODETECT`, `MD_LINEAR`, `MD_RAID0`, `MD_RAID1`, `MD_RAID10`, `MD_RAID456`, `MD_MULTIPATH`, `MD_FAULTY`, and `MD_CLUSTER`.
- Includes `drivers/md/bcache/Kconfig`.
- Device-mapper options include `BLK_DEV_DM`, debug support, helper libraries such as `DM_BUFIO` and `DM_BIO_PRISON`, and many targets: crypt, snapshot, thin, cache, writecache, ebs, era, clone, mirror, raid, zero, multipath, delay, dust, flakey, verity, switch, log-writes, integrity, zoned, and audit.

## Control Flow
The file is declarative: selecting an option controls compilation through the adjacent Makefile and pulls in required helper symbols with `select` or `depends on`. MD RAID is configured first, then bcache, then DM core and targets.

## Integration Points
DM RAID selects MD RAID personalities and `BLK_DEV_MD`. Thin, cache, era, clone, verity, integrity, and zoned targets select shared DM metadata, bufio, crypto, checksum, or block-integrity infrastructure as needed. `source "drivers/md/persistent-data/Kconfig"` and bcache's Kconfig extend the menu.

## Notable Behaviors
- Several legacy MD personalities are explicitly marked deprecated.
- `BLK_DEV_DM` requires `DAX || DAX=n`, which prevents incompatible built-in/module combinations.
- `DM_INIT` only exists for built-in `BLK_DEV_DM=y`, enabling early `dm-mod.create=` devices for rootfs use.
- Verity root-hash signature support is split between primary trusted keyring and optional secondary keyring.

## Risks And Review Focus
- Build dependencies must prevent illegal built-in/module combinations, especially for DAX, SCSI device handlers, crypto, and audit.
- `select` chains for shared helpers are correctness-sensitive because Makefile objects assume those symbols are present.
- Any new DM target should be wired here and in `drivers/md/Makefile` consistently.
