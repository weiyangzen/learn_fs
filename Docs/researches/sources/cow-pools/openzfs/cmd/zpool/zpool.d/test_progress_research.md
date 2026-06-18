# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_progress

Symlink to `smart`; behavior is selected by invoked basename `test_progress`.

Behavior:
- Parses self-test progress from SAS execution status or SATA self-test log.
- Converts SATA percent remaining to percent done.
- Prints `test_progress=<percent/status>` or `test_progress=`.

Role:
- Reports progress of the current or latest SMART self-test.
