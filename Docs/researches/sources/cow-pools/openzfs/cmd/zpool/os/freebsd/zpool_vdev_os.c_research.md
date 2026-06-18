# File Research: sources/cow-pools/openzfs/cmd/zpool/os/freebsd/zpool_vdev_os.c

FreeBSD-specific `zpool` vdev helper implementation.

Core behavior:
- `check_device()` normalizes device names to `/dev/...` when needed, then delegates validation to `check_file()`.
- `check_file()` delegates to shared `check_file_generic()`.
- `check_sector_size_database()` is a stub returning false; FreeBSD does not use the Linux SCSI inquiry override table here.
- `after_zpool_upgrade()` warns when a pool has `bootfs` set, telling the user they may need to update boot code and referencing `gptzfsboot(8)` and `loader.efi(8)`.
- `zpool_power_current_state()` returns `-1`, marking enclosure slot power state unsupported.
- `zpool_power()` returns `ENOTSUP`, marking slot power control unsupported.

Dependencies:
- Uses FreeBSD device/path headers, `libgeom`, ZFS nvlist/libzutil interfaces, and shared `zpool_util.h`.

Role:
- Supplies the OS abstraction functions required by common `zpool` vdev code.
- FreeBSD validation is intentionally thinner than Linux here and relies on generic file checks plus `/dev` path normalization.
