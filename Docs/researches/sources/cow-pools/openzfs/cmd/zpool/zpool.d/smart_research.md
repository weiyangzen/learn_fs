# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/smart

Main SMART custom-column helper.

Behavior:
- `-h` prints help for the invoked basename.
- Uses `VDEV_UPATH` when valid, otherwise `VDEV_PATH`.
- Runs `sudo smartctl -a` if the target is a block device and `smartctl` exists.
- Includes a developer `samples` hook for parsing saved smartctl outputs.
- Awk parser detects SAS, SATA, and NVMe output and extracts health, temperature, hours, serial, error counters, lifetime processed data, and self-test fields.
- If drive type cannot be detected or smartctl fails, defaults to `sata` with empty values.

When invoked as `smart`:
- SAS columns: `temp`, `health`, `r_ucor`, `w_ucor`.
- SATA columns: `temp`, `health`, `ata_err`, `realloc`, `rep_ucor`, `cmd_to`, `pend_sec`, `off_ucor`.
- NVMe columns: `temp`, `health`, `nvme_err`.

Output:
- Prints found `key=value` lines.
- Prints missing requested keys with empty values so column output remains stable.

Role:
- Aggregates the most important SMART failure-predictor fields for `zpool status -c smart`.
