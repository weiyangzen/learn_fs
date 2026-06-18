# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/w_proc

Symlink to `smart`; behavior is selected by invoked basename `w_proc`.

Behavior:
- Parses SAS `write:` SMART statistics.
- Extracts lifetime write gigabytes processed into `w_proc=<value>`.
- Emits `w_proc=` when unavailable.

Role:
- Reports SAS write data processed over drive lifetime.
