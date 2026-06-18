# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/encdev

Symlink to `ses`; behavior is selected by invoked basename `encdev`.

Behavior:
- Reads `VDEV_ENC_SYSFS_PATH`.
- Lists `../device/scsi_generic` below the enclosure slot path.
- Prints `encdev=<sg device>` or `encdev=`.

Role:
- Reports the SCSI generic enclosure device associated with a vdev slot.
