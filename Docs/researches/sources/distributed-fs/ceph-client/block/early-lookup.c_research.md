# sources/distributed-fs/ceph-client/block/early-lookup.c

Purpose: resolves early-boot root/device specifiers into `dev_t` before the root filesystem is mounted and prints available partitions when mounting fails.

Important APIs and functions: `early_lookup_bdev()` is the main resolver. Helpers include `devt_from_partuuid()`, `devt_from_partlabel()`, `devt_from_devname()`, `devt_from_devnum()`, `blk_lookup_devt()`, `match_dev_by_uuid()`, `match_dev_by_label()`, `bdevt_str()`, and `printk_all_partitions()`.

Control flow: `early_lookup_bdev()` recognizes `PARTUUID=`, `PARTLABEL=`, `/dev/...`, decimal major:minor, major:minor:offset syntax, and legacy hexadecimal device numbers. PARTUUID matching can parse `/PARTNROFF=<int>` and derive a relative partition number. `/dev/` names replace slashes with `!`, try an exact disk name, then parse trailing partition numbers including the `pN` convention for disk names ending in digits. Partition listing iterates block-class disks and their xarray partition table under RCU and prints hex devt, size, name, UUID, and driver.

State and persistence: this file stores no lasting state. It reads current block-class devices, disk partition tables, and partition metadata populated by earlier probing.

Dependencies and integration points: depends on the block device class, `disk_type`, `dev_to_bdev()`, `dev_to_disk()`, partition metadata (`bd_meta_info`), `part_devt()`, `new_decode_dev()`, early init annotations, and kernel boot/root mount diagnostics.

Risks and test signals: malformed PARTUUID syntax must fail clearly, UUID matching uses prefix length before optional suffix, and devname parsing must distinguish disk names ending in digits from partition suffixes. Test root by PARTUUID, PARTUUID/PARTNROFF positive and negative offsets, PARTLABEL, `/dev/sda1`, `/dev/nvme0n1p1`, major:minor, hex devt, hidden/empty disks in partition printing, and devices whose partitions appear only after opening.
