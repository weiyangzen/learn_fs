# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/smart_test

Symlink to `smart`; behavior is selected by invoked basename `smart_test`.

Behavior:
- Parses SMART self-test log/status information.
- Reports four fields: `test_type`, `test_status`, `test_progress`, and `test_ended`.
- Converts SATA percent remaining into percent done.
- Computes rough elapsed time since test end when power-on hours are available.
- Emits empty fields for unavailable values.

Role:
- Provides a compact SMART self-test summary custom column group.
