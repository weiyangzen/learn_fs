# Research: sources/distributed-fs/ceph-client/drivers/tty/tty_audit.c

## Purpose

`tty_audit.c` records audited tty input for tasks whose `signal_struct` has tty auditing enabled. It batches input bytes into a per-signal audit buffer, emits `AUDIT_TTY` records with task and tty metadata, logs `TIOCSTI` injection separately, and flushes/free buffers on explicit push and task exit.

## Important APIs, Types, and Functions

`struct tty_audit_buf` stores a mutex, source `dev_t`, canonical-mode flag, valid byte count, and a 4096-byte data allocation. `tty_audit_add_data` is the main input ingestion API. `tty_audit_tiocsti` logs injected characters. `tty_audit_push` flushes the current task's buffer if tty audit is enabled. `tty_audit_exit` pushes and frees a task's buffer during signal teardown, and `tty_audit_fork` copies the audit enable flags to a new signal struct.

Internal helpers include `tty_audit_buf_ref`, `tty_audit_buf_alloc`, `tty_audit_buf_free`, `tty_audit_buf_get`, `tty_audit_buf_push`, and `tty_audit_log`.

## Control Flow

`tty_audit_add_data` first reads `current->signal->audit_tty`; if tty auditing is disabled, size is zero, the tty is a PTY master, or password-style canonical no-echo input should be hidden without `AUDIT_TTY_LOG_PASSWD`, it returns without logging. Otherwise it allocates or retrieves the current signal's buffer, locks it, flushes if the tty device or canonical mode changed, copies data in chunks until the 4096-byte buffer fills, and pushes whenever full.

`tty_audit_push` validates `AUDIT_TTY_ENABLE`, locks the existing buffer if present, and emits pending data. `tty_audit_tiocsti` computes the tty device number, pushes prior buffered data so ordering is preserved, and emits an `ioctl=TIOCSTI` audit record for the injected byte. `tty_audit_exit` atomically marks the signal buffer as exited with `ERR_PTR(-ESRCH)`, pushes final data, and frees the allocation.

## State and Persistence Behavior

Audit buffering is per `signal_struct` via `current->signal->tty_audit_buf`, so threads in the same thread group share the same buffer and mutex. Buffered data persists until full, pushed, device/mode changes, audit disabled, or task exit. Records are persisted only through the kernel audit subsystem; this file does not write storage directly.

## Dependencies and Integration Points

The code depends on the audit subsystem (`audit_log_start`, `audit_context`, `audit_log_n_hex`, `audit_enabled`, loginuid/session helpers), tty driver identity, task credentials, task command names, slab allocation, and the private tty header for declarations. It is compiled behind `CONFIG_AUDIT`; callers use no-op stubs from `tty.h` otherwise.

## Risks and Edge Cases

The shared per-signal buffer requires correct mutex use across multiple threads. `tty_audit_exit` uses an `ERR_PTR(-ESRCH)` sentinel; callers must tolerate that value and avoid dereferencing it. Out-of-memory drops audit data and calls `audit_log_lost`. Password filtering depends on canonical mode and echo state, so noncanonical sensitive input may still be logged if tty audit policy requests it. Audit-disabled transitions clear pending bytes without emission.

## Test Signals

Test coverage should include audit enabled/disabled tasks, fork inheritance of `audit_tty`, canonical echo and no-echo input, PTY master exclusion, buffer-full flushing at 4096 bytes, device/mode-change flushing, `TIOCSTI` ordering, out-of-memory/lost audit behavior, and exit-time flushing/freeing for single-threaded signal teardown.
