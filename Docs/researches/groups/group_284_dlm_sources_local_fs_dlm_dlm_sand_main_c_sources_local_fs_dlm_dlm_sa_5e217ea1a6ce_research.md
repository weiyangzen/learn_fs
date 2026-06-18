# Group Research: group_284_dlm_sources_local_fs_dlm_dlm_sand_main_c_sources_local_fs_dlm_dlm_sa_5e217ea1a6ce

Scope verified against `Docs/research_subset_a.md`. All 21 listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_sand/main.c -->
# File Research: sources/local-fs/dlm/dlm_sand/main.c

## Purpose
Implements `dlm_sand`, an experimental DLM/GFS2 event-log coordinator backed by shared storage and sanlock. It initializes/dumps an events LV, watches DLM kernel uevents for lockspace online/offline transitions, coordinates cluster membership changes through an on-disk log, and drives kernel DLM configfs/sysfs start/stop actions.

## Main Responsibilities
- Provides `dlm_sand init /dev/vg/lv_events` to format a 512 MiB events LV with header, node, summary, record, and sanlock lease areas.
- Provides `dlm_sand dump /dev/vg/lv_events` to inspect the event header, node table, summary, and event records.
- Runs a daemon that listens for kernel DLM uevents and client commands over abstract UNIX sockets.
- Tracks per-GFS2/DLM lockspaces derived from `vg-lv` names and per-VG sanlock lockspaces named `lvm_<vg>`.
- Maintains membership recovery using on-disk records: `EV_JOIN`, `EV_LEAVE`, `EV_FAILED`, `EV_FENCED`, `EV_STOPPED`, `EV_STARTED`.
- Uses sanlock host state as the source of failed/fenced generation changes.
- Exposes status, config, and debug dumps for `dlm_tool`.

## Key Flows
- Startup reads CLI/config defaults, determines local node id from `/etc/lvm/lvmlocal.conf` or `dlm.conf`, validates `local_ipaddr`, daemonizes unless foreground/debug, locks `/run/dlm_sand.pid`, initializes configfs/local node, starts query sockets, and polls uevents.
- Online uevent creates a `lockspace`, finds/adds its VG sanlock lockspace, records local generation, starts a `lockspace_thread`.
- `lockspace_thread` opens the events LV, validates the header, initializes node metadata, finds the end of the log from the summary record, waits for a safe join point, writes a join, starts the kernel lockspace, and then continually processes log records and sanlock failure state.
- Offline uevent sets `ls->leave`, waits for the lockspace thread to write leave/stop records, tears down configfs state, closes descriptors, and drops unused VG state.
- Query thread serializes status/debug/config responses with `query_mutex` so `copy_status()` can inspect shared lists safely.

## Important Data/Interfaces
- Depends on `sand_internal.h` structures such as `lockspace`, `current_event`, `dlm_node`, and `vg_lockspace`.
- Uses `ondisk.c` helpers for little-endian header/node/summary/record serialization.
- Uses sanlock APIs: `sanlock_inq_lockspace`, `sanlock_get_hosts`, `sanlock_acquire`, `sanlock_release`, `sanlock_read_resource`, `sanlock_direct_write_resource`.
- Uses action/config helpers declared in `sand_internal.h` for configfs/sysfs work.
- Uses abstract UNIX sockets from `dlm_sand_sock.h`.

## Notable Implementation Details
- The event log is circular; record number modulo `record_count` chooses the physical record index, while `wraps` tracks wraps.
- `last_all_started_rn` summary is an optimization so joining nodes do not scan from the beginning.
- Joining is deliberately restricted to stable points: after all-started, after last-leave, after compatible join, or after log reset if old members are dead/free.
- Failure handling writes failed/fenced records only after filtering notices already seen from other nodes.
- `cur_event_status` mirrors the active recovery state for `dlm_tool status`.

## Risks / Gaps
- Several error branches contain empty blocks after failed allocation/read/write calls, so some failures are logged weakly or continue unsafely.
- `client_alloc()` may leak the old `client` array if `realloc(client)` succeeds and `realloc(pollfd)` fails.
- Many fixed-size string copies assume prior length constraints; most are bounded by naming rules, but enforcement is uneven.
- `process_uevent()` frees `vg` directly in one error path even when `get_add_vg_lockspace()` may have linked or initialized state; this path needs careful audit.
- The daemon ignores shutdown while active lockspaces exist, which is intentional, but operationally means service stop can hang until unmount/offline completes.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_sand/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_sand/ondisk.c -->
# File Research: sources/local-fs/dlm/dlm_sand/ondisk.c

