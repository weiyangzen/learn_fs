# Research: subset-b-009843

This grouped report covers Samba source files from `source3/printing`, `source3/profile`, and `source3/registry`. Each section preserves its source path and is delimited for reconciliation into one source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/printing.c -->
# sources/user-network-fs/samba/source3/printing/printing.c

## Purpose

`printing.c` is the main Samba source3 print backend implementation. It owns per-printer job records, queue cache refresh, spool job start/end/delete/pause/resume operations, queue pause/resume/purge operations, and notification emission for spoolss consumers. It bridges SMB/SPOOLSS-visible jobs to backend-specific print interfaces selected from `printing =` service configuration.

## Important APIs, Types, and Functions

- `print_backend_init()` creates the cache directory, initializes or wipes per-printer TDBs when `PRINT_DATABASE_VERSION` changes, closes cached DB handles, and calls `nt_printing_init()`.
- `printing_end()` closes all cached print DBs.
- `get_printer_fns_from_type()` and `get_printer_fns()` select `generic_printif`, `cups_printif`, or `iprint_printif` and set the interface type.
- `print_key()` builds binary uint32 TDB keys for job records.
- `pack_devicemode()` and `unpack_devicemode()` serialize `spoolss_DeviceMode` with NDR and store it in a TDB-packed blob.
- `unpack_pjob()` and `pjob_store()` decode and encode `struct printjob` records.
- `print_job_find()`, `print_job_exists()`, `print_job_devmode()`, `print_job_set_name()`, and `print_job_get_name()` expose stored job lookup and metadata operations.
- `sysjob_to_jobid_pdb()`, `sysjob_to_jobid()`, and `jobid_to_sysjob_pdb()` map OS spooler job numbers to Samba job IDs by traversing print DB records.
- `print_queue_update_internal()`, `print_queue_update_with_lock()`, `print_queue_receive()`, and `print_queue_update()` refresh the internal queue cache from the backend lpq interface, either locally or through `samba-bgqd`.
- `print_queue_length()` and `print_queue_status()` provide cached queue status and queue snapshots.
- `print_job_start()`, `print_job_write()`, `print_job_endpage()`, and `print_job_end()` implement the lifecycle of an SMB print job.
- `print_job_delete()`, `print_job_pause()`, `print_job_resume()`, `print_queue_pause()`, `print_queue_resume()`, and `print_queue_purge()` implement administrative and owner-visible controls.
- `print_notify_register_pid()` and `print_notify_deregister_pid()` maintain per-printer notification subscriber PID/refcount lists.

## Control Flow

Startup calls `print_backend_init()`, which opens each printable service DB, locks `INFO/version`, wipes stale DB format versions, then initializes NT printing. Job creation enters `print_job_start()`: access, time, disk-space, autoloaded-printer, and max-job checks run first; `allocate_print_jobid()` locks `INFO/nextjob`, advances the cyclic job ID, stores an empty placeholder, and returns the chosen ID. The job is filled with PID, client, user, queue, devmode, spool state, and a spool file from `print_job_spool_file()`, then `pjob_store()` persists it and appends it to `INFO/jobs_added`.

Writes go through `print_job_write()` only for the creating process and only while not in `PJOB_SMBD_SPOOLING`. `print_job_end()` handles normal or shutdown close by sizing the file, rejecting zero-length or deleting jobs, running the backend `job_submit` callback, switching the job to spooled/queued, and forcing or requesting queue refresh when the cache is stale. Error close or submission failure unlinks the spool file and deletes the job record.

Queue refresh starts with `print_queue_length()` or `print_queue_status()` checking `print_cache_expired()`. If needed, `print_queue_update()` either sends a `MSG_PRINTER_UPDATE` to `samba-bgqd` or performs the update locally. The update path throttles duplicate requests with `MSG_PENDING/<share>`, serializes refreshes with `LOCK/<share>` and `UPDATING/<share>`, runs backend `queue_get`, sorts by submission time, updates or creates jobs, deletes stale records via `traverse_fn_delete()`, stores `INFO/linear_queue_array`, updates `INFO/total_jobs`, writes `STATUS/<share>`, and clears pending state.

Deletion and pause/resume first validate ownership or administrative access. `print_job_delete1()` marks jobs `LPQ_DELETING`, calls backend `job_delete` when already spooled, deletes successful records, and updates the rough job count. `print_job_delete()` also handles unspooled spool-file removal for the owning process, forces a refresh, and returns `WERR_PRINTER_HAS_JOBS_QUEUED` when the job is still deleting.

## State and Persistence

The durable state is in per-printer cache TDBs under `cache_path("printing/")`. Important records include binary job-id keys containing packed `struct printjob`, `INFO/version`, `INFO/nextjob`, `INFO/total_jobs`, `INFO/jobs_added`, `INFO/jobs_changed`, `INFO/linear_queue_array`, `STATUS/<share>`, `CACHE/<share>`, `MSG_PENDING/<share>`, `UPDATING/<share>`, and notification PID lists. Spool data is stored in files under the printer path using `PRINT_SPOOL_PREFIX` and `mkstemp()` unless an external spool file has already been created by smbd. In-memory state is limited to stack/talloc contexts and backend interface selection; job mappings to RAP IDs are delegated to `rap_jobid.c`.

## Dependencies and Integration Points

This file depends on Samba loadparm (`lp_*`) configuration, TDB utility APIs, print interface tables, spoolss NDR for devmode serialization, printer notifications, pcap/printer-list state, server messaging, auth/session info, NT printing initialization, statvfs disk checks, and the background queue daemon helpers from `queue_process.h`. It integrates with `printspoolss.c` through job lifecycle functions, with registry/NT printing through `nt_printing_init()`, with backend-specific `struct printif` operations, and with smbd file close paths.

## Risks and Edge Cases

- Queue refresh is race-sensitive; `CACHE`, `MSG_PENDING`, `LOCK`, and `UPDATING` records reduce duplicate or overlapping lpq scans but stale PIDs or clock changes are explicitly handled.
- `sysjob_to_jobid()` traverses all printer DBs and is intentionally expensive.
- TDB record format is tightly coupled to `tdb_pack` formats and unguarded struct sizes for `print_status_struct`.
- `get_stored_queue_info()` mixes cached linear queue data with `jobs_added` and `jobs_changed`; corrupt list lengths are partly guarded by modulo checks.
- Job ID allocation retries only three candidate IDs and can report no spool space if collisions persist.
- Some status transitions are optimistic because backend delete/pause/resume commands may not synchronously prove final spooler state.
- External spool-file acceptance only verifies it is under the printer path and already exists; path boundary logic is security-relevant.

## Test Signals

