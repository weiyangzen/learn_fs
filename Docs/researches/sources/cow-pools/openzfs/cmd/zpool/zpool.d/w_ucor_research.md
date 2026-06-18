# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/w_ucor

Symlink to `smart`; behavior is selected by invoked basename `w_ucor`.

Behavior:
- Parses SAS `write:` SMART statistics.
- Extracts write uncorrectable errors into `w_ucor=<count>`.
- Emits `w_ucor=` when unavailable.

Role:
- Reports SAS write uncorrectable error count.