## Purpose
Provides serialization/deserialization helpers for the `dlm_sand` on-disk events format.

## Contents
- `header_copy_out()` / `header_copy_in()` copy event-log header strings and convert all numeric fields between CPU and little-endian format.
- `node_copy_out()` / `node_copy_in()` copy node id, generation, address, node UUID, and boot id.
- `summary_copy_out()` / `summary_copy_in()` serialize `last_all_started_rn`.
- `record_copy_out()` / `record_copy_in()` serialize event records, leaving CRC generation to `record_crc_out()` in `main.c`.

## Dependencies
- Uses structures and constants from `sand_internal.h`.
- Uses byte-order macros from `ondisk.h`.

## Risks / Gaps
- `node_copy_in()` uses `cpu_to_le16()` and `cpu_to_le64()` instead of `le16_to_cpu()` and `le64_to_cpu()`. This is harmless on little-endian systems but wrong for big-endian portability.
- CRC is intentionally not calculated here; callers must remember to call `record_crc_out()` after `record_copy_out()`.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_sand/ondisk.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_sand/ondisk.h -->
# File Research: sources/local-fs/dlm/dlm_sand/ondisk.h

## Purpose
Declares the `dlm_sand` on-disk serialization helpers and defines little-endian conversion macros for big- and little-endian hosts.

## Contents
- Includes `<endian.h>` and `<byteswap.h>`.
- Defines `le16_to_cpu`, `le32_to_cpu`, `le64_to_cpu`, `cpu_to_le16`, `cpu_to_le32`, and `cpu_to_le64`.
- Declares header, node, summary, and record copy-in/copy-out functions.

## Dependencies
- Requires struct definitions from `sand_internal.h` before use.

## Risks / Gaps
- No fallback for unknown `__BYTE_ORDER` values.
- Header depends on external struct declarations but does not include `sand_internal.h` itself, so include ordering matters.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_sand/ondisk.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_sand/sand_internal.h -->
# File Research: sources/local-fs/dlm/dlm_sand/sand_internal.h

## Purpose
Central internal header for `dlm_sand`, defining daemon globals, configuration options, on-disk layout constants, cluster state structures, and cross-file function prototypes.

## Key Definitions
- Configuration paths: `/etc/dlm/dlm.conf`, `/run/dlm_sand.pid`, `/var/log/dlm_sand.log`.
- Option indexes for daemon/debug/fencing/protocol/port/mark/local node and IP settings.
- Event LV layout: 512 MiB total, fixed offsets for config, nodes, summary, records, and lock-manager data.
- Maximum node model: 2000 active node ids with 2048-sized aligned arrays and 256-byte nodeid bitmaps.
- On-disk structures: `dlm_events_header`, `dlm_events_summary`, `dlm_events_node`, `log_record`.
- Runtime structures: `current_event`, `vg_lockspace`, `vg_node`, `dlm_node`, `rd_sanlock`, `lockspace`.

## Interfaces Declared
- Kernel/configfs actions from `action.c`.
- Config loading and online setting from `config.c`.
- Main-loop helpers from `main.c`.
- Logging functions from `log.c`.

## Notable Design
- Uses the `EXTERN` macro pattern so `main.c` can define globals and other C files can declare them.
- Separates VG-level sanlock host tracking from DLM lockspace-level event processing.
- Stores per-lockspace recovery state in fixed arrays indexed by `nodeid - 1`.

## Risks / Gaps
- Fixed-size arrays for 2000 nodes are simple but large; each `lockspace` carries multiple 2048-byte and 2000-entry generation arrays.
- `struct log_record` relies on exact layout comments and CRC length assumptions; future field changes require careful compatibility work.
- Includes many system and project headers globally, increasing coupling across the `dlm_sand` implementation.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_sand/sand_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_tool/Makefile -->
# File Research: sources/local-fs/dlm/dlm_tool/Makefile

## Purpose
Builds and installs the `dlm_tool` administrative CLI and its man page.

## Build Behavior
- Compiles `main.c` into `dlm_tool`.
- Uses hardening flags: PIE, RELRO, immediate binding, stack protector, fortify, stack clash protection.
- Includes headers from `../include`, `../libdlm`, `../dlm_controld`, and `../dlm_sand`.
- Links against `libdlm`, `libdlmcontrol`, and pthreads.
- Installs binary to `$(PREFIX)/sbin` and `dlm_tool.8` to man8.