The strongest local test signal is exercising Samba print tests with the virtual lp helper `printing/tests/vlp.c`, plus integration tests that start a job, write data, end it, query queue status, pause/resume/delete, and force background queue refresh. Targeted regression checks should include corrupt TDB list lengths, stale updater PID cleanup, clock-skew cache expiry, zero-length print cancellation, max-jobs enforcement, notification PID refcounts, and CUPS/generic backend selection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/printing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/printing_db.c -->
# sources/user-network-fs/samba/source3/printing/printing_db.c

## Purpose

`printing_db.c` manages cached handles for per-printer print TDBs and stores the notification-subscriber PID list helper used by `printing.c`. It is a small persistence/cache layer around `tdb_open_log()` with reference counting and a maximum-open-DB recycling policy.

## Important APIs, Types, and Functions

- `get_print_db_byname()` finds or opens a `struct tdb_print_db` for a printer name, increments its refcount, and promotes it in an intrusive list.
- `release_print_db()` decrements the refcount and asserts it does not go negative.
- `close_all_print_db()` closes every open TDB, removes entries from the list, zeroes, and frees them.
- `get_printer_notify_pid_list()` fetches `NOTIFY_PID_LIST_KEY`, validates record size, and optionally removes dead or zero-refcount entries.

## Control Flow

Lookup first scans `print_db_head` for a matching open `printer_name`. If found, it promotes the entry and returns it. If the cache has reached `MAX_PRINT_DBS_OPEN`, the least-recently-used entry with zero references is closed, cleared, and reused. Otherwise a new entry is allocated and added to the list. Opening builds `cache_path("printing/") + printername + ".tdb"`, temporarily becomes root when needed, and opens the TDB with `O_RDWR|O_CREAT` mode `0600`.

Notification list fetching reads a single TDB record. If the record size is not a multiple of 8 bytes, it is deleted as corrupt. When cleaning is requested, the helper walks pid/refcount pairs and removes entries where the process no longer exists or the refcount is zero, preserving the current process.

## State and Persistence

Open DB handles and reference counts are process-local in `print_db_head`. Persistent records live in one TDB per printer under the printing cache directory. The notification list record is an array of 8-byte entries: pid followed by refcount.

## Dependencies and Integration Points

This file depends on Samba TDB logging, `cache_path()`, privilege switching, `fstring` helpers, process-existence checks, and the `struct tdb_print_db` definition from printing headers. `printing.c` calls these functions for nearly every print job and queue operation.

## Risks and Edge Cases

- A leaked `release_print_db()` would pin a DB handle and reduce the effectiveness of LRU recycling.
- `get_printer_notify_pid_list()` can leave altered list contents in memory without storing them; callers must store cleaned results when they want persistence.
- The open path uses printer names in filenames, so upstream service-name validation remains important.

## Test Signals

Tests should open more than `MAX_PRINT_DBS_OPEN` printers with mixed refcounts, verify LRU reuse avoids referenced handles, validate close-all cleanup, and exercise corrupt notification records plus stale PID cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/printing_db.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/printspoolss.c -->
# sources/user-network-fs/samba/source3/printing/printspoolss.c

## Purpose

`printspoolss.c` bridges SMB print-file opens/writes/closes to the spoolss RPC server. It lets smbd write spool bytes to a local file for scalability and driver seek behavior while spoolss owns printer validation, job creation, final `EndDocPrinter`, and cancellation.

## Important APIs, Types, and Functions

- `struct print_file_data` stores service name, document name, spool filename, spoolss printer handle, 32-bit job ID, and 16-bit RAP job ID.
- `print_spool_rap_jobid()` returns the downlevel RAP job ID.
- `print_spool_open()` creates the spool file, opens the printer over spoolss, starts a document with `output_file`, maps the job to a RAP ID, and initializes the smbd `files_struct`.
- `print_spool_write()` writes bytes at SMB offsets and detects spoolss-side deletion by checking link count.
- `print_spool_end()` closes the printer on normal/shutdown close or terminates the job on error close.
- `print_spool_terminate()` removes RAP mapping and issues `spoolss_SetJob(...DELETE...)` followed by `ClosePrinter`.

## Control Flow

Open allocates per-file data under `fsp`, derives a Windows-like document name from the SMB filename, creates a temporary spool file in the printer path, opens a spoolss pipe, calls `OpenPrinter` with `PRINTER_ACCESS_USE`, and calls `StartDocPrinter` with level 1 document info using datatype `RAW` and the created output file. Once spoolss returns a job ID, `pjobid_to_rap()` creates the RAP mapping and the SMB file object is initialized as a write-only non-directory FSA-backed file.

Writes first `fstat()` the backing descriptor. If spoolss has unlinked the file as a cancellation signal, the descriptor is closed and `EBADF` is returned. For old SMB write semantics, offsets below the high 4GB chunk are rebased against the file size high bits. Failed writes terminate the spool job; successful writes return the byte count.

Close truncates the file if SMB delete-on-close is set, relying on spoolss end-doc cleanup to delete the zero-length job. Normal and shutdown close call `ClosePrinter`, which also ends the document. Error close calls `print_spool_terminate()`.

## State and Persistence

Per-open state lives in `fsp->print_file`; spool bytes live in a temporary file in the print share path. The long-lived spool job state is created by spoolss and lower print backend code. RAP mapping is in the in-memory TDB owned by `rap_jobid.c`.

## Dependencies and Integration Points

The file depends on `rpc_pipe_open_interface()`, generated spoolss client stubs, smbd `files_struct` setup, loadparm paths, FD handle helpers, security/session data, and RAP job-id mapping. It is called by SMB print-file open/write/close handling and relies on spoolss to call into the ordinary print job backend when `EndDocPrinter` happens.

## Risks and Edge Cases

- Open failure after `StartDocPrinter` must delete the spoolss job, so cleanup ordering is important.
- Link-count cancellation detection assumes spoolss communicates deletion by unlinking the file.
- The 4GB offset adjustment is compatibility logic and can be fragile with unusual write sequences.
- `print_spool_end()` assumes `conn->spoolss_pipe` remains valid.

## Test Signals

Integration tests should cover successful open/write/close, open failure cleanup after job creation, delete-on-close truncation, error-close cancellation, spoolss-side unlink during writes, RAP mapping cleanup, and large-offset SMB write behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/printspoolss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/queue_process.c -->
# sources/user-network-fs/samba/source3/printing/queue_process.c

## Purpose

`queue_process.c` starts and manages the background print queue daemon (`samba-bgqd`) and registers its messaging handlers. It isolates expensive pcap reloads, print queue refreshes, stale printer removal, and driver upgrade work from client-serving smbd processes.

## Important APIs, Types, and Functions

