# subset-b-009879 research

Grouped research report for Samba `source3/torture` files under `sources/user-network-fs/samba/source3/torture`. Each section is based on a full read of the mapped source file and is wrapped for reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_chain3.c -->
# sources/user-network-fs/samba/source3/torture/test_chain3.c

Purpose: This file tests SMB1 chained AndX request handling while an oplock break is in flight. `run_chain3()` starts an asynchronous workflow that opens `chain3.txt` with a batch oplock, waits for the oplock break, then submits a chained open/write/close sequence against the same file to exercise request ordering and cleanup in smbd's chain handling.

Important APIs/types/functions: `struct chain3_andx_state` tracks the chained open fnum, write count, and string payload. `chain3_andx_send()` builds three linked SMB1 requests with `cli_openx_create()`, `cli_write_andx_create()`, and `cli_smb1_close_create()`, then dispatches them with `smb1cli_req_chain_submit()`. `chain3_send()` sets up the outer test, uses `cli_smb_oplock_break_waiter_send()`, `cli_ntcreate_send()`, and then calls the AndX helper. The public entrypoint is `run_chain3()`.

Control flow: `run_chain3()` creates a tevent context and polls the outer request. The first phase opens a torture SMB connection and registers an oplock-break waiter. The second phase creates the file with `REQUEST_OPLOCK|REQUEST_BATCH_OPLOCK`. Once the create succeeds, the code submits the chained open/write/close sequence; in parallel the oplock break callback closes the broken fnum. Completion is reported through `chain3_recv()`.

State/persistence behavior: Runtime state is held in talloc-owned tevent request objects and a single remote test file. The chained request stores `"hello"` including its terminator and persists it briefly to the share. The test depends on server-side oplock state, file handles, and SMB1 request chain state; it frees local subrequests as callbacks complete but does not explicitly unlink the test file in this file.

Dependencies and integration points: The test integrates with Samba's torture connection helpers, `async_smb.h`, tevent NTSTATUS helpers, SMB1 client chain helpers, oplock break waiting, and SMB security constants. It is registered as a torture test by the surrounding harness through `run_chain3()`.

Risks: Timing sensitivity is high because oplock break delivery and chained request completion race by design. The test assumes SMB1 support and a Samba server with oplock behavior; dialect restrictions or disabled oplocks make it unrepresentative. Failures can indicate request-chain ordering bugs, stale fnum handling, or oplock cleanup regressions.

Test signals: Passing requires `cli_ntcreate`, oplock break receive/close, chained open/write/close, and final tevent polling to all return successful NTSTATUS values. Diagnostic prints include each callback's returned status and fnum/write counts, making protocol sequencing failures visible.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_chain3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_cleanup.c -->
# sources/user-network-fs/samba/source3/torture/test_cleanup.c

Purpose: This file tests that smbd correctly cleans up server-side share modes and byte-range locks when a connection is forcibly killed. The three exported tests are regression cases around stale lock records causing later opens or writes to behave incorrectly.

Important APIs/types/functions: `run_cleanup1()` checks share-mode cleanup after `smbXcli_conn_samba_suicide()`. `run_cleanup2()` checks byte-range lock cleanup after killing one lock holder. `run_cleanup4()` checks an iteration bug where cleanup of one stale share mode must not skip conflict detection against another live open. Core APIs are `torture_open_connection()`, `cli_openx()`, `cli_ntcreate()`, `cli_lock32()`, `cli_smbwrite()`, `cli_close()`, and `smbXcli_conn_samba_suicide()`.

Control flow: Each test opens one or more SMB connections, creates/open files with specific share and access modes, then kills one smbd-backed connection using the Samba-specific suicide helper. After the kill, a second connection probes whether a new open or write sees the expected post-cleanup state. `run_cleanup2()` also verifies the file is initially locked by expecting `NT_STATUS_FILE_LOCK_CONFLICT` before the kill, sleeps briefly to allow process death, and then expects the write to succeed.

State/persistence behavior: State lives primarily in smbd's locking databases: share-mode records, byte-range lock records, and open file handles. Test files `\cleanup1`, `\cleanup2`, and `\cleanup4` are created on the remote share. Cleanup is server-driven, not local; the point is to prove dead process records are removed while live records remain enforced.

Dependencies and integration points: The tests use Samba torture connection helpers, SMB client calls, low-level locking headers, SMBX client suicide support, and generated open-files NDR definitions. They integrate with the source3 torture suite as individual `run_cleanup*` entrypoints.

Risks: These tests are intentionally Samba-specific because they use `smbXcli_conn_samba_suicide()`. Timing can be fragile around process death; `run_cleanup2()` hard-codes a one-second sleep. Misconfiguration of durable handles, clustering, or nonstandard lock backends can alter cleanup timing.

Test signals: Expected statuses are precise: second open in cleanup1 must succeed, pre-kill write in cleanup2 must return `NT_STATUS_FILE_LOCK_CONFLICT`, post-kill write must succeed, and cleanup4's final conflicting open must return `NT_STATUS_SHARING_VIOLATION`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_cleanup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_ctdbd_conn.c -->
# sources/user-network-fs/samba/source3/torture/test_ctdbd_conn.c

Purpose: This file stress-tests asynchronous CTDB daemon request/response handling through Samba's `ctdbd_connection` layer. It repeatedly sends CTDB `CTDB_CONTROL_ECHO_DATA` controls with random payloads and validates echoed replies while running multiple requests in parallel.

Important APIs/types/functions: `struct ctdb_echo_state` owns a `ctdb_req_control_old`, two iovecs, and expected echo data. `ctdb_echo_send()` constructs a CTDB control request, uses `ctdbd_prep_hdr_next_reqid()`, and sends it with `ctdbd_req_send()`. `ctdb_echo_done()` validates operation, status, data length, and payload bytes from `ctdbd_req_recv()`. `ctdb_ping_flood_send()` maintains a parallel request window until a timed wakeup marks the flood done. The public test is `run_ctdbd_conn1()`.

Control flow: `run_ctdbd_conn1()` creates a Samba tevent context, opens an async CTDB connection using `lp_ctdbd_socket()`, starts `ctdb_ping_flood_send()` with `torture_nprocs` parallel requests and a duration derived from `torture_numops`, then polls and receives the aggregate result. Each completed echo starts another echo until the timer fires; after the timer, the request completes once all in-flight echoes drain.

