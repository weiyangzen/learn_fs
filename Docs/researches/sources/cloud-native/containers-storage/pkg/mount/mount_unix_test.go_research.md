# sources/cloud-native/containers-storage/pkg/mount/mount_unix_test.go

Purpose: tests Linux mount option parsing and basic mount/unmount integration.

Important APIs, types, and functions: `TestMountOptionsParsing`, `TestMounted`, `TestMountReadonly`, `TestGetMounts`, and `TestMergeTmpfsOptions`.

Control flow: root-only tests create temp source/target directories, bind mount them, check `Mounted`, verify read-only behavior by attempting an RW open, and unmount in defers. Non-root environments skip privileged mount tests.

State and persistence: temporarily mutates the host mount table and filesystem under temp directories; cleanup depends on deferred unmounts and directory removal.

Dependencies and integration points: depends on `os`, `path`, `slices`, `testing`, and `testify/require`. It validates mount parsing and Linux kernel mount integration.

Risks and edge cases: requires root. Defers call `t.Fatal` in cleanup, which can obscure prior failures. Tests do not cover recursive unmount.

Test signals: confirms parser flags/data, `Mounted`/`GetMounts`, bind mount success, read-only bind enforcement, and tmpfs option collision/error handling.
