# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/model

Symlink to `lsblk`; behavior is selected by invoked basename `model`.

Behavior:
- Runs `lsblk -dl -n -o model` on the resolved vdev path.
- Trims whitespace.
- Prints `model=<device model>`.

Role:
- Provides disk model number as a custom column.
