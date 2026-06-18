# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/r_ucor

Symlink to `smart`; behavior is selected by invoked basename `r_ucor`.

Behavior:
- Parses SAS `read:` SMART statistics.
- Extracts read uncorrectable errors into `r_ucor=<count>`.
- Emits `r_ucor=` when unavailable.

Role:
- Reports SAS read uncorrectable error count.
