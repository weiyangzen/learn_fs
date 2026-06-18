# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/ses

Shell helper for SCSI Enclosure Services and PCI slot metadata.

Behavior:
- `-h` prints basename-specific help.
- If invoked as `ses`, reports `enc`, `encdev`, `slot`, `fault_led`, and `locate_led`.
- Otherwise reports only the invoked basename.
- Uses `VDEV_ENC_SYSFS_PATH`.
- Handles both normal enclosure paths and NVMe PCI slot paths under `/sys/bus/pci/slots`.
- Reads sysfs files for slot number, fault/attention LED, and locate LED.
- Prints each requested item as `name=value`.

Role:
- Provides enclosure identity, slot, device, and LED state custom columns.