## Notes
- The Makefile assumes local build products for `libdlm` and `libdlmcontrol` via `-L../libdlm -L../dlm_controld`.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_tool/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_tool/main.c -->
# File Research: sources/local-fs/dlm/dlm_tool/main.c

## Purpose
Implements `dlm_tool`, the main administrative CLI for DLM lockspaces, daemon status/config/debug dumps, plocks, fencing acknowledgements, run commands, and kernel debugfs lock inspection.

## Command Areas
- Direct libdlm operations: `join`, `leave`, `joinleave`.
- Daemon operations through `dlm_controld`: `ls`, `status`, `dump`, `dump_config`, `reload_config`, `set_config`, `plocks`, `log_plock`, `fence_ack`, `run*`.
- `dlm_sand` fallback for status/debug/config query dumps where supported.
- Debugfs operations: `lockdump`, `lockdebug`.

## Key Logic
- `decode_arguments()` parses command, options, optional lockspace name, run UUID, or command payload.
- `_daemon_connect()` first tries `dlm_controld` sockets, then `dlm_sand` sockets when the command supports both.
- `_dlms_dump()` speaks the `dlm_sand` query protocol using `dlm_sd_header`.
- `_dlmc_*()` wrappers use `libdlmcontrol` APIs.
- `do_lockdebug()` parses modern and older debugfs formats, printing resources, locks, LVBs, toss entries, waiters, and optional summaries.
- `do_join()` and `do_leave()` call `dlm_new_lockspace()` / `dlm_release_lockspace()`.

## Dependencies
- `libdlm.h` for kernel lockspace creation/removal.
- `libdlmcontrol.h` and `dlm_controld.h` for daemon-control APIs.
- `dlm_sand_sock.h` for fallback query/control socket constants and headers.
- Kernel debugfs files under `/sys/kernel/debug/dlm`.

## Risks / Gaps
- Fixed `MAX_NODES` is 128 for `dlm_controld` node display, smaller than `dlm_sand`’s 2000-node model.
- `run_command` is built by repeated `strcat()` after length checks; acceptable but brittle.
- Some debugfs parsers are tightly coupled to text formats and fail noisily if kernel output changes.
- `daemon_reload_config()` and `daemon_set_config()` do nothing for `dlm_sand`; only query dumps are supported by this CLI path.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_tool/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/fence/Makefile -->
# File Research: sources/local-fs/dlm/fence/Makefile

## Purpose
Builds and installs `dlm_stonith`, a Pacemaker-backed fencing helper.

## Build Behavior
- Compiles `stonith_helper.c`.
- Uses hardening flags similar to other DLM user tools.
- Uses `pkg-config --cflags pacemaker-fencing` and errors out if Pacemaker fencing headers are unavailable.
- Links with `-ldl`.
- Installs binary to `$(PREFIX)/sbin` and `dlm_stonith.8` to man8.

## Notes
- The link line relies on Pacemaker fencing symbols being provided through included build/link environment or dynamic loading semantics; the Makefile only explicitly adds `-ldl`.
<!-- END FILE RESEARCH: sources/local-fs/dlm/fence/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/fence/stonith_helper.c -->
# File Research: sources/local-fs/dlm/fence/stonith_helper.c

## Purpose
Small helper that asks Pacemaker/STONITH to fence a failed DLM node.

## Behavior
- Accepts `-n <nodeid>` and `-t <fail_time>` from argv, or reads `node=<id>` and `fail_time=<time>` key/value pairs from stdin.
- Requires a nonzero node id.
- If `fail_time` is supplied, calls `stonith_api_time_helper(nodeid, 0)` and exits successfully if the node has already been fenced at or after that time.
- Otherwise calls `stonith_api_kick_helper(nodeid, 300, 0)` with a 300-second timeout.
- Logs fencing failures to stderr and syslog under `dlm_stonith`.

## Dependencies
- Pacemaker `crm/stonith-ng.h`.

## Risks / Gaps
- Minimal validation on input values.
- Global `nodeid` and `fail_time` are simple process-wide state; fine for this one-shot helper.
<!-- END FILE RESEARCH: sources/local-fs/dlm/fence/stonith_helper.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/init/dlm.service -->
# File Research: sources/local-fs/dlm/init/dlm.service

## Purpose
Systemd unit for the standard `dlm_controld` daemon.