State/persistence behavior: This is a transient IPC test. Request ids are allocated on the CTDB connection, echo payloads are talloc-owned buffers with random content, and no durable database state is written by the test itself. Persistence concerns are limited to CTDB daemon request queues and socket state.

Dependencies and integration points: It depends on `ctdbd_conn.h`, cluster support, CTDB protocol definitions, `tevent_unix`, and global torture knobs `torture_nprocs` and `torture_numops`. It integrates with clustered Samba deployments and validates the async CTDB client path used by source3 components.

Risks: The test requires a reachable CTDB daemon and valid `lp_ctdbd_socket()`; standalone non-clustered environments will fail setup. Random payload sizes and concurrent request churn expose ordering and lifetime bugs, but also make failures sensitive to CTDB load and timeout settings.

Test signals: Passing requires every echo reply to be `CTDB_REPLY_CONTROL`, status zero, same datalen, and byte-identical payload. Failures print reqid, errno, wrong operation, nonzero status, length mismatch, or data mismatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_ctdbd_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_dbwrap_ctdb.c -->
# sources/user-network-fs/samba/source3/torture/test_dbwrap_ctdb.c

Purpose: This file tests basic transaction semantics for the CTDB-backed dbwrap backend. It verifies that a CTDB database can start/cancel transactions, store and overwrite integer records inside a transaction, commit, and read the committed values back.

Important APIs/types/functions: The only public entrypoint is `run_local_dbwrap_ctdb1()`. It uses `global_messaging_context()`, `db_open_ctdb()`, `dbwrap_transaction_start()`, `dbwrap_transaction_cancel()`, `dbwrap_transaction_commit()`, `dbwrap_store_uint32_bystring()`, and `dbwrap_fetch_uint32_bystring()`. The database is opened as `torture.tdb` with `DBWRAP_LOCK_ORDER_1`.

Control flow: The test opens a CTDB dbwrap context, starts and cancels an empty transaction, starts a second transaction, stores `"foo"=1`, `"bar"=5`, overwrites `"foo"=2`, verifies values before commit, commits, and verifies values after commit. Any unexpected NTSTATUS or nonzero transaction return jumps to cleanup.

State/persistence behavior: The test writes persistent records to the CTDB-backed TDB named `torture.tdb`. It intentionally validates that transaction commit reaches disk/backend state by fetching after commit. It does not unlink the database, so test isolation relies on deterministic overwrites of the specific keys.

Dependencies and integration points: It depends on dbwrap CTDB support, source3 messaging, CTDB message glue, global contexts, and the TDB/dbwrap API. It is a local torture test for database backend integration rather than SMB protocol behavior.

Risks: Requires CTDB dbwrap support and a functioning messaging context. Existing `torture.tdb` content for unrelated keys is ignored, but backend permission or cluster configuration can make open fail. Transaction bugs may appear as stale reads, lost overwrites, or commit failures.

Test signals: Expected key values are `"foo"=2` and `"bar"=5` both before and after commit. Failure messages identify transaction start/cancel/commit failures, store/fetch NTSTATUS, and mismatched fetched integer values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_dbwrap_ctdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_dbwrap_do_locked.c -->
# sources/user-network-fs/samba/source3/torture/test_dbwrap_do_locked.c

Purpose: This file tests `dbwrap_do_locked()` against a watched dbwrap database. It verifies that a callback can atomically store a record while holding the lock, that the stored value is visible through parsing, and that a second locked callback can delete the record.

Important APIs/types/functions: `struct do_locked1_state` carries the expected value and callback status. `do_locked1_cb()` stores through `dbwrap_record_store()`, `do_locked1_check()` compares using `tdb_data_cmp()`, and `do_locked1_del()` deletes via `dbwrap_record_delete()`. `run_dbwrap_do_locked1()` opens a TDB backend, wraps it with `db_open_watched()`, and exercises `dbwrap_do_locked()` and `dbwrap_parse_record()`.

Control flow: The public test initializes global event and messaging contexts, opens `test_do_locked.tdb` with `TDB_CLEAR_IF_FIRST`, wraps the backend, stores `"value"` under key `"key"` through a locked callback, parses the record to verify bytes, deletes through another locked callback, then parses again expecting `NT_STATUS_NOT_FOUND`.

State/persistence behavior: The test creates a local TDB file and removes it at the end with `unlink(dbname)`. Record state is transient and intentionally moves through absent -> present -> absent. The watched wrapper also maintains watcher metadata internally, although this test focuses on lock callback behavior.

Dependencies and integration points: It depends on `lib/dbwrap`, watched dbwrap support, util TDB helpers, source3 util TDB helpers, and global Samba event/messaging contexts. It integrates with the same watched dbwrap layer used by higher-level database notification code.

Risks: Cleanup only unlinks on the normal fail label after `db` is created; early backend-open failures can leave nothing to clean but also skip `backend` free. Failures in watched backend behavior may surface as callback status mismatches rather than direct `dbwrap_do_locked()` errors.

Test signals: Passing requires `dbwrap_do_locked()` to return OK for store and delete, callback status to be OK, parse comparison to match exactly, and final parse to return `NT_STATUS_NOT_FOUND`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_dbwrap_do_locked.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_dbwrap_watch.c -->
# sources/user-network-fs/samba/source3/torture/test_dbwrap_watch.c

Purpose: This file tests the watched dbwrap API: keyed watch notification, invalid watched-record data handling, cleanup of dead watchers, and rejection of duplicate watches in one locked update round.

Important APIs/types/functions: `test_dbwrap_watch_init()` creates a tevent context, messaging context, TDB backend, and watched wrapper via `db_open_watched()`. `run_dbwrap_watch1()` uses `dbwrap_fetch_locked()` and `dbwrap_watched_watch_send()`. `run_dbwrap_watch2()` writes invalid watcher metadata directly to the backend. `run_dbwrap_watch3()` forks a child that registers a watch then exits. `run_dbwrap_watch4()` uses `dbwrap_do_locked()` and two watch requests to verify duplicate rejection.

