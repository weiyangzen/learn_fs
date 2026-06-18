# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/cmd_to

Symlink to `smart`; behavior is selected by invoked basename `cmd_to`.

Behavior:
- Resolves the vdev path from `VDEV_UPATH` or `VDEV_PATH`.
- Runs and parses `smartctl -a`.
- Extracts SATA `Command_Timeout` raw value into `cmd_to=<value>`.
- Emits `cmd_to=` when no value is found.

Role:
- Provides a custom column for ATA/SATA command timeout count.
