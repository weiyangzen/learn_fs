# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-wchan.c

Purpose: verifies that reading `/proc/self/wchan` for the running task reports `0`.

Important APIs and functions: uses `open`, `read`, and skip-on-ENOENT behavior.

Control flow: open `/proc/self/wchan`, read exactly one byte into a small buffer, and require it to be ASCII `0`.

State and persistence: none.

Dependencies and integration: depends on `/proc/self/wchan` being enabled. Missing file returns kselftest skip 4.

Risks and test signals: exact single-byte expectation is format-sensitive. Failure means the current running userspace task is being attributed a wait channel incorrectly or the proc format changed.