Control flow: The first test watches key `"key"`, stores a different key to prove no completion, stores the watched key, polls the request, and expects success. The second test stores `UINT32_MAX` directly in the backend and expects the watched wrapper to treat it as not found. The third test waits for a child watcher process to exit, then stores the watched key and expects dead watcher cleanup not to fail. The fourth test creates two watches within one locked callback, stores the key, drains the event loop, and expects the first request OK and the second `NT_STATUS_REQUEST_NOT_ACCEPTED`.

State/persistence behavior: All tests use `test_watch.tdb` and unlink it on success paths. Persistent state includes regular records plus watched-db metadata used to resume or notify watchers. Process liveness matters because dead watcher records must be cleaned when a store occurs.

Dependencies and integration points: The file depends on tevent, messaging, dbwrap open APIs, watched dbwrap, TDB utilities, fork/wait behavior, and NTSTATUS request lifecycles. It covers a core integration point between dbwrap record updates and Samba interprocess messaging.

Risks: Forked watcher cleanup is timing and platform sensitive. Some failure paths do not unlink the test database before returning, which can affect later manual runs. Duplicate-watch semantics are subtle because both requests are created in one locked record callback and endtimes are used to avoid indefinite waits.

Test signals: Key success signals are watch completion after the target key changes, `NT_STATUS_NOT_FOUND` for invalid backend watcher data, successful store after a dead child watcher exits, and `NT_STATUS_REQUEST_NOT_ACCEPTED` for the second same-round watch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_dbwrap_watch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_g_lock.c -->
# sources/user-network-fs/samba/source3/torture/test_g_lock.c

Purpose: This file is a broad torture suite for Samba's global lock (`g_lock`) API. It covers basic lock/unlock semantics, lock data storage, read/write upgrade behavior, interprocess contention, stale lock cleanup, upgrade deadlock detection, data watch notification, and a ping-pong performance pattern.

Important APIs/types/functions: `get_g_lock_ctx()` obtains global tevent and messaging contexts and creates a `g_lock_ctx`. Public entrypoints include `run_g_lock1()` through `run_g_lock8()` plus `run_g_lock_ping_pong()`. Key APIs are `g_lock_lock()`, `g_lock_lock_send()/recv()`, `g_lock_unlock()`, `g_lock_write_data()`, `g_lock_dump()`, and `g_lock_watch_data_send()`. Parser callbacks validate exclusive/shared lockers and stored data.

Control flow: Simple tests run in-process: double-write lock returns `NT_STATUS_WAS_LOCKED`, unlocking an absent lock returns `NT_STATUS_NOT_FOUND`, writing data requires a held write lock, and read locks upgrade to write locks. Contention tests fork children holding read or write locks, coordinate with pipes, then verify immediate timeouts, async acquisition after child exit, and dump contents. Cleanup tests fork children that exit while holding locks to check heuristic removal of stale server ids. Deadlock testing arranges two readers attempting upgrade and expects `NT_STATUS_POSSIBLE_DEADLOCK`. The watch test starts a data watch, writes nonempty then empty data under a write lock, unlocks, and polls the watch.

State/persistence behavior: Lock state is stored in the g_lock backend and includes exclusive locker, shared locker array, and optional data bytes. Tests rely on process identity from messaging server ids and fork reinitialization via `reinit_after_fork()`. Some locks are intentionally stale after child exit to exercise cleanup.

Dependencies and integration points: Dependencies include source3 messaging, server id utilities, sys read/write wrappers, TDB utilities, tevent NTSTATUS helpers, and global contexts. The suite validates global locking used by clustered and multi-process Samba subsystems.

Risks: Fork/pipe synchronization and process liveness checks are inherently timing sensitive. The tests assume specific NTSTATUS behavior for conflicts, upgrades, and stale cleanup. Clustered mode lacks clear-if-first semantics, so `run_g_lock6()` explicitly wipes stale lock state before starting.

Test signals: Passing emits expected statuses for all lock transitions: OK, `WAS_LOCKED`, `NOT_FOUND`, `NOT_LOCKED`, `IO_TIMEOUT`, `POSSIBLE_DEADLOCK`, and successful async completion. Dump parser callbacks verify the exact locker identity and number of locks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_g_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_hidenewfiles.c -->
# sources/user-network-fs/samba/source3/torture/test_hidenewfiles.c

Purpose: This file tests Samba's "hide new files timeout" behavior. It verifies that a newly created unreadable file is hidden from directory listings until the configured timeout has elapsed, while containing directories remain visible.

Important APIs/types/functions: `servertime()` creates and deletes a temporary file to obtain server-side creation time. `have_file_fn()` and `have_file()` list the share with `cli_list()` and test whether a name is visible. Public entrypoints are `run_hidenewfiles()` and `run_hidenewfiles_showdirs()`.

Control flow: `run_hidenewfiles()` opens a connection, removes stale test files, creates `new_hidden.txt`, records its last-write time, then loops: list for visibility, fetch current server time by creating `timestamp.txt`, compute age, and sleep until the file becomes visible. It fails if the file appears before five seconds or remains hidden past ten times that interval. `run_hidenewfiles_showdirs()` creates `dir/x.txt` and immediately verifies that `dir` itself is visible.

State/persistence behavior: Remote files and directories are created on the test share. `new_hidden.txt` is marked delete-on-close in cleanup. `servertime()` uses `FILE_DELETE_ON_CLOSE` for the timestamp probe. The behavior depends on server-side timestamps and smb.conf's hide-new-files configuration.

Dependencies and integration points: The file depends on torture SMB connection helpers, `cli_ntcreate()`, `cli_list()`, `cli_unlink()`, `cli_mkdir()`, `cli_rmdir()`, security access masks, and NT time conversion. It integrates with VFS/share configuration for hiding newly created files.

Risks: The code hard-codes `hideunreadable_seconds = 5` with a comment saying this is configured in smb.conf. Mismatch between configuration and test constant causes false failures. Server/client clock conversion and directory listing filters are also important.

Test signals: Passing requires no early listing visibility for `new_hidden.txt`, eventual visibility within the allowed bound, and immediate visibility of the parent directory in the showdirs case.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_hidenewfiles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_idmap_cache.c -->
# sources/user-network-fs/samba/source3/torture/test_idmap_cache.c

