# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/pend_sec

Symlink to `smart`; behavior is selected by invoked basename `pend_sec`.

Behavior:
- Parses ATA/SATA SMART attributes.
- Extracts `Current_Pending_Sector` raw value into `pend_sec=<value>`.
- Emits `pend_sec=` when unavailable.

Role:
- Reports pending sector count for ATA/SATA devices.
