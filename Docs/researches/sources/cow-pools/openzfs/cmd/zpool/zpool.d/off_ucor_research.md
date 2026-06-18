# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/off_ucor

Symlink to `smart`; behavior is selected by invoked basename `off_ucor`.

Behavior:
- Parses ATA/SATA SMART attributes.
- Extracts `Offline_Uncorrectable` raw value into `off_ucor=<value>`.
- Emits `off_ucor=` when unavailable.

Role:
- Reports offline uncorrectable sector/error count for ATA/SATA devices.