## Behavior
- Requires and starts after `corosync.service` and `sys-kernel-config.mount`.
- Loads the `dlm` kernel module before daemon start.
- Uses `/etc/sysconfig/dlm` for `DLM_CONTROLD_OPTS`.
- Runs `/usr/sbin/dlm_controld --foreground`.
- Uses `Type=notify` and `NotifyAccess=main`.
- Sets `OOMScoreAdjust=-1000`.
- Disables `SendSIGKILL` to avoid killing an active daemon with lockspaces, which could cause fencing.

## Notes
- This unit is for `dlm_controld`, not `dlm_sand`.
<!-- END FILE RESEARCH: sources/local-fs/dlm/init/dlm.service -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/libdlm/51-dlm.rules -->
# File Research: sources/local-fs/dlm/libdlm/51-dlm.rules

## Purpose
udev rules for DLM misc devices.

## Rules
- Creates `/dev/misc/dlm-control` and `/dev/misc/dlm-monitor` with mode `0666`.
- Creates `/dev/misc/dlm_plock` with mode `0666`.
- Creates symlinks for `dlm_*` devices under `/dev/misc/%k` with mode `0660`.

## Notes
- These rules are required by `libdlm.c`, which waits for `/dev/misc/dlm-control` and per-lockspace `/dev/misc/dlm_<lockspace>` paths.
<!-- END FILE RESEARCH: sources/local-fs/dlm/libdlm/51-dlm.rules -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/libdlm/Makefile -->
# File Research: sources/local-fs/dlm/libdlm/Makefile

## Purpose
Builds threaded and non-threaded DLM user libraries, pkg-config files, public headers, man pages, and udev rules.

## Build Products
- `libdlm.so.3.0` from `libdlm.c` with `_REENTRANT` and pthread support.
- `libdlm_lt.so.3.0` from the same source without `_REENTRANT`.
- `libdlm.pc` and `libdlm_lt.pc`.
- Public header `libdlm.h`.
- Man pages for lockspace, lock/unlock, dispatch, pthread, cleanup APIs.
- udev rules `51-dlm.rules`.

## Build Details
- Uses PIC and common hardening flags.
- Threaded library links with `-lpthread`; both use `-Wl,-z,now`.
- Installs symlinks for soname and unversioned shared library names.

## Risks / Gaps
- `LIBNUM=/lib64` is a platform assumption unless overridden.
- pkg-config files are generated with `cat | sed`, which is simple but less portable than install-time substitution tooling.
<!-- END FILE RESEARCH: sources/local-fs/dlm/libdlm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/libdlm/libdlm.c -->
# File Research: sources/local-fs/dlm/libdlm/libdlm.c

## Purpose
Implements the user-space `libdlm` API over the Linux kernel DLM misc-device ABI.

## Main Responsibilities
- Open/create/release DLM lockspaces via `/dev/misc/dlm-control`.
- Open per-lockspace misc devices under `/dev/misc/dlm_<name>`.
- Encode lock/unlock/purge/deadlock requests into kernel ABI write requests.
- Read AST/BAST completion records from the lockspace fd and invoke user callbacks.
- Provide synchronous wrappers using `LKF_WAIT`.
- Provide optional pthread receiver threads for asynchronous callbacks.

## ABI Handling
- Supports kernel DLM device ABI v5 through local `dlm_write_request_v5` and result structs.
- Supports v6+ through kernel `struct dlm_write_request` and `struct dlm_lock_result`.
- Detects kernel ABI version by reading `dlm-control`; falls back to version 5 if read fails.
- Marks request architecture width through `is64bit`.

## Key APIs Implemented
- Default lockspace: `dlm_lock`, `dlm_unlock`, `dlm_lock_wait`, `dlm_unlock_wait`, `dlm_get_fd`, `dlm_dispatch`.
- Named lockspaces: `dlm_create_lockspace`, `dlm_new_lockspace`, `dlm_open_lockspace`, `dlm_close_lockspace`, `dlm_release_lockspace`, `dlm_ls_get_fd`.
- Named lockspace locking: `dlm_ls_lock`, `dlm_ls_lockx`, `dlm_ls_lock_wait`, `dlm_ls_unlock`, `dlm_ls_unlock_wait`.
- Maintenance: `dlm_ls_deadlock_cancel`, `dlm_ls_purge`, version queries.
- Threaded-only helpers: `lock_resource`, `unlock_resource`, `dlm_pthread_init`, `dlm_ls_pthread_init`, `dlm_pthread_cleanup`.

