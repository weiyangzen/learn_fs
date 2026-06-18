# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/r_proc

Symlink to `smart`; behavior is selected by invoked basename `r_proc`.

Behavior:
- Parses SAS `read:` SMART statistics.
- Extracts lifetime read gigabytes processed into `r_proc=<value>`.
- Emits `r_proc=` when unavailable.

Role:
- Reports SAS read data processed over drive lifetime.
