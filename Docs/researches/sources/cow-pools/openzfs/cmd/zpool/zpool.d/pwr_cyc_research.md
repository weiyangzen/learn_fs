# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/pwr_cyc

Symlink to `smart`; behavior is selected by invoked basename `pwr_cyc`.

Behavior:
- Parses SATA `Power_Cycle_Count` or NVMe `Power Cycles`.
- Prints `pwr_cyc=<count>` or `pwr_cyc=`.

Role:
- Reports drive power cycle count.
