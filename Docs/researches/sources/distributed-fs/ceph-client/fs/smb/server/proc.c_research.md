# sources/distributed-fs/ceph-client/fs/smb/server/proc.c

## Purpose
Implements procfs diagnostics and per-CPU counters for ksmbd. It creates `/proc/fs/ksmbd`, a `sessions` subdirectory, a `server` status file, and initializes/destroys/reset counters used by request processing and VFS I/O accounting.

## Important APIs, Types, and Functions
- Global `static struct proc_dir_entry *ksmbd_proc_fs` holds the procfs root.
- Global `struct ksmbd_counters ksmbd_counters` provides storage for percpu counters declared in `stats.h`.
- `ksmbd_proc_create()` wraps `proc_create_single_data()` under the ksmbd proc root.
- `smb2_process_req[]` maps SMB2 command numbers to display names for per-command counters.
- `proc_show_ksmbd_stats()` emits server identity/configuration, session/tree/read/write counters, and SMB2 per-command request counters through `seq_file`.
- `ksmbd_proc_init()` creates the proc root and `sessions` directory, initializes all percpu counters, creates the `server` file, and resets counters.
- `ksmbd_proc_cleanup()` removes the proc tree and destroys counters.
- `ksmbd_proc_reset()` sets all counters to zero.

## Control Flow
Module init calls `ksmbd_proc_init()` before server operation. If any proc or counter setup step fails, `ksmbd_proc_init()` jumps to cleanup. Request dispatch increments per-command counters through `ksmbd_counter_inc_reqs()`, session/tree code updates their counters, and VFS read/write paths add bytes. Reading `/proc/fs/ksmbd/server` calls `proc_show_ksmbd_stats()`. Module shutdown calls `ksmbd_proc_cleanup()`.

## State and Persistence
Proc entries and counters are runtime-only kernel state. Counters are per-CPU and reset at initialization and on server control reset via `ksmbd_proc_reset()`. No values persist across module unload or reset.

## Dependencies and Integration Points
This file depends on procfs, seq_file, Linux module headers, `server.h`, `stats.h`, `smb_common.h`, and `smb2pdu.h`. It reads `server_conf` and server identity helpers from `server.c`, protocol string helpers from SMB common code, and counter helpers from `stats.h`. Session-specific proc entries are created elsewhere under the `sessions` directory.

## Risks and Edge Cases
- If counter initialization fails partway through, `ksmbd_proc_cleanup()` destroys every counter slot, including any not successfully initialized; this depends on percpu counter destroy tolerating zero/uninitialized storage.
- `ksmbd_proc_reset()` assumes counters are initialized; calls before successful init would be unsafe.
- The command-name table must stay aligned with `KSMBD_COUNTER_MAX_REQS` and SMB2 command ordering.
- Proc output reads global configuration without explicit locking, so it is a diagnostic snapshot rather than a strongly consistent view.

## Test Signals
Build with procfs enabled; mount/read `/proc/fs/ksmbd/server`; verify counters increment for representative SMB2 commands and read/write byte paths; reset the server and confirm counters zero; exercise init failure injection for proc creation and percpu counter allocation; unload/reload under KASAN to detect proc/counter lifetime issues.
