# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_ended

Symlink to `smart`; behavior is selected by invoked basename `test_ended`.

Behavior:
- Parses latest SMART self-test entry.
- Uses current power-on hours and test lifetime hour to estimate how long ago the test ended.
- Formats days/hours as a compact string such as `1d2h`.
- Prints `test_ended=<age>` or `test_ended=`.

Role:
- Reports approximate completion age of the most recent SMART self-test.