Purpose: This file tests Samba's local idmap cache for SID-to-unixid and unixid-to-SID lookups, including deletion and negative mapping behavior.

Important APIs/types/functions: The public entrypoint is `run_local_idmap_cache1()`. It uses `dom_sid_parse()`, `dom_sid_equal()`, `idmap_cache_set_sid2unixid()`, `idmap_cache_find_sid2unixid()`, `idmap_cache_find_xid2sid()`, and `idmap_cache_del_sid()`. Data types are `struct dom_sid` and `struct unixid`.

Control flow: The test stores a UID mapping for a concrete domain SID, looks it up by SID and by unixid, verifies the returned type/id and SID, confirms that changing the lookup type to GID does not find the UID mapping, deletes the SID mapping, then verifies the UID lookup is gone. It then stores a negative mapping using the zero SID and verifies that reverse lookup finds the negative result.

State/persistence behavior: The idmap cache is global/local process state backed by Samba cache infrastructure, not by a file created in this test. The `expired` flag is checked on every successful lookup and must be false. Deletion mutates the cache and is verified immediately.

Dependencies and integration points: It depends on `lib/idmap_cache.h`, generated idmap NDR types, and SID helpers. The test is a local cache contract check used by winbind/idmap code paths.

Risks: Cache state from other tests could interfere if the same SID/xid keys are reused, though this test uses a specific SID and deletes it. Negative mapping semantics are easy to regress because a zero SID is a valid cache payload with special meaning.

Test signals: Passing requires successful nonexpired forward and reverse lookups, correct UID/GID discrimination, no stale lookup after deletion, and successful reverse lookup of the negative zero-SID mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_idmap_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_idmap_tdb_common.c -->
# sources/user-network-fs/samba/source3/torture/test_idmap_tdb_common.c

Purpose: This file is a comprehensive unit-style test for idmap TDB common allocation and mapping code. It validates high-water-mark allocation, SID/unixid mapping creation, one-to-one constraints, batch lookup status codes, read-only behavior, and range exhaustion.

Important APIs/types/functions: The file defines stub winbind functions (`find_domain_from_name()`, `get_global_winbindd_state_offline()`, `winbindd_use_idmap_cache()`) so idmap code can run locally. `open_db()` creates `idmap_test.tdb` under `lp_private_dir()` and initializes `GROUP HWM` and `USER HWM` to `LOW_ID`. `idmap_test_tdb_db_init()` installs `idmap_tdb_common_get_new_id()` and `idmap_tdb_common_set_mapping()` in an `idmap_rw_ops`. `createdomain()` builds an `idmap_domain` with low/high range 100..199. `run_idmap_tdb_common_test()` sequences all checks.

Control flow: The test initializes a domain and database, allocates a single id, sets valid UID and GID mappings while rejecting invalid parameters and SID/type conflicts, tests single SID-to-unixid and unixid-to-SID lookups, tests batch `sids_to_unixids()` and `unixids_to_sids()` including NONE_MAPPED/SOME_UNMAPPED/OK statuses, toggles `dom->read_only` for status-only lookup behavior, and finally consumes the remaining id range to ensure allocation fails when exhausted.

State/persistence behavior: Persistent state is in `idmap_test.tdb`: high-water-mark keys and bidirectional mapping records. Tests share one domain/database across the sequence, so earlier mappings are intentionally reused by later batch lookup status tests. The file does not explicitly unlink the database.

Dependencies and integration points: It integrates with winbind idmap headers, dbwrap TDB open APIs, domain SID helpers, idmap RW methods, and Samba private-dir configuration. It tests the common backend code used by idmap TDB implementations.

Risks: Because state accumulates across test functions, order matters; `CHECKRESULT` short-circuits on first failure. Existing database contents or previous partial runs can affect high-water marks unless the private test database is reset externally. Range exhaustion is deterministic only with the configured `LOW_ID`/`HIGH_ID`.

Test signals: Passing requires exact NTSTATUS values for invalid parameters, conflict rejection, out-of-range lookup rejection, mapping-state statuses, successful round-trip equality with `dom_sid_equal()`, nonzero allocated ids within range, and final allocation failure after the pool is depleted.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_idmap_tdb_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_matching.c -->
# sources/user-network-fs/samba/source3/torture/test_matching.c

Purpose: This file tests Samba path matching utilities for MS wildcard lists and regular-expression-with-one-substitution lists. It compares legacy matching behavior with the newer `samba_path_matching` abstraction and validates match indexes and replacement spans.

Important APIs/types/functions: `run_str_match_mswild()` exercises `set_namearray()`, `is_in_path()`, `samba_path_matching_mswild_create()`, and `samba_path_matching_check_last_component()`. `run_str_match_regex_sub1()` exercises `samba_path_matching_regex_sub1_create()` and checks invalid regex lists. Data tables encode expected match indexes for case-sensitive and case-insensitive modes plus expected regex subgroup start/end offsets.

Control flow: The MS wildcard test creates both case-sensitive and case-insensitive matchers from `/abc*.txt/xyz*.dat/a0123456789Z/`, iterates representative paths, compares legacy boolean membership with matcher index output, and requires no replacement span. The regex test first asserts that malformed lists return `NT_STATUS_INVALID_PARAMETER`, then creates a valid matcher and checks path matches plus the first captured subgroup offsets.

State/persistence behavior: This is an in-memory utility test. Matchers and name arrays are talloc-owned; there is no file, network, or persistent cache state. Diagnostic output goes to stderr.

Dependencies and integration points: It depends on `lib/util_matching.h`, torture prototypes, `SMB_ASSERT`, and Samba string/path matching utilities used by include/exclude and path rewrite style configuration.

Risks: The tests assert on many setup failures, so malformed matcher behavior can abort rather than return false. Regex offset expectations are byte-index based and depend on last-component matching semantics; changes in path normalization or regex dialect will require updating the fixture table.

Test signals: Passing requires expected indexes for all wildcard samples, rejection of four invalid regex lists, expected match indexes for valid regex samples, and exact captured replacement start/end offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_matching.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_messaging_fd_passing.c -->
# sources/user-network-fs/samba/source3/torture/test_messaging_fd_passing.c

