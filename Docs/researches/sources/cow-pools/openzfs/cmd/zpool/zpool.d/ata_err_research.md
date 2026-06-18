# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/ata_err

Symlink to `smart`; behavior is selected by invoked basename `ata_err`.

Behavior:
- Uses `VDEV_UPATH` when it is a block device, otherwise falls back to `VDEV_PATH`.
- Runs `sudo smartctl -a` when available, or optional developer sample output.
- Parses SMART output with awk.
- For `ata_err`, extracts ATA/SATA `ATA Error Count:` into `ata_err=<count>`.
- If unavailable, prints `ata_err=`.

Role:
- Provides a `zpool status -c ata_err` custom column for ATA error count.
