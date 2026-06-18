# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/enc

Symlink to `ses`; behavior is selected by invoked basename `enc`.

Behavior:
- Reads `VDEV_ENC_SYSFS_PATH`.
- If no enclosure sysfs path is set, prints `enc=`.
- For PCI slot paths under `/sys/bus/pci/slots`, returns that sysfs path.
- For normal enclosure paths, lists the parent enclosure directory name.
- Prints `enc=<value>`.

Role:
- Provides the enclosure identifier custom column.
