# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_status

Symlink to `smart`; behavior is selected by invoked basename `test_status`.

Behavior:
- Parses latest SMART self-test status.
- Normalizes lowercase strings and selected multi-word failure statuses with underscores.
- Maps a parsed `self` status to `running`.
- Prints `test_status=<status>` or `test_status=`.

Role:
- Reports status of the latest SMART self-test.
