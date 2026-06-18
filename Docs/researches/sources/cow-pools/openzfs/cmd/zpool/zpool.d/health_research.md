# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/health

Symlink to `smart`; behavior is selected by invoked basename `health`.

Behavior:
- Runs/parses `smartctl -a`.
- Supports SAS `SMART Health Status`, SATA `SMART overall-health self-assessment test result`, and NVMe health output.
- Normalizes multi-word SAS health strings with underscores.
- Prints `health=<status>` or `health=`.

Role:
- Provides a drive-reported SMART health custom column across SAS/SATA/NVMe.