Purpose: This file tests Unix file-descriptor passing through Samba's messaging layer. It covers self-send behavior and parent-to-child fd passing with large, small, and zero payloads to exercise both queued/fragmented and fast paths.

Important APIs/types/functions: `run_messaging_fdpass1()` sends one pipe fd to its own `messaging_server_id()`. `fdpass2_filter()` selects messages with `MSG_TORTURE_FDPASS2` and exactly two fds. `fdpass2_child()` waits with `messaging_filtered_read_send()/recv()` and echoes a byte between passed pipes. `fdpass2_parent()` creates up/down pipes, sends fds with `messaging_send_iov()`, waits for child readiness through tevent fd callbacks, and verifies byte round-trip. Public variants are `run_messaging_fdpass2()`, `run_messaging_fdpass2a()`, and `run_messaging_fdpass2b()`.

Control flow: The parent and child synchronize on a ready pipe. The parent sends the child's process id as the message destination, passes the read end of one pipe and write end of another, closes its copies after child confirmation, writes a byte, and expects to read the same byte back. Payload size is parameterized: 1 MB for fragmentation/reassembly, one byte for fast path with payload, and zero bytes for fast path without payload.

State/persistence behavior: State is transient IPC: pipes, process ids, messaging sockets, tevent fd handlers, and talloc frames. No durable data is written. Correctness depends on fd lifetime and close ordering after descriptor transfer.

Dependencies and integration points: It depends on Samba messaging, tevent Unix helpers, fork/wait, DATA_BLOB/iovec payload handling, and messaging fd-passing support. It validates infrastructure used by source3 daemons to transfer descriptors between processes.

Risks: Platform support for Unix-domain fd passing is required. The large payload path can expose resource limits or socket buffering issues. Child readiness and completion use byte pipes, so missed synchronization can deadlock or fail the test.

Test signals: Passing requires `messaging_send_iov()` OK, filtered read receiving exactly two fds, child confirmation, successful byte round-trip through passed descriptors, and child `waitpid()` success for all three payload variants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_messaging_fd_passing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_messaging_read.c -->
# sources/user-network-fs/samba/source3/torture/test_messaging_read.c

Purpose: This file tests edge cases in `messaging_read`: competing readers for the same message type, freeing one pending request from another request's callback, repeated ping/pong against a child process, and large message payload transfer.

Important APIs/types/functions: `msg_count_send()` creates a persistent read loop that increments a counter and re-arms `messaging_read_send()`. `msg_free_send()` frees another pending request when its own read completes. `msg_pingpong_send()` sends `MSG_PING` and waits for `MSG_PONG`. `ping_responder()` runs a child event loop until an exit pipe fires. `read4_child()` and `read4_parent()` transfer a 1 MB `MSG_TORTURE_READ4` payload. Public tests are `run_messaging_read1()` through `run_messaging_read4()`.

Control flow: `run_messaging_read1()` starts two readers for `MSG_SMB_NOTIFY`, sends one message to itself, runs two event iterations, and expects only the first counter to increment. `run_messaging_read2()` starts a read whose callback frees the second pending read and verifies no second callback fires. `run_messaging_read3()` forks a responder, sends 100 ping/pong requests to the child pid, then signals exit. `run_messaging_read4()` forks a child receiver, sends a 1 MB iovec message, waits for child confirmation, and reaps it.

State/persistence behavior: All state is in process-local messaging contexts, tevent requests, pipes, child processes, and transient message buffers. No persistent files are created. The tests intentionally mutate tevent request ownership/lifetime to catch use-after-free or double-dispatch bugs.

Dependencies and integration points: It depends on Samba messaging, tevent Unix helpers, process synchronization, and the automatic MSG_PING/MSG_PONG messaging behavior. It covers infrastructure used broadly by source3 multi-process services.

Risks: Reentrant free behavior is delicate; a bug may surface as crashes rather than clean NTSTATUS failures. Large payload transfer depends on messaging fragmentation and memory availability. Child process cleanup must be reliable to avoid hanging tests.

Test signals: Expected outcomes are count `1/0` in read1, zero count after freeing the second request in read2, 100 successful ping/pong cycles in read3, and successful receive/confirmation of the 1 MB message in read4.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_messaging_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_messaging_send_all.c -->
# sources/user-network-fs/samba/source3/torture/test_messaging_send_all.c

Purpose: This file tests `messaging_send_all()` broadcast behavior. It verifies that all forked responder processes receive a broadcast ping and reply with pongs, while the sender does not receive its own broadcast.

Important APIs/types/functions: `fork_responder()` forks a child using a shared messaging context, calls `messaging_reinit()` in the child, signals readiness, and waits on an exit pipe. `collect_pong_send()` creates a request that repeatedly calls `messaging_read_send()` for `MSG_PONG`. `collect_pong_received()` tracks which child pids have replied and rejects a pong from the parent pid. The public entrypoint is `run_messaging_send_all()`.

Control flow: The parent initializes tevent and messaging, creates an exit pipe, forks `MAX(5, torture_nprocs)` responders, starts pong collection with a ten-second endtime, calls `messaging_send_all(MSG_PING)`, polls until all children have replied, closes the exit pipe, and waits for every child.

State/persistence behavior: State is transient process and messaging state: child pid array, exit/ready pipes, tevent request state, and the list of senders still expected. No files or databases are written. Children exit when the parent closes the exit pipe they are watching.

Dependencies and integration points: It depends on Samba messaging broadcast semantics, `messaging_reinit()` after fork, `wait_for_read_send()` from async socket helpers, sys read/write wrappers, and global `torture_nprocs`. It validates broadcast messaging used for daemon notifications.

Risks: Broadcast fan-out is sensitive to process registration timing, so `fork_responder()` blocks until each child signals readiness. The test rejects self-broadcasts with `EMULTIHOP`; any semantic change that includes the sender will fail. High `torture_nprocs` increases process and message load.

Test signals: Passing requires all expected child pids to produce one `MSG_PONG`, no pong from the parent pid, successful collection before the ten-second endtime, and successful `waitpid()` for every responder.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_messaging_send_all.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_namemap_cache.c -->
# sources/user-network-fs/samba/source3/torture/test_namemap_cache.c

Purpose: This file tests the name/SID mapping cache, including invalid cache payload rejection, case-insensitive domain/name lookup, empty-domain handling, and domain-only entries with an empty account name.

Important APIs/types/functions: Callback helpers `namemap_cache1_fn1()` through `namemap_cache1_fn6()` validate returned domain/name/type or SID/type values. `run_local_namemap_cache1()` uses `gencache_set()`, `namemap_cache_set_sid2name()`, `namemap_cache_find_sid()`, `namemap_cache_set_name2sid()`, and `namemap_cache_find_name()`. It uses well-known SIDs `global_sid_Network`, `global_sid_World`, and a local domain SID constant.

Control flow: The test first stores an invalid raw gencache value for `SID2NAME/S-1-5-2` and expects the namemap parser not to accept it. It then stores and finds `NT Authority\Network` both by SID and by lower-case name, verifies a missing name lookup fails, repeats the process for an empty-domain `Everyone` mapping, and finally tests a domain-only mapping `SAMBA-DOM` with empty name.

State/persistence behavior: State is stored in Samba's generic cache with explicit expirations of `time(NULL)+60`. The test mutates shared cache keys for well-known SIDs. Returned `expired` flags are supplied to callbacks but the callbacks focus on values and SID types.

Dependencies and integration points: It depends on `lib/namemap_cache.h`, SID helpers, gencache, and LSA SID type enums. It covers cache behavior used by name resolution and SID lookup paths.

Risks: Cache pollution from earlier runs can matter for the same well-known keys, although the test overwrites the keys it uses. Time-based expiry is short but should not expire during normal execution. Case normalization behavior is part of the contract and must be preserved.

Test signals: Passing requires invalid gencache data to be rejected, all stored mappings to be found with expected normalized domain/name/type or SID/type, missing `foo\bar` to fail, and empty-domain/domain-only cases to round-trip.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_namemap_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_notify.c -->
# sources/user-network-fs/samba/source3/torture/test_notify.c

Purpose: This file contains scalability and synchronization tests for SMB change notifications. It creates many outstanding notify requests, triggers directory changes, and uses barriers to coordinate concurrent notify registration and cleanup.

Important APIs/types/functions: `wait_for_one_notify_send()` opens a directory, issues `cli_notify_send()`, sends a `cli_chkpath_send()` barrier request to ensure the notify reached the server, and closes after notification. `run_notify_bench2()` starts many of these requests. `notify_bench3_send()` implements a longer state machine with `tevent_barrier` objects, directory creation, recursive notifications, subdirectory creation/deletion, delete-on-close, and close. Public entrypoints are `run_notify_bench2()` and `run_notify_bench3()`.

Control flow: Bench2 creates `\notify.dir`, opens `torture_nprocs` connections, starts `torture_numops` notify waiters per connection, waits until every waiter has passed the chkpath synchronization point, creates `\notify.dir\subdir`, then drains until all notifications close. Bench3 creates two barriers: a small barrier for per-round synchronization and a large barrier for notification/deletion phases. Each request opens a directory, waits with peers before registering notify, confirms registration, creates a related subdirectory, waits for notify delivery, deletes subdirectories, sets delete-on-close on the directory, and closes.

State/persistence behavior: Remote directory trees are created and removed under names such as `\notify.dir` and `\dirNNNNNNNN`. State includes many open directory handles, outstanding notify requests, tevent barriers, and counters. Persistence is intentionally temporary but cleanup is distributed across async callbacks.

Dependencies and integration points: The file depends on Samba SMB client async APIs, notification structures, tevent NTSTATUS helpers, security masks, `tevent_barrier`, and global torture concurrency knobs. It validates server notify scalability and ordering.

Risks: These are high-concurrency timing tests. Missed barrier participation, notification loss, or cleanup errors can hang or fail. Directory names in bench3 intentionally cross-reference neighboring indexes, so off-by-one changes can alter notification topology.

Test signals: Passing requires every notify to be registered before the trigger, all notifications to complete, all async state machines to return OK, and final `num_done` or `num_notifies` counters to reach expected values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_notify_online.c -->
# sources/user-network-fs/samba/source3/torture/test_notify_online.c

Purpose: This file tests that reading an offline file through SMB triggers a file attribute change notification indicating the file has become online or otherwise changed. It is driven by the external `test_filename` argument.

Important APIs/types/functions: `struct notify_online_state` tracks directory and file handles plus a `got_notify` flag. `notify_online_send()` opens the containing directory, starts `cli_notify_send()` for `FILE_NOTIFY_CHANGE_ATTRIBUTES`, opens the target file, reads one byte with `cli_read_andx_send()`, closes file and directory, and waits up to ten seconds. `notify_online_recv()` returns whether the expected notify was observed. Public entrypoint is `run_notify_online()`.

Control flow: `run_notify_online()` requires `test_filename`, splits it into directory and basename, opens a torture connection, and calls `notify_online()`. The async state machine starts the notify before reading the file. The notify callback checks for exactly one change with `NOTIFY_ACTION_MODIFIED` and matching filename, then marks success.

State/persistence behavior: The test does not create the target file; it operates on the supplied file path and changes server-side file state indirectly by reading. State includes one directory handle, one file handle, an outstanding notify request, and a ten-second wakeup before directory close.

Dependencies and integration points: It depends on SMB client async create/read/close/notify calls, tevent NTSTATUS polling, security masks, and the torture harness global `test_filename`. It integrates with offline-file/VFS behavior where reads should trigger online transition notifications.

Risks: Requires an appropriately configured offline file; running it on a normal file may not produce the notify. Filename splitting uses `/`, while SMB paths may be environment-dependent. The notify matching is strict about action count, action type, and name.

Test signals: Passing requires `notify_online()` to return OK and `got_notify` true. Diagnostics print the returned NTSTATUS and boolean flag.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_notify_online.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_nttrans_create.c -->
# sources/user-network-fs/samba/source3/torture/test_nttrans_create.c

Purpose: This file tests NT transaction create with an explicit security descriptor, specifically that a file created without `WRITE_DAC` for Everyone subsequently denies an open requesting `WRITE_DAC_ACCESS`.

Important APIs/types/functions: The public entrypoint is `run_nttrans_create()`. It builds a `security_ace`, `security_acl`, owner SID, and self-relative `security_descriptor` via `make_sec_desc()`. It uses `cli_nttrans_create()`, `cli_query_secdesc()`, `cli_ntcreate()`, and `cli_nt_delete_on_close()`.

Control flow: The test opens a torture SMB connection, constructs an ACL granting `SEC_RIGHTS_FILE_ALL` except `SEC_STD_WRITE_DAC` to `global_sid_World`, creates `transtest` through `cli_nttrans_create()` with that descriptor, queries the security descriptor for diagnostics, then attempts a normal `cli_ntcreate()` asking for `WRITE_DAC_ACCESS`. It sets delete-on-close on the original handle and succeeds only if the second open returns `NT_STATUS_ACCESS_DENIED`.

State/persistence behavior: The remote file `transtest` is created and then marked delete-on-close through its original handle. Security descriptor state is persisted to the server long enough to test access checks.

Dependencies and integration points: It depends on Samba SMB client create APIs, security descriptor construction helpers, SID parsing, ACL constants, and torture connection helpers. It validates the server path that accepts security descriptors in NT_TRANSACT_CREATE.

Risks: Access-check behavior depends on server security model and share permissions. If the descriptor is not applied, inherited permissions may allow `WRITE_DAC`. The failure message for the second create prints `status` rather than `status2`, which can obscure diagnostics.

Test signals: Passing requires NT transaction create OK, delete-on-close OK, and the `WRITE_DAC_ACCESS` open to return exactly `NT_STATUS_ACCESS_DENIED`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_nttrans_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_nttrans_fsctl.c -->
# sources/user-network-fs/samba/source3/torture/test_nttrans_fsctl.c

Purpose: This file probes NT transaction FSCTL handling for several control codes and expected statuses. It creates a file, marks it delete-on-close, then sends raw `SMBnttrans` `NT_TRANSACT_IOCTL` requests through `cli_trans()`.

Important APIs/types/functions: The public entrypoint is `run_nttrans_fsctl()`. It uses `cli_nttrans_create()`, `cli_nt_delete_on_close()`, and repeated `cli_trans()` calls. FSCTLs include `FSCTL_SET_SPARSE`, `FSCTL_CREATE_OR_GET_OBJECT_ID`, `FSCTL_GET_REPARSE_POINT`, `FSCTL_SET_REPARSE_POINT`, `FSCTL_GET_SHADOW_COPY_DATA`, `FSCTL_FIND_FILES_BY_SID`, `FSCTL_QUERY_ALLOCATED_RANGES`, and `FSCTL_IS_VOLUME_DIRTY`.

Control flow: After creating `fsctltest`, the test fills the NT transaction setup array with the FSCTL code, fnum, and ioctl marker, then sends data/parameter buffers sized to trigger expected behavior. It frees returned data buffers after object-id and range queries. Each FSCTL has a hard-coded expected NTSTATUS: OK for sparse, object id, allocated ranges; not-a-reparse-point, invalid-buffer-size, or invalid-parameter for others.

State/persistence behavior: Remote state is a temporary file marked delete-on-close. Some FSCTLs can alter file metadata, notably sparse state and object id creation. Returned buffers are talloc-owned and freed locally.

Dependencies and integration points: It depends on SMB1 NT transaction support, FSCTL constants, raw trans helpers, and security access masks. It is an integration test for server ioctl dispatch and status mapping.

Risks: Filesystem support affects FSCTL behavior, especially sparse files, object ids, shadow copies, and allocated ranges. SMB dialect or server feature differences can legitimately alter statuses. Several diagnostic strings mention the wrong FSCTL name after copy/paste, so status is more reliable than message text.

Test signals: Passing is a sequence of exact status checks for each FSCTL and successful cleanup through connection close. Any mismatch prints the actual status and expected status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_nttrans_fsctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_oplock_cancel.c -->
# sources/user-network-fs/samba/source3/torture/test_oplock_cancel.c

Purpose: This file tests cancellation of an SMB2/3 create request that is blocked by an oplock break. It verifies that canceling the create does not leave server state that prevents later cleanup and unlink.

Important APIs/types/functions: `create_cancel_send()` issues `cli_ntcreate_send()` and immediately calls `tevent_req_cancel()` on the subrequest. `create_cancel_done()` expects `cli_ntcreate_recv()` to return `NT_STATUS_CANCELLED`. `create_cancel()` wraps the async helper in a tevent poll. Public entrypoint is `run_oplock_cancel()`.

Control flow: The test opens two SMB connections with SMB1 disabled and oplocks enabled. `cli1` opens `oplock-cancel` for read, holding an oplock. `cli2` starts and cancels an open of the same file. After successful cancellation, `cli1` closes its handle and is freed, the test sleeps five seconds to let smbd instances communicate, and `cli2` unlinks the file.

State/persistence behavior: State includes a remote file, oplock state on the first connection, a canceled create request on the second connection, and delayed inter-smbd notification. The file is deleted at the end through `cli_unlink()`.

Dependencies and integration points: It depends on SMB2/3 client behavior (`CLI_FULL_CONNECTION_DISABLE_SMB1`), oplock support, async create cancellation, tevent NTSTATUS helpers, and Samba-specific smbd coordination. It tests a server behavior called out in comments as Samba-specific relative to Windows.

Risks: The comment says the test currently works only with SMB2/3 and Samba. The fixed five-second wait is timing-sensitive. If server cancel semantics change to ignore create cancel like Windows, the expected result may need revision.

Test signals: Passing requires the canceled create to complete as `NT_STATUS_CANCELLED`, no errors closing the original handle, and final unlink success after smbd coordination delay.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_oplock_cancel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_posix.c -->
# sources/user-network-fs/samba/source3/torture/test_posix.c

Purpose: This file is a large SMB1 Unix extensions/POSIX semantics torture suite focused on symlinks, POSIX listing/stat/readlink behavior, default ACL translation, symlink rename/chmod safety, and robustness of SMB1 path info calls against symlink paths.

Important APIs/types/functions: Shared helpers include `struct posix_test_entry`, `struct posix_test_state`, `posix_ls_fn()`, `posix_test_entries_reset()`, and `posix_test_entry_check()`. Public tests are `run_posix_ls_wildcard_test()`, `run_posix_ls_single_test()`, `run_posix_readlink_test()`, `run_posix_stat_test()`, `run_posix_symlink_parent_test()`, `run_posix_symlink_chmod_test()`, `run_posix_dir_default_acl_test()`, `run_posix_symlink_rename_test()`, `run_posix_symlink_getpathinfo_test()`, and `run_posix_symlink_setpathinfo_test()`. It uses `torture_setup_unix_extensions()`, `cli_posix_*` operations, `cli_list()`, `cli_readlink()`, `cli_chmod()`, `cli_query_security_descriptor()`, `cli_qpathinfo()`, `cli_setpathinfo()`, and raw trans2 helpers.

Control flow: The listing/readlink/stat tests create a real file and three symlinks: dangling, in-share, and outside-share. Windows-flavor listing should hide invalid/dangling or outside-share symlinks, while POSIX-flavor listing and stat/readlink should expose symlink metadata and target lengths. The symlink-parent test creates a directory symlink and then creates/removes files, dirs, symlinks, and hardlinks through that symlink. The chmod test confirms chmod on symlinks fails without disconnecting the server. The default ACL test creates a directory, verifies no inheritable Windows ACEs, sets a POSIX default ACL buffer, and expects inheritable ACE flags afterward. Rename tests ensure real-target and dangling symlinks can be renamed. Getpathinfo/setpathinfo tests iterate tables of SMB1 info levels against real-target and dangling symlink paths; most statuses are acceptable as long as the server does not disconnect.

State/persistence behavior: The tests create many remote files, directories, symlinks, hardlinks, and ACL changes, then attempt cleanup at each `out:` block. They require SMB1 Unix extensions and intentionally compare POSIX client behavior with Windows-style client behavior. ACL state is translated from POSIX ACL wire buffers into Windows security descriptors.

Dependencies and integration points: Dependencies include torture credentials/globals, SMB client setup and tree connect, Unix extension helpers, POSIX SMB calls from `libsmb/clirap.h`, security descriptor utilities, and trans2 level constants. The suite validates the interaction between Samba's POSIX extension layer, Windows-compatible views, and symlink safety paths.

Risks: SMB1 Unix extensions must be enabled; several tests are explicitly SMB1-only. Host filesystem symlink, hardlink, ACL, and path traversal policy can affect results. The getpathinfo/setpathinfo tests are crash-safety probes and accept many error statuses, so they detect disconnects more than semantic correctness.

Test signals: Passing requires expected visibility differences for symlinks, correct readlink/stat target sizes, successful operations under a symlinked parent, chmod failure without connection loss, default ACL producing inheritable ACE flags, symlink rename success, and no `NT_STATUS_CONNECTION_DISCONNECTED` across all path info level probes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_posix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_posix_append.c -->
# sources/user-network-fs/samba/source3/torture/test_posix_append.c

Purpose: This file is a regression test for Samba bug 6898: `GENERIC_WRITE` with POSIX semantics must not imply append-only write behavior.

Important APIs/types/functions: The single public entrypoint is `run_posix_append()`. It uses `torture_open_connection()`, `torture_setup_unix_extensions()`, `cli_ntcreate()`, `cli_writeall()`, and `cli_qfileinfo_basic()`. Access and create flags include `GENERIC_WRITE_ACCESS`, `GENERIC_READ_ACCESS`, `DELETE_ACCESS`, `FILE_FLAG_POSIX_SEMANTICS`, `FILE_OVERWRITE_IF`, `FILE_NON_DIRECTORY_FILE`, and `FILE_DELETE_ON_CLOSE`.

Control flow: The test opens file `append` with POSIX semantics and delete-on-close, writes one byte at offset zero twice, queries file size, and expects the final size to remain one byte. If the server incorrectly treats the handle as append-only, the second write extends the file to two bytes and the test fails.

State/persistence behavior: The remote file is temporary and marked delete-on-close. Persistent state is limited to file contents and size during the open handle lifetime. The test closes the connection in cleanup.

Dependencies and integration points: It depends on SMB Unix extension setup, SMB create/write/query APIs, and POSIX semantics flag handling in smbd. It is a focused protocol regression test.

Risks: Requires Unix extensions and server support for POSIX semantics. If write coalescing or file-size query behavior changes, the size assertion is the key contract. Failure leaves a delete-on-close file only if close/connection teardown also fails.

Test signals: Passing requires both writes at offset zero to succeed and `cli_qfileinfo_basic()` to report size `sizeof(c)`, not two bytes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_posix_append.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_pthreadpool_tevent.c -->
# sources/user-network-fs/samba/source3/torture/test_pthreadpool_tevent.c

Purpose: This file tests integration between Samba's pthread pool wrapper and tevent request polling. It submits one background job and verifies completion through the tevent-facing API.

Important APIs/types/functions: `run_pthreadpool_tevent()` creates a poll-backed tevent context, initializes a `pthreadpool_tevent` with pool size 100, submits `job_fn()` through `pthreadpool_tevent_job_send()`, polls the request, receives it with `pthreadpool_tevent_job_recv()`, and frees the pool/context. `job_fn()` writes `4711` to the provided integer and calls `poll(NULL, 0, 100)` to simulate work.

Control flow: The entrypoint initializes event and pool state, sets `val = -1`, submits the job, blocks with `tevent_req_poll()`, checks the receive return code, prints the final value, and returns true on success.

State/persistence behavior: State is entirely in memory: tevent context, thread pool object, tevent request, and an integer passed by pointer to the worker. There is no persistent file or network state. The worker mutates caller-owned stack state, so completion ordering is essential before reading `val`.

Dependencies and integration points: It depends on `lib/pthreadpool/pthreadpool_tevent.h`, `system/select.h`, POSIX `poll()`, and tevent. It validates that asynchronous thread-pool jobs can be driven from Samba's event loop.

Risks: Thread creation or pool initialization can fail under resource limits. The test does not assert the printed value directly after receive, so a future bug that returns success without running the job would only be visible in output unless additional checking is added.

Test signals: Passing requires successful tevent context creation, pool initialization, job send, event polling, and zero return from `pthreadpool_tevent_job_recv()`. The diagnostic value should print `4711`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_pthreadpool_tevent.c -->
