# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/nonmed

Symlink to `smart`; behavior is selected by invoked basename `nonmed`.

Behavior:
- Parses SAS SMART output.
- Extracts `Non-medium error count` into `nonmed=<count>`.
- Emits `nonmed=` when missing.

Role:
- Reports SAS non-medium error count.
