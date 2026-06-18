# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fclog.c

## Purpose

`fclog.c` tests the read side of new mount API filesystem context logs, especially empty-log, error-log, post-creation retention, and too-small-buffer behavior.

## Important APIs, Types, and Functions

The `ns` fixture saves the original mount namespace, unshares a private mount namespace, and restores it during teardown. Assertion macros compare syscall return values to negative errno. Tests call `fsopen`, `fsconfig`, `fsmount`, `move_mount`, `read`, `close`, `unshare`, `mount`, and `setns`.

## Control Flow, State, and Persistence

Each test opens a tmpfs filesystem context. `fscontext_log_enodata` repeatedly reads a fresh context and expects `ENODATA`. `fscontext_log_errorfc` submits an invalid option and expects one exact tmpfs error line, then `ENODATA` after consumption. `fscontext_log_errorfc_after_fsmount` verifies the same log remains readable after `FSCONFIG_CMD_CREATE`, `fsmount`, and attaching the mount to `/tmp`. `fscontext_log_emsgsize` verifies zero-, one-, and sixteen-byte reads fail with `EMSGSIZE` without consuming the message. State is the fscontext log queue and temporary mount namespace.

## Dependencies, Integration Points, Risks, and Test Signals

The file depends on new mount API syscalls, tmpfs option parsing, mount namespace capability, and kselftest harness support. It integrates with VFS fs_context diagnostics. Risks are exact error string drift, namespace restore failures, and attaching to `/tmp` in an isolated namespace. Passing signals are stable `ENODATA`, `EINVAL`, `EMSGSIZE`, exact error text, and non-consumption on short reads.
