# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_type

Symlink to `smart`; behavior is selected by invoked basename `test_type`.

Behavior:
- Parses latest SMART self-test type from `# 1` log entries.
- Lowercases and joins the type fields with an underscore.
- Prints `test_type=<type>` or `test_type=`.

Role:
- Reports the latest SMART self-test type, such as short or extended/long variants.
