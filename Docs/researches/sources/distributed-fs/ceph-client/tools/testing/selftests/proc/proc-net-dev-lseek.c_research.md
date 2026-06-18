# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-net-dev-lseek.c

Purpose: regression test that `/proc/net/dev` implements `lseek(fd, 0, SEEK_SET)` correctly and can be reread identically after rewind.

Important APIs and functions: uses `unshare(CLONE_NEWNET)` for deterministic network namespace contents, then `open`, `read`, `lseek`, `memcmp`, and assertions.

Control flow: create a fresh net namespace, read `/proc/net/dev` into `buf1`, seek to offset zero, reread into `buf2`, and assert both size and contents match.

State and persistence: transient network namespace only. No files are created.

Dependencies and integration: requires network namespace permission. `ENOSYS` and `EPERM` return skip code 4. It relies on loopback-only output being stable enough in a fresh netns.

Risks and test signals: does not validate field content, only seek semantics. A failure indicates proc net device seq-file rewind regression or nondeterministic content in the isolated namespace.
