# File Research: sources/cow-pools/openzfs/cmd/zpool/os/linux/zpool_vdev_os.c

Linux-specific `zpool` vdev validation and enclosure power-control implementation.

Sector-size database:
- Defines `vdev_disk_db_entry_t` and a static table of device inquiry strings known to misreport or require overridden physical sector sizes.
- `check_sector_size_database()` sends a SCSI INQUIRY through `SG_IO`, compares bytes 8-31 against 24-byte database IDs, and returns an override sector size when matched.

Device safety checks:
- `check_slice()` asks `libblkid` for filesystem `TYPE`.
- Empty/unknown type is considered safe.
- `zfs_member` devices are passed to `check_file()` so spare-sharing rules can be applied.
- Non-ZFS filesystems are rejected unless `force` is set.
- `check_disk()` handles whole-disk validation with `O_EXCL` for non-spares, reads EFI/GPT labels with `efi_alloc_and_read()`, scans assigned partitions, and checks each partition path.
- For corrupt primary EFI labels, force allows proceeding via backup-label behavior; otherwise it reports an error.
- `check_device()` owns the `blkid_cache` lifecycle and delegates to `check_disk()`.

Other command hooks:
- `after_zpool_upgrade()` is a Linux no-op.
- `check_file()` delegates to shared `check_file_generic()`.

Sysfs utilities:
- `zpool_sysfs_gets()` reads a sysfs file into an allocated string and strips one trailing newline.
- `zpool_sysfs_puts()` writes a string to a sysfs file.
- `rescan_vdev_config_dev_sysfs_path()` refreshes enclosure sysfs path metadata in a vdev nvlist.

Slot power control:
- `zpool_power_sysfs_path()` finds a vdev with `zpool_find_vdev()`, refreshes enclosure sysfs metadata, then locates either HDD/JBOD `power_status` or NVMe PCI-slot `power`.
- `zpool_power_parse_value()` maps `off`/`0` to 0 and `on`/`1` to 1.
- `zpool_power_use_word()` selects word values for `power_status` and numeric values for `power`.
- `zpool_power_current_state()` reads and parses current power state.
- `zpool_power()` changes state if needed, writes the sysfs value, then polls up to `ZPOOL_POWER_ON_SLOT_TIMEOUT_MS` or 30 seconds by default until the state changes.

Role:
- Implements Linux-specific userland preflight safety for pool device creation.
- Adds Linux-only enclosure/NVMe slot power operations through sysfs.