- `delete_and_reload_printers_full()` reconciles smb.conf/printer-list state into NT printer registry entries and removes stale autoloaded printers.
- `reload_pcap_change_notify()` reloads printers in the background process and broadcasts `MSG_PRINTER_PCAP`.
- `struct bq_state` keeps tevent, messaging, idle housekeeping, and signal handler state.
- `printing_subsystem_queue_tasks()` schedules printcap housekeeping based on `lp_printcap_cache_time()` and `lp_load_printers()`.
- `register_printing_bq_handlers()` registers `MSG_SMB_CONF_UPDATED`, `MSG_PRINTER_UPDATE`, `MSG_PRINTER_DRVUPGRADE`, signal handlers, loads shares, reloads pcap cache, and schedules housekeeping.
- `start_background_queue()` spawns `samba-bgqd` with ready/watch file descriptors and waits for readiness.
- `printing_subsystem_init()` starts the background daemon and initializes the print backend.
- `send_to_bgqd()` looks up the daemon PID file and sends a message to it.

## Control Flow

Initialization calls `start_background_queue()`, which creates a readiness pipe, builds argv for `samba-bgqd`, spawns it with inherited environment, closes the write end in the parent, and waits to read the daemon PID. After the daemon is available, `print_backend_init()` prepares per-printer TDBs and NT printing.

Inside the daemon, `register_printing_bq_handlers()` registers message handlers for configuration updates, queue-update messages, and driver upgrades. It also installs SIGHUP and SIGCHLD handlers, loads shares for `[printers]`, immediately reloads the pcap cache, and schedules periodic housekeeping. Housekeeping calls `pcap_cache_reload()` with a callback that does full printer reconciliation before notifying smbd processes.

`send_to_bgqd()` is the client-side send path. It reads the `samba-bgqd` PID file and sends `msg_type` and buffer to that process over Samba messaging.

## State and Persistence

`bq_state` is in-memory daemon state. Persistent daemon identity is the `samba-bgqd` PID file. Printer state is not stored here directly; reconciliation updates NT printing/registry state through helper calls and queue updates are performed by handlers in `printing.c`.

## Dependencies and Integration Points

The file depends on tevent, Samba messaging, loadparm, pcap/printer-list APIs, NT printing functions, spoolss driver upgrade handlers, auth system-session creation, locking, pidfile utilities, `posix_spawn()`, and `samba-bgqd`. It is used by smbd startup and by printing queue refresh callers.

## Risks and Edge Cases

- `delete_and_reload_printers_full()` can permanently remove printer and driver registry entries, so it must only be called after a successful pcap reload.
- Failure to start or signal `samba-bgqd` disables normal background refresh and may force local updates elsewhere.
- Signal handlers reload configuration and pcap state while daemon work is live, so handler registration/destruction must be consistent.
- `bq_sig_chld_handler()` inspects `status` after `waitpid`; callers should ensure abnormal child handling remains robust.

## Test Signals

Tests should verify daemon spawn readiness, lost/duplicate daemon PID handling, message registration and deregistration, SIGHUP reload behavior, housekeeping scheduling disabled/enabled cases, `MSG_SMB_CONF_UPDATED` reload, and `send_to_bgqd()` behavior when the PID file is absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/queue_process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/queue_process.h -->
# sources/user-network-fs/samba/source3/printing/queue_process.h

## Purpose

`queue_process.h` declares the public interface for the Samba source3 printing background queue process. It lets smbd initialize the printing subsystem, start the daemon, register daemon-side message handlers, and send messages to the daemon.

## Important APIs, Types, and Functions

- `printing_subsystem_init()` initializes background queue support and the print backend.
- `start_background_queue()` starts `samba-bgqd` and returns its PID.
- `send_to_bgqd()` sends a typed message buffer to the daemon.
- `struct bq_state` is an opaque daemon handler state.
- `register_printing_bq_handlers()` installs background queue daemon messaging and signal handlers.

## Control Flow

The header describes a split lifecycle: smbd calls `printing_subsystem_init()` before serving print workloads; that function can use `start_background_queue()`. The daemon process calls `register_printing_bq_handlers()` after creating messaging and event contexts. Regular code uses `send_to_bgqd()` to send queue-update or related messages.

## State and Persistence

No state is stored in the header. It exposes opaque state ownership through `struct bq_state *`, keeping implementation details in `queue_process.c`.

## Dependencies and Integration Points

The declarations depend on `tevent_context`, `messaging_context`, `dcesrv_context`, and PID types from surrounding Samba headers. They are consumed by print backend and daemon startup code.

## Risks and Edge Cases

The header’s API assumes callers have initialized Samba messaging and event contexts. Misordered startup can produce missing daemon state or failed message delivery.

## Test Signals

Compile-time coverage should ensure prototypes match `queue_process.c`; runtime tests should verify each exported function’s startup/send/registration path through smbd and `samba-bgqd`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/queue_process.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/rap_jobid.c -->
# sources/user-network-fs/samba/source3/printing/rap_jobid.c

## Purpose

`rap_jobid.c` maintains an in-memory bidirectional mapping between Samba/spoolss 32-bit print job IDs and legacy RAP/LANMAN 16-bit job IDs. This supports downlevel APIs that cannot represent full spoolss job IDs.

## Important APIs, Types, and Functions

- `struct rap_jobid_key` combines `fstring sharename` and `uint32_t jobid` for the spoolss-side key.
- `pjobid_to_rap()` returns an existing RAP ID or allocates a new nonzero 16-bit ID and stores both forward and reverse records.
- `rap_to_pjobid()` resolves a RAP ID back to sharename and 32-bit job ID.
- `rap_jobid_delete()` removes both mapping directions for a given share/job ID.

## Control Flow

The first mapping request lazily creates an internal TDB with `TDB_INTERNAL`. `pjobid_to_rap()` looks up the compound key; if found, it returns the stored RAP ID. Otherwise it increments `next_rap_jobid`, skips zero, stores compound-key to RAP-ID and RAP-ID to compound-key records, and returns the new ID. Reverse lookup builds a 2-byte key and expects a `struct rap_jobid_key` value. Deletion first finds the RAP ID from the compound key, then deletes both records.

## State and Persistence

All mappings are process-local and in-memory only. They do not survive process exit. Keys are raw struct bytes for the compound key and two-byte little-endian values for RAP IDs.

## Dependencies and Integration Points

The file depends on TDB internal databases, Samba byte-order helpers, `fstring`, and debug utilities. It is used by `printspoolss.c` when creating or terminating spoolss jobs and by `printing.c` when print jobs are deleted.

## Risks and Edge Cases

- RAP IDs wrap at 16 bits; only zero is skipped, so old mappings can collide after enough allocations if not deleted.
- Raw struct keys depend on stable struct layout and zero-initialization.
- Mappings are per-process, so cross-process RAP lookup only works when the same process handles both operations.

## Test Signals

Tests should cover idempotent forward lookup, reverse lookup with sharename output, deletion of both directions, zero-skip behavior on wrap, and failure when lookup happens before any mapping exists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/rap_jobid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/rap_jobid.h -->
# sources/user-network-fs/samba/source3/printing/rap_jobid.h

## Purpose

`rap_jobid.h` declares the legacy RAP-to-spoolss print job ID mapping API.

## Important APIs, Types, and Functions

- `pjobid_to_rap(const char *sharename, uint32_t jobid)` maps a 32-bit spoolss job to a 16-bit RAP ID.
- `rap_to_pjobid(uint16_t rap_jobid, fstring sharename, uint32_t *pjobid)` resolves a RAP ID.
- `rap_jobid_delete(const char *sharename, uint32_t jobid)` removes a mapping.

## Control Flow

The header exposes a simple create-or-find, resolve, and delete lifecycle for print job ID compatibility.

## State and Persistence

No state is defined in the header; the implementation owns an in-memory TDB and allocation counter.

## Dependencies and Integration Points

It includes `includes.h` for Samba types such as `fstring` and integer typedefs. `printing.c` and `printspoolss.c` are primary consumers.

## Risks and Edge Cases

The API returns `0` for failure from `pjobid_to_rap()`, making zero an invalid RAP ID by contract. Callers must treat false from `rap_to_pjobid()` as lookup failure.

## Test Signals

Header coverage is mostly compile-time; integration tests should verify consumers correctly handle `0` and false lookup results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/rap_jobid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/samba-bgqd.c -->
# sources/user-network-fs/samba/source3/printing/samba-bgqd.c

## Purpose

`samba-bgqd.c` is the executable entry point for Samba’s background print queue daemon. It parses daemon options, creates a singleton PID file, initializes global messaging/session/locking state, registers print queue handlers, reports readiness, watches its parent, and runs the tevent loop.

## Important APIs, Types, and Functions

- `watch_handler()` marks the daemon done when the parent-watch fd becomes readable.
- `bgqd_sig_term_handler()` marks the daemon done on SIGTERM.
- `ready_signal_filter()` replies to `MSG_DAEMON_READY_FD` by writing this process PID to a passed fd.
- `samba_bgqd_pidfile_create()` creates or races for the daemon PID file and forwards readiness fds to an existing daemon if needed.
- `main()` owns full daemon initialization and event loop.

## Control Flow

`main()` preserves fd parameters through `closefrom_except_fd_params()`, initializes Samba command-line parsing, optionally daemonizes, blocks SIGPIPE, initializes locale and core dumps, obtains the global messaging context and event context, and creates the singleton PID file. If a parent-watch fd was provided, it registers an async read that exits the loop when the parent dies. It initializes guest and system session info with winbind temporarily disabled, installs SIGTERM handling, registers background queue handlers through `register_printing_bq_handlers()`, initializes locking, reports daemon readiness, and loops on `tevent_loop_once()` until `done` is set.

When PID-file creation finds an existing daemon, a new instance sends the ready fd to the existing process using `MSG_DAEMON_READY_FD` and exits with `EAGAIN`. The existing process listens with a filtered messaging read and writes its PID to satisfy the parent readiness wait.

## State and Persistence

Runtime state is held in talloc objects under the stack frame: messaging context, event context, signal handlers, watch request, and `bq_state`. Persistent state is the PID file under `lp_pid_directory()`.

## Dependencies and Integration Points

The daemon depends on Samba command-line/daemon helpers, tevent, messaging, pidfile utilities, async fd waits, security session initialization, winbind toggles, locking initialization, global contexts, and `queue_process.c` handler registration. It is spawned by `start_background_queue()`.

## Risks and Edge Cases

- Singleton races are handled through PID file and fd passing; failures in messaging fd transfer can cause parent readiness timeouts.
- `ready_signal_fd` must be closed after successful readiness reporting to avoid fd leaks.
- The daemon exits on any `tevent_loop_once()` error, so handler errors can terminate background print processing.
- Initialization order matters: messaging must exist before PID race handling, and session info must exist before print queue handlers run.

## Test Signals

Tests should spawn two daemons to exercise PID-file race behavior, verify ready fd reporting, verify parent-watch exit, SIGTERM shutdown, failure paths for missing messaging/session/locking setup, and successful registration of queue handlers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/samba-bgqd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/tests/vlp.c -->
# sources/user-network-fs/samba/source3/printing/tests/vlp.c

## Purpose

`vlp.c` implements a virtual lp command for Samba printing tests. It emulates `lpq`, `lprm`, print submission, queue pause/resume, and job pause/resume using a simple TDB-backed queue, allowing print backend tests without a real system spooler.

## Important APIs, Types, and Functions

- `struct vlp_job` stores owner, job ID, job name, size, status, submit time, and deletion flag.
- `get_job_list()` and `set_job_list()` fetch/store `LPQ/<printer>` arrays.
- `next_jobnum()` locks `JOBNUM/<printer>` and allocates job IDs starting at `PRINT_FIRSTJOB`.
- `set_printer_status()` and `get_printer_status()` manage `STATUS/<printer>`.
- Command handlers implement `lpq`, `lprm`, `print`, `queuepause`, `queueresume`, `lppause`, and `lpresume`.
- `main()` parses `tdbfile=...` and dispatches commands.

## Control Flow

The program opens or creates the provided TDB file, chmods it to `0666`, and dispatches based on the subcommand. `print` builds a job owned by the effective user, assigns a job number, and appends it to `LPQ/<printer>`. `lpq` prints printer status followed by non-deleted jobs in a tab-separated format; the first queued job is reported as spooling. `lprm` marks matching jobs as deleted. Queue and job pause/resume mutate status records or job status fields.

## State and Persistence

All test state is stored in the TDB file passed by `tdbfile=...`. Queue entries are raw arrays of `struct vlp_job`, job counters are `JOBNUM/<printer>`, and printer status is `STATUS/<printer>`.

## Dependencies and Integration Points

It depends on Samba printing status constants, TDB helpers, passwd lookup, and filesystem mode changes. Samba test configurations can use it as `lpq command`, `print command`, `lprm command`, and pause/resume commands.

## Risks and Edge Cases

- Queue arrays are raw structs, so format is architecture/build dependent and suited only for tests.
- `get_job_list()` returns `data.dptr` directly and `num_jobs` from size division; corrupt sizes are not explicitly rejected.
- `lprm_command()` does not free `job_list`.
- The final unknown-command error prints `argv[1]` instead of `argv[2]`.

## Test Signals

This file is itself a test helper. Useful checks are command-level tests for append/list/delete, status transitions, queue pause/resume, job pause/resume, missing arguments, and interoperability with Samba’s parsing of lpq output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/printing/tests/vlp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/profile/profile.c -->
# sources/user-network-fs/samba/source3/profile/profile.c

## Purpose

`profile.c` implements Samba smbd profiling collection when profiling support is enabled. It maintains global and per-service counters/timers, receives runtime profiling control messages, dumps per-process statistics into `smbprofile.tdb`, aggregates exited worker data, and exposes collection helpers.

## Important APIs, Types, and Functions

- Globals `profile_p` and `smbprofile_state` hold active profile stats and configuration.
- `set_profile_level()` switches profiling off/counts/full/reset and wipes per-service/profile TDB data on reset.
- `profile_message()` and `reqprofile_message()` handle `MSG_PROFILE` and `MSG_REQ_PROFILELEVEL`.
- `profile_setup()` opens `smbprofile.tdb`, registers message handlers, initializes `profile_p`, and computes the stats magic value.
- `smbprofile_dump_setup()`, `smbprofile_dump_schedule_timer()`, and `smbprofile_dump()` schedule and write profile records.
- `smbprofile_cleanup()` moves a dead worker’s stats into a destination summary record.
- `smbprofile_collect()` aggregates profile records through `profile_read.c`.
- Per-service helpers `smbprofile_persvc_mkref()`, `smbprofile_persvc_unref()`, `smbprofile_persvc_get()`, `smbprofile_persvc_collect()`, and `smbprofile_persvc_reset()` track service-specific activity.

## Control Flow

`profile_setup()` opens `cache_path("smbprofile.tdb")` with mutex locking when writable, optionally registers messaging callbacks, points `profile_p` at the global stats structure, and stores a magic value derived from profile layout. Runtime messages call `set_profile_level()` to adjust counters/timers or reset values.

`smbprofile_dump()` runs when scheduled or called. It exits quickly when profiling is inactive or DB is missing, chain-locks the PID key, parses any previous record, accumulates in-memory counters into it, updates CPU usage and transient session/tcon/file counts, stores the full `profile_stats`, unlocks, clears in-memory counters, and flushes active per-service stats. Cleanup of an exited PID deletes its record, accumulates it into a destination summary record, fixes disconnect count to match connect count, clears transient counters, marks the result as a summary, and stores it.

Per-service profiling grows an array indexed by service number, creates DB keys containing service, PID, snum, and remote, increments/decrements refs as connections are made and released, returns a stats pointer for active services, stores active entries during dump, and deletes entries whose refcount has reached zero.

## State and Persistence

The primary persistent store is `smbprofile.tdb` in the cache directory. Keys are PID bytes for global worker records and string keys for per-service records. In-memory state includes active profiling config, pending stats, event/timer references, smbd connection pointer, and per-service table entries. Profile records include a magic value so readers ignore records from incompatible layouts.

## Dependencies and Integration Points

The file depends on Samba messaging, tevent timers, TDB wrap, profile read helpers, GnuTLS-derived magic from `profile_read.c`, `smbd_server_connection` counters, process IDs from tevent, and optional `getrusage()`. It integrates with smbcontrol/profile commands and smbd connection lifecycle.

## Risks and Edge Cases

- Profile layout changes require magic mismatch handling; stale records are zeroed/ignored.
- Chain-lock failures silently skip dumps or cleanup.
- Reset wipes the TDB and in-memory per-service stats, which is intentionally broad.
- Per-service DB keys include remote names and PIDs; uncontrolled string sizes are bounded only by allocation success.
- Transient counters must not be accumulated across worker cleanup; the code explicitly zeroes them in summary records.

## Test Signals

Tests should cover profile level toggles, request-level response, writable and read-only setup, magic mismatch filtering, dump accumulation with CPU/session counters, cleanup into summary records, per-service ref/store/delete behavior, and reset wiping both global and per-service state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/profile/profile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/profile/profile_dummy.c -->
# sources/user-network-fs/samba/source3/profile/profile_dummy.c

## Purpose

`profile_dummy.c` provides stub implementations when profiling is unavailable in the build. It keeps callers linkable without creating profiling state.

## Important APIs, Types, and Functions

- `profile_setup()` always returns true.
- `set_profile_level()` logs that profiling support is unavailable.

## Control Flow

There is no setup logic. Calls to configure profiling do not change runtime state and only emit a notice.

## State and Persistence

No state is allocated or persisted.

## Dependencies and Integration Points

It includes `smbprofile.h` to match the real profiling API. Build selection chooses this file instead of `profile.c` for non-profiling builds.

## Risks and Edge Cases

Callers that assume profiling commands have an effect will receive success from setup but no data will be produced. That is the intended compatibility behavior for builds without profiling support.

## Test Signals

Compile/link tests should verify the stub satisfies required symbols. Runtime tests should confirm profile setup succeeds and profile-level changes do not crash.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/profile/profile_dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/profile/profile_read.c -->
# sources/user-network-fs/samba/source3/profile/profile_read.c

## Purpose

`profile_read.c` contains layout-aware helpers for accumulating, validating, and reading smbd profile statistics from TDB records. It is shared by the profiling writer and tools that collect profile data.

## Important APIs, Types, and Functions

- `smbprofile_stats_accumulate()` adds every generated stats field from one `profile_stats` into another using the `SMBPROFILE_STATS_ALL_SECTIONS` macro expansion.
- `smbprofile_magic()` hashes the struct contents and generated field names to produce a layout magic value.
- `smbprofile_collect_tdb()` traverses profile TDB records, accumulates records with matching magic, and returns the number of non-summary workers.
- `smbprofile_persvc_collect_tdb()` traverses per-service records and invokes a user callback.

## Control Flow

Accumulation is generated from macros in `smbprofile.h`, ensuring every counter/time/bytes/iobytes section is handled consistently. Magic computation temporarily enables GnuTLS FIPS lax mode, hashes the zero/current stats bytes plus section/field name strings, derives a little-endian 64-bit value from the SHA1 digest, and restores strict mode.

Collection initializes the destination stats with the expected magic, traverses the TDB read-only, filters values that are not exactly `sizeof(struct profile_stats)` or whose magic differs, counts non-summary worker records, and accumulates accepted stats. Per-service collection similarly filters by minimum key size and value size, then calls the provided callback and stops traversal on callback error.

## State and Persistence

This file does not own persistent state. It interprets records already stored in a TDB by `profile.c`. The magic value is the compatibility guard for persisted binary records.

## Dependencies and Integration Points

Dependencies include TDB traversal APIs, GnuTLS hash functions, Samba byte-order helpers, and generated profile macros. `profile.c` calls `smbprofile_magic()`, `smbprofile_stats_accumulate()`, and collection wrappers; external profile tools can use the TDB collection functions.

## Risks and Edge Cases

- Binary `profile_stats` records are ABI-sensitive; magic filtering prevents mixing incompatible layouts but does not migrate old records.
- FIPS mode is deliberately relaxed for SHA1-based compatibility hashing and must be restored.
- Per-service collection does not check magic, only value size, so callback consumers should validate what they need.

## Test Signals

Tests should validate field accumulation across all macro-generated sections, stable nonzero magic for a layout, rejection of wrong-size and wrong-magic records, worker count excluding summary records, callback error propagation, and FIPS mode restoration around hash computation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/profile/profile_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_api.c -->
# sources/user-network-fs/samba/source3/registry/reg_api.c

## Purpose

`reg_api.c` implements a winreg-like high-level API over Samba’s virtual registry layer. It opens hives and subkeys, enforces access masks, caches subkeys and values, enumerates and queries data, creates/deletes keys, sets/deletes values, manages security descriptors, reports registry version, and provides recursive deletion utilities.

## Important APIs, Types, and Functions

- `fill_value_cache()` and `fill_subkey_cache()` refresh `registry_key` caches when backend sequence numbers indicate stale data.
- `regkey_open_onelevel()` allocates a `registry_key`, opens `registry.tdb`, resolves backend hooks, verifies existence by fetching subkeys, and applies `regkey_access_check()`.
- `reg_openhive()` and `reg_openkey()` open hive roots or multi-component paths.
- `reg_enumkey()`, `reg_enumvalue()`, `reg_queryvalue()`, `reg_querymultiplevalues()`, and `reg_queryinfokey()` implement read/query operations.
- `reg_createkey()` creates one or more path components under a transaction and reports opened-vs-created action.
- `reg_deletekey()`, `reg_deletekey_recursive()`, and `reg_deletesubkeys_recursive()` delete keys with transaction handling.
- `reg_setvalue()`, `reg_deletevalue()`, and `reg_deleteallvalues()` mutate value containers.
- `reg_getkeysecurity()` and `reg_setkeysecurity()` delegate security descriptor access.
- `reg_getversion()` returns Windows 2000-compatible version `0x00000005`.

## Control Flow

Opening a key starts with a hive lookup or parent key. `reg_openkey()` splits multi-component paths, opening intermediate components with enumerate access, then opens the final component with requested access. `regkey_open_onelevel()` allocates the key object and handle, duplicates the security token, opens the registry DB with destructor-backed refcounting, marks HKPD performance keys, selects backend ops through `reghook_cache_find()`, fills subkeys to prove existence, and checks access.

Read operations check the access bits stored in the key handle before refreshing caches. Enumeration returns `WERR_NO_MORE_ITEMS` when the requested index exceeds the cached container. Query-by-name scans the existing cache and uses the no-cache-fill enum helper to avoid changing indexes mid-query. Query-info computes max key/value sizes and obtains the security descriptor size via NDR.

Mutation operations are transaction-oriented. `reg_createkey()` starts a DB transaction, recursively creates intermediate path components if needed, checks `KEY_CREATE_SUB_KEY`, calls backend `create_reg_subkey()`, opens the new key, and commits or cancels. `reg_setvalue()` and `reg_deletevalue()` fill the value cache, adjust the container, call `store_reg_values()`, and commit/cancel. `reg_deletekey()` refuses keys with subkeys, while recursive deletion walks children from the end of the subkey list and deletes bottom-up.

## State and Persistence

State is represented by `struct registry_key`, its `registry_key_handle`, cached `regsubkey_ctr` and `regval_ctr` containers, duplicated security token, backend ops pointer, granted access mask, and backend-specific persistent data. Persistent storage is usually `registry.tdb` through `reg_backend_db.c`, but hook backends can overlay virtual values/subkeys. `regkey_destructor()` closes the registry DB reference when the key handle is freed.

## Dependencies and Integration Points

The file depends on registry core types, hook cache lookup, backend DB open/transaction APIs, dispatcher helpers (`fetch_reg_keys`, `store_reg_values`, `create_reg_subkey`, etc.), security token duplication, access-check helpers, NDR security descriptor sizing, and regval/regsubkey containers. It is the core API consumed by RPC winreg handlers and registry utilities.

## Risks and Edge Cases

- Caches rely on backend sequence numbers; a backend with weak `*_need_update` semantics can return stale data.
- `reg_querymultiplevalues()` counts found values but stores each result at the requested-name index, so callers must understand sparse semantics.
- Recursive `reg_createkey()` starts transactions recursively; this relies on underlying transaction nesting behavior.
- Access checks happen at open and before operations; callers retaining handles across policy changes may have stale granted access.
- `reg_deleteallvalues()` deletes while iterating forward over a changing container, which deserves regression coverage.

## Test Signals

Tests should cover hive open failures, path normalization with trailing separators, access denial for missing query/set/create rights, cache refresh on sequence number changes, create existing vs new action, transaction rollback on failed create/set/delete, non-recursive delete refusal for keys with subkeys, recursive deletion order, security descriptor query sizing, and multi-value query behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_api.h -->
# sources/user-network-fs/samba/source3/registry/reg_api.h

## Purpose

`reg_api.h` declares Samba’s high-level virtual registry API, mirroring common winreg operations for hive/key open, enumeration, query, mutation, security, version, and recursive delete.

## Important APIs, Types, and Functions

The header exports `reg_openhive`, `reg_openkey`, enumeration/query APIs, `reg_queryinfokey`, `reg_createkey`, `reg_deletekey`, `reg_setvalue`, `reg_deletevalue`, key security get/set, `reg_getversion`, `reg_deleteallvalues`, `reg_deletekey_recursive`, and `reg_deletesubkeys_recursive`.

## Control Flow

The API model is handle-based: callers open a hive or key with desired access and token, then pass the resulting `registry_key` to query, enumerate, mutate, or delete operations. Recursive helpers operate relative to a parent key.

## State and Persistence

The header defines no state, but its APIs operate on `struct registry_key`, `struct registry_value`, security descriptors, and backend-persistent registry data.

## Dependencies and Integration Points

It depends on Samba WERROR, TALLOC, security token/descriptor, NTTIME, and winreg create action types from surrounding includes. RPC winreg server code and registry utilities consume this public interface.

## Risks and Edge Cases

Callers must request sufficient desired access up front. The create/delete APIs return Windows-style WERROR values, so error mapping must be preserved by consumers.

## Test Signals

Compile-time tests should ensure signatures match implementation and generated RPC callers. API-level tests should use this header to exercise open/query/mutate/delete workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_api_util.c -->
# sources/user-network-fs/samba/source3/registry/reg_api_util.c

## Purpose

`reg_api_util.c` provides a convenience wrapper for opening a complete registry path that includes the hive prefix.

## Important APIs, Types, and Functions

- `reg_open_path()` parses `orig_path`, opens the hive, and optionally opens the remaining subkey path with requested access.

## Control Flow

The function duplicates the input path, finds the first backslash, and treats paths without a non-empty suffix as hive-only opens. For subkey paths it terminates the hive component, opens the hive with `KEY_ENUMERATE_SUB_KEYS`, opens the remainder with the caller’s desired access, frees the temporary hive key, and returns the final key.

## State and Persistence

No state is owned here. It allocates temporary path memory with `SMB_STRDUP()` and registry key objects through `reg_openhive()`/`reg_openkey()`.

## Dependencies and Integration Points

It depends on `reg_api.h`, registry types, security tokens, and registry path utilities. It is a helper for callers that receive full strings such as `HKLM\Software\...`.

## Risks and Edge Cases

- It mutates the duplicated string in place and must free it on all paths.
- Hive-only detection treats a trailing backslash with no key behind it as opening the hive.
- Intermediate hive access is always enumerate-subkeys, which must be enough for the final open traversal.

## Test Signals

Tests should cover hive-only paths, trailing backslash paths, full key paths, unknown hive errors, allocation failure handling where injectable, and access-denied propagation from final open.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_api_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_api_util.h -->
# sources/user-network-fs/samba/source3/registry/reg_api_util.h

## Purpose

`reg_api_util.h` declares utility APIs layered over `reg_api.c`.

## Important APIs, Types, and Functions

- `reg_open_path()` opens a complete registry path containing a hive prefix and optional subkey suffix.

## Control Flow

The declared API collapses the usual `reg_openhive()` plus `reg_openkey()` sequence into one call.

## State and Persistence

The header owns no state. Returned `registry_key` objects are allocated under the caller-provided TALLOC context.

## Dependencies and Integration Points

It depends on registry key and security token types from surrounding registry headers. It is intended for utility callers that parse user-provided registry paths.

## Risks and Edge Cases

Callers still need to pass the desired access and security token appropriate for the final key; the utility does not bypass registry access checks.

## Test Signals

Compile-time coverage plus functional tests through `reg_open_path()` are sufficient.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_api_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_current_version.c -->
# sources/user-network-fs/samba/source3/registry/reg_backend_current_version.c

## Purpose

`reg_backend_current_version.c` implements a virtual registry overlay for `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion`, dynamically exposing Samba-compatible Windows version values while delegating subkeys and unrelated value fetches to the default registry DB backend.

## Important APIs, Types, and Functions

- `current_version_fetch_values()` normalizes the key path and returns virtual `SystemRoot` and `CurrentVersion` values for the target key.
- `current_version_fetch_subkeys()` delegates to `regdb_ops.fetch_subkeys`.
- `current_version_reg_ops` exposes the overlay operations table.

## Control Flow

When values are fetched, the key is duplicated and normalized. If the path does not match the normalized CurrentVersion prefix condition, the request is delegated to `regdb_ops.fetch_values()`. For the CurrentVersion key, it adds `SystemRoot = c:\Windows` and `CurrentVersion = <SAMBA_MAJOR_NBT_ANNOUNCE_VERSION>.<SAMBA_MINOR_NBT_ANNOUNCE_VERSION>` to the provided container and returns the value count.

## State and Persistence

No persistent state is written. Values are generated dynamically. Subkeys are still read from the default registry backend.

## Dependencies and Integration Points

It depends on registry value containers, path normalization, Samba version macros, and the default `regdb_ops`. Hook registration elsewhere maps the CurrentVersion path to `current_version_reg_ops`.

## Risks and Edge Cases

The string comparison uses `strncmp(path, KEY_CURRENT_VERSION_NORM, strlen(path))`, so prefix behavior is sensitive to normalized path length and should be tested for parent/child paths. The overlay does not merge default DB values for the matched key; it returns only virtual values it adds.

## Test Signals

Tests should fetch exact CurrentVersion values, fetch subkeys through delegation, query unrelated paths through delegation, and verify normalized case/backslash behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_current_version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_db.c -->
# sources/user-network-fs/samba/source3/registry/reg_backend_db.c

## Purpose

`reg_backend_db.c` is the default persistent backend for Samba’s virtual registry. It stores key subkey lists, key values, and key security descriptors in `registry.tdb`; initializes built-in registry paths and default values; upgrades old DB formats; exposes transaction/open/close utilities; and publishes a `registry_ops` table used by the high-level registry API.

## Important APIs, Types, and Functions

- Global `regdb` and `regdb_refcount` manage the shared DB context.
- `regdb_trans_do()` wraps actions in a DB transaction and rejects writes if the stored DB version no longer equals `REGDB_CODE_VERSION`.
- `init_registry_key()` and `init_registry_data()` create built-in paths/values.
- `regdb_init()`, `regdb_open()`, `regdb_close()`, transaction wrappers, and `regdb_get_seqnum()` manage DB lifecycle.
- Upgrade helpers normalize slash paths and migrate v2 to v3 by creating missing subkey-list records and deleting sorted subkey caches.
- Key helpers include `regdb_key_exists()`, `regdb_fetch_keys_internal()`, `regdb_store_keys_internal()`, `regdb_create_subkey_internal()`, `regdb_delete_subkey()`, and `regdb_delete_key_lists()`.
- Value helpers include `regdb_fetch_values_internal()`, `regdb_pack_values()`, `regdb_unpack_values()`, and `regdb_store_values_internal()`.
- Security helpers `regdb_get_secdesc()` and `regdb_set_secdesc()` marshal/unmarshal security descriptors.
- `regdb_ops` exports backend operations to the registry dispatcher.

## Control Flow

Initialization opens `state_path("registry.tdb")`, creating it with mode `0600` if necessary and storing the current version. Existing DBs are version-checked; missing version records are treated as v1, unknown/future versions are rejected, and upgrades run inside one transaction. Built-in initialization first checks for missing paths/values to avoid unnecessary writes, then creates all configured built-in path components and default values inside one transaction.

Keys are represented by a normalized key-name record containing a packed count and zero-terminated subkey names. Key existence is defined by a structurally valid subkey-list record. Creating a subkey transactionally fetches the parent list, adds the subkey, stores the parent list, and creates an empty child subkey-list record. Storing subkey lists deletes removed children’s value/security/subkey records before replacing the parent list, then creates records for new children. Deleting a subkey removes value, security, and subkey-list records and optionally removes the child from the parent list.