## Notable Design
- `default_ls` is global and intentionally not heavily synchronized; callers are expected to coordinate.
- Synchronous writes either block on a condition variable or, when already in the AST thread, dispatch completions until `sb_status` changes.
- Lockspace creation waits for udev to create the device and handles truncated sysfs names by adding a symlink.
- `dlm_release_lockspace()` closes/cancels pthread handling before asking the kernel to remove the lockspace.

## Risks / Gaps
- Range locks are explicitly unsupported and return `ENOSYS`.
- `timeout` passed to `dlm_ls_lockx()` is accepted in the API but not copied into the v6 request in this implementation.
- Some pthread condition waits are not wrapped in predicate loops, so spurious wakeups are theoretically possible.
- Global `control_fd`, `default_ls`, and version state are not fully thread-safe.
<!-- END FILE RESEARCH: sources/local-fs/dlm/libdlm/libdlm.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/libdlm/libdlm.h -->
# File Research: sources/local-fs/dlm/libdlm/libdlm.h

## Purpose
Public C API header for `libdlm`.

## Contents
- Replicates minimal kernel-compatible user structs/constants when not building the library, so applications do not need kernel DLM headers.
- Declares library/kernel version functions.
- Declares default lockspace lock/unlock APIs.
- Declares fd dispatch APIs for callers that poll their own fds.
- Declares lockspace lifecycle APIs.
- Declares named-lockspace lock/unlock/deadlock/purge APIs.
- Declares pthread receiver APIs under `_REENTRANT`.
- Defines DLM lock modes, lock flags, lock status block flags, and extra return codes.

## Important Constants
- `DLM_LVB_LEN` is 32.
- User-facing `DLM_LOCKSPACE_LEN` and `DLM_RESNAME_MAXLEN` are 64 when not building libdlm.
- `LKF_WAIT` is userspace-only and used to request synchronous behavior.

## Notes
- `dlm_lshandle_t` is an opaque `void *`.
- Public comments document unused parameters such as parent/range in several APIs.
<!-- END FILE RESEARCH: sources/local-fs/dlm/libdlm/libdlm.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/libdlm/libdlm.pc.in -->
# File Research: sources/local-fs/dlm/libdlm/libdlm.pc.in

## Purpose
pkg-config template for the threaded `libdlm`.

## Contents
- Substitutes `@PREFIX@` and `@LIBDIR@`.
- Exposes include path `${prefix}/include`.
- Names package `libdlm`, version `4.0.0`.
- Links with `-ldlm -lpthread`.

## Notes
- Version here is package/API metadata and does not match the Makefile soname major/minor directly.
<!-- END FILE RESEARCH: sources/local-fs/dlm/libdlm/libdlm.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/libdlm/libdlm_internal.h -->
# File Research: sources/local-fs/dlm/libdlm/libdlm_internal.h

## Purpose
Internal compatibility header for building libdlm with kernel-style DLM headers.

## Contents
- Defines `__user`.
- Typedefs `__u8`, `__u16`, and `__u32`.
- Defines `BUILDING_LIBDLM`.

## Notes
- This avoids depending on kernel annotation/type definitions in contexts where only user-space fixed-width integer types are available.
<!-- END FILE RESEARCH: sources/local-fs/dlm/libdlm/libdlm_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/libdlm/libdlm_lt.pc.in -->
# File Research: sources/local-fs/dlm/libdlm/libdlm_lt.pc.in

## Purpose
pkg-config template for the non-threaded `libdlm_lt`.

## Contents
- Substitutes `@PREFIX@` and `@LIBDIR@`.
- Names package `libdlm_lt`, version `4.0.0`.
- Links with `-ldlm_lt` and does not include pthreads.

## Notes
- Used by the Python ctypes wrapper in this group.
<!-- END FILE RESEARCH: sources/local-fs/dlm/libdlm/libdlm_lt.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/python/bindings/__init__.py -->
# File Research: sources/local-fs/dlm/python/bindings/__init__.py

## Purpose
Empty Python package initializer for `python/bindings`.

## Contents
- File is zero bytes.

## Notes
- Provides package recognition only; all binding logic is in `dlm.py`.
<!-- END FILE RESEARCH: sources/local-fs/dlm/python/bindings/__init__.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/python/bindings/dlm.py -->
# File Research: sources/local-fs/dlm/python/bindings/dlm.py

## Purpose
Python ctypes wrapper around `libdlm_lt`.

