# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/realloc

Symlink to `smart`; behavior is selected by invoked basename `realloc`.

Behavior:
- Parses ATA/SATA `Reallocated_Sector_Ct`.
- Prints `realloc=<raw count>` or `realloc=`.

Role:
- Reports reallocated sector count for ATA/SATA devices.
