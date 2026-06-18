# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/slot

Symlink to `ses`; behavior is selected by invoked basename `slot`.

Behavior:
- For PCI slot paths, uses the basename of `VDEV_ENC_SYSFS_PATH`.
- For enclosure paths, reads `<VDEV_ENC_SYSFS_PATH>/slot`.
- Prints `slot=<slot>` or `slot=`.

Role:
- Reports enclosure or PCI slot number for a vdev.