## Behavior
- Exits on non-Linux platforms.
- Locates `dlm_lt` with `ctypes.util.find_library`.
- Loads the library with `ctypes.CDLL`.
- Defines ctypes representations for lockspace handles and `struct dlm_lksb`.
- Binds `dlm_create_lockspace`, `dlm_release_lockspace`, `dlm_ls_lock_wait`, and `dlm_ls_unlock_wait`.
- Defines Python enums for lock modes, lock flags, and lock status block flags.
- Provides `Lockspace` class and nested per-resource `Lock` objects.

## API Model
- `Lockspace(name="default", mode=0o600)` creates a kernel DLM lockspace.
- `release(force=2)` releases it.
- `create_lock(name)` returns a lock object.
- `Lock.lock_wait()` synchronously locks; default mode is exclusive.
- `Lock.unlock_wait()` synchronously unlocks.
- Destructors attempt cleanup of held locks and lockspaces.

## Risks / Gaps
- Constructor maps a null handle to `ENOMEM`, losing the real C `errno`.
- Callback objects for BAST are local variables; if the C layer retains them beyond the synchronous call, lifetime may be unsafe.
- `C_DLM_LKSB.sb_flags` is `ctypes.c_char`; `LockSBFlag(flags[0])` depends on bytes indexing semantics.
- Destructor cleanup can raise through `release()`/`unlock_wait()` during garbage collection.
<!-- END FILE RESEARCH: sources/local-fs/dlm/python/bindings/dlm.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/python/ebpf/dlmhist.py -->
# File Research: sources/local-fs/dlm/python/ebpf/dlmhist.py

## Purpose
BCC/eBPF tracing script that measures DLM exclusive noqueue lock latency from kernel `dlm_lock_start` to successful AST completion.

## Behavior
- Attaches tracepoint probes to `dlm:dlm_lock_start`, `dlm:dlm_lock_end`, and `dlm:dlm_ast`.
- Tracks start timestamps in a BPF hash keyed by `ls_id ^ lkb_id`.
- Only records `DLM_LKF_NOQUEUE` and `DLM_LOCK_EX` starts.
- Deletes starts on lock-end errors.
- On AST with successful `sb_status`, records log2 nanosecond latency histogram.
- Waits until Ctrl-C, then prints the histogram.

## Dependencies
- Python BCC package.
- Kernel DLM tracepoints and DLM UAPI headers.

## Risks / Gaps
- Hash key is simple XOR and can collide.
- Script cannot distinguish local-master latency from remote/network latency; comment notes expected two peaks.
<!-- END FILE RESEARCH: sources/local-fs/dlm/python/ebpf/dlmhist.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/python/tests/dlm.py -->
# File Research: sources/local-fs/dlm/python/tests/dlm.py

## Purpose
Duplicate copy of the Python ctypes DLM wrapper found at `python/bindings/dlm.py`.

## Contents
- File content matches `sources/local-fs/dlm/python/bindings/dlm.py` byte-for-byte in this checkout.
- Provides the same `LockMode`, `LockFlag`, `LockSBFlag`, `DLMError`, `Lockspace`, and nested `Lock` APIs.

## Notes
- Because this is under `python/tests`, it is likely vendored locally so test scripts can import `dlm` without package installation.

## Risks / Gaps
- Same risks as the binding file: errno loss on create failure, callback lifetime concerns, destructor exceptions, and `c_char` flag handling.
- Duplication means fixes to bindings must be mirrored here unless tests are changed to import the package copy.
<!-- END FILE RESEARCH: sources/local-fs/dlm/python/tests/dlm.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/python/tests/recovery_interrupt -->
# File Research: sources/local-fs/dlm/python/tests/recovery_interrupt

## Purpose
Python test/stress script that repeatedly creates and destroys a DLM lockspace, optionally doing lock activity, until interrupted.

## Behavior
- Imports `Lockspace` from `dlm`.
- Handles SIGINT by setting a global `end` flag.
- Options:
  - `--lock` / `-l` to lock/unlock resource `fooobaar` each cycle.
  - `--wait` / `-w` to sleep while holding the lock.
  - `--debug` / `-d` for logging level.
- Loop creates a default lockspace, optionally creates and locks a resource, sleeps, unlocks, deletes lock, deletes lockspace, and logs each step.

## Dependencies
- Relies on local/importable `dlm.py` wrapper and working `libdlm_lt`/kernel DLM environment.

## Risks / Gaps
- Uses destructor side effects for cleanup via `del`, which depends on CPython reference counting behavior.
- No exception handling inside the loop, so a DLM operation failure aborts the test.
<!-- END FILE RESEARCH: sources/local-fs/dlm/python/tests/recovery_interrupt -->