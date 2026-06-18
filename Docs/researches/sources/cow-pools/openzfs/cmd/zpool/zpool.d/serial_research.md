# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/serial

Symlink to `smart`; behavior is selected by invoked basename `serial`.

Behavior:
- Parses serial number lines from SAS/SATA/NVMe SMART output.
- Prints `serial=<serial number>` or `serial=`.

Role:
- Reports disk serial number through SMART data rather than `lsblk`.
