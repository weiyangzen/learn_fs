# sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/pstore_tests

Purpose: pre-crash pstore validation that console and pmsg support are available and a unique pmsg string can be written for later recovery.

Important APIs and functions: sources `common_tests`, uses `dmesg | grep`, tests `/dev/pmsg0`, writes to `/dev/pmsg0`, and writes `uuid`.

Control flow: verify pstore console registration in dmesg, verify `/dev/pmsg0` exists, write `Testing pstore: uuid=<UUID>` to the pmsg device, record the UUID in the test directory, and exit accumulated result code.

State and persistence: creates `uuid` for `pstore_crash_test` to rename. Writes pmsg content intended to survive crash.

Dependencies and integration: requires pstore backend, pstore console, and pmsg device support.

Risks and test signals: dmesg pattern matching is broad but still format-sensitive. Failure means post-reboot pmsg validation cannot be meaningful.
