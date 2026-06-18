# sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/pstore_crash_test

Purpose: destructive pstore phase that prepares state, then intentionally crashes the kernel so post-reboot tests can inspect persisted records.

Important APIs and functions: sources `common_tests`, writes `/proc/sys/kernel/sysrq` and `/proc/sys/kernel/panic`, moves `uuid` to `prev_uuid`, touches `reboot_flag`, syncs, then writes `c` to `/proc/sysrq-trigger`.

Control flow: after common backend checks, log intent, enable sysrq, configure panic reboot delay, preserve UUID, mark reboot expected, sync filesystems, and trigger crash.

State and persistence: writes `prev_uuid` and `reboot_flag` in the pstore test directory; relies on pstore backend preserving dmesg, console, and pmsg data across reboot.

Dependencies and integration: requires root, sysrq crash support, panic reboot, and a real pstore backend. It is invoked manually via `make run_crash`.

Risks and test signals: intentionally panics the system. Should only run on disposable or prepared hosts. Failure before crash prevents post-reboot phase from knowing a crash occurred.
