# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/config

Purpose: kselftest config fragment requiring procfs support.

Important APIs/types/functions: contains `CONFIG_PROC_FS=y`.

Control flow: none.

State and persistence behavior: no runtime state.

Dependencies and integration points: applies to the proc selftest directory.

Risks and test signals: without procfs enabled, all researched proc tests are invalid or skipped by environment rather than by this one-line file.