Values are stored under `REG_VALUE_PREFIX\key` as a packed count plus `name,type,size,data` tuples. Fetching values checks key existence, reads with stable seqnum retry, and unpacks into a `regval_ctr`. Storing values deletes the value record when the container is empty; otherwise it avoids writes if packed data is unchanged and uses transactional store. Security descriptors are stored under `REG_SECDESC_PREFIX\key` using Samba security descriptor marshal helpers.

## State and Persistence

Persistent state is a dbwrap/TDB database at `state_path("registry.tdb")`. Logical namespaces are the raw normalized key path for subkey lists, `REG_VALUE_PREFIX\...` for values, `REG_SECDESC_PREFIX\...` for security descriptors, and `INFO/version` for DB version. In-memory state is the singleton DB context and refcount.

## Dependencies and Integration Points

The backend depends on dbwrap open/store/fetch/traverse/transaction APIs, TDB pack/unpack helpers, registry container objects, registry path normalization, hive metadata, built-in key macros, NT printing key constants, security descriptor marshal/unmarshal, and loadparm clustering checks. `reg_api.c` and registry dispatchers call the exported `regdb_ops` and lifecycle functions.

## Risks and Edge Cases

- DB corruption is detected by subkey-list structural checks; corrupt keys become non-existent and can block operations.
- Raw packed formats are compatibility-sensitive and must preserve endianness/string assumptions.
- Stable reads use seqnum retry loops; heavy concurrent writers can cause repeated fetch attempts.
- Upgrade v2-to-v3 logs inconsistencies and asks for `net registry check` but may continue past some malformed records.
- `regdb_trans_do()` prevents writes during version mismatch, but direct helpers must be routed through it for safety.
- Clustering requires root unless uid wrapper is enabled.

## Test Signals

Tests should cover fresh DB creation, refcounted open/close, version-missing and version-upgrade paths, future-version rejection, built-in path/value idempotence, create/delete subkeys, removed-child data purging, empty value deletion, unchanged value no-op, corrupt subkey/value records, secdesc marshal failures, seqnum cache invalidation, and transaction rollback on injected store failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_db.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_db.h -->
# sources/user-network-fs/samba/source3/registry/reg_backend_db.h

## Purpose

`reg_backend_db.h` declares lifecycle and transaction functions for Samba’s default registry TDB backend.

## Important APIs, Types, and Functions

- `init_registry_key()` and `init_registry_data()` initialize built-in registry structure.
- `regdb_init()`, `regdb_open()`, and `regdb_close()` manage the singleton DB context.
- `regdb_transaction_start()`, `regdb_transaction_commit()`, and `regdb_transaction_cancel()` expose transaction control.
- `regdb_get_seqnum()` returns the backend sequence number used by caches.

## Control Flow

Callers initialize or open the backend before registry operations, use transactions around multi-step mutations, and close handles when registry key objects are freed.

## State and Persistence

The header does not store state. The implementation manages `registry.tdb`, a DB context, and a refcount.

## Dependencies and Integration Points

It includes `registry.h` for WERROR and registry types. `reg_api.c` uses the lifecycle and transaction functions; backend setup code uses initialization functions.

## Risks and Edge Cases

Callers must pair opens with closes and must not assume transactions are active unless start returned `WERR_OK`.

## Test Signals

Compile-time checks plus integration tests around registry open/create/set/delete transaction paths validate this interface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_hkpt_params.c -->
# sources/user-network-fs/samba/source3/registry/reg_backend_hkpt_params.c

## Purpose

`reg_backend_hkpt_params.c` implements a dynamic registry backend for HKPT performance counter parameters. It exposes generated counter names and help text under value names expected by this hive.

## Important APIs, Types, and Functions

- `hkpt_params_fetch_values()` adds `Counters` and `Help` `REG_MULTI_SZ` values from performance counter helpers.
- `hkpt_params_fetch_subkeys()` delegates subkey fetching to `regdb_ops`.
- `hkpt_params_reg_ops` publishes the backend operation table.

## Control Flow

Fetching values obtains the performance counter base index, asks for counter names and help buffers, adds each buffer as a registry multi-string value, frees non-empty buffers, and returns the value count. Subkey requests use the default DB backend.

## State and Persistence

No values are persisted by this backend; all values are generated dynamically from performance counter data. Subkeys remain persisted by `regdb_ops`.

## Dependencies and Integration Points

It depends on `reg_perfcount_get_base_index()`, `reg_perfcount_get_counter_names()`, `reg_perfcount_get_counter_help()`, registry value containers, and default `regdb_ops`. Hook registration maps HKPT parameter paths to this ops table.

## Risks and Edge Cases

- Buffer ownership depends on performance counter helpers returning heap buffers only when size is positive.
- The file intentionally uses `Counters` rather than `Counter`, matching HKPT expectations.
- No store operations are supplied, so mutation should fall back or fail according to dispatcher semantics.

## Test Signals

Tests should verify generated `Counters` and `Help` values, zero-size buffer handling, delegation of subkeys, and correct behavior when performance counter helpers fail or return empty data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_hkpt_params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_netlogon_params.c -->
# sources/user-network-fs/samba/source3/registry/reg_backend_netlogon_params.c

## Purpose

`reg_backend_netlogon_params.c` implements a dynamic registry backend for Netlogon parameters. It exposes the Samba account policy controlling machine password change refusal as a registry DWORD.

## Important APIs, Types, and Functions

- `netlogon_params_fetch_values()` reads `PDB_POLICY_REFUSE_MACHINE_PW_CHANGE` and adds `RefusePasswordChange`.
- `netlogon_params_fetch_subkeys()` delegates to `regdb_ops`.
- `netlogon_params_reg_ops` publishes the backend operations table.

## Control Flow

On value fetch, the backend asks passdb for `PDB_POLICY_REFUSE_MACHINE_PW_CHANGE`; if unavailable, it defaults to `0`. It then adds a `REG_DWORD` value named `RefusePasswordChange` and returns the value count. Subkey fetches are delegated to the persistent DB backend.

## State and Persistence

The exposed value is dynamic and derived from passdb account policy. This backend does not store registry values itself.

## Dependencies and Integration Points

It depends on passdb policy APIs, registry containers, and default `regdb_ops`. It integrates with registry hook dispatch for `KEY_NETLOGON_PARAMS`.

## Risks and Edge Cases

- Failure to read the account policy is indistinguishable from an explicit zero value to registry callers.
- Only fetch operations are defined; mutations must be handled elsewhere or rejected.

## Test Signals

Tests should mock or set account policy to both 0 and 1, verify default 0 on policy read failure, confirm value type/size/name, and verify subkey delegation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_netlogon_params.c -->
