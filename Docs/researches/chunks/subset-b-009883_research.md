# sources/user-network-fs/samba/source3/torture/torture.c lines 10422-16777

## Scope

This chunk covers the tail of Samba's legacy `source3/torture/torture.c` SMB torture client. The requested range begins inside the end of `run_dirtest1()` and continues through many SMB1/SMB2/LDAP/POSIX/local utility test implementations, the `torture_ops[]` test registry, the `run_test()` dispatcher, `usage()`, and `main()`.

The file is a standalone command-line test harness for `smbtorture //server/share [options] TEST...`. The closing registry in this chunk wires tests defined earlier in the file together with tests defined in this range, so this slice is both implementation code and the main integration surface for the whole legacy binary.

## Purpose

The code in this range adds regression, stress, protocol-edge, and local-library tests to the legacy SMB torture executable. The network-facing tests exercise SMB1 and SMB2 client behavior, server error mapping, directory notifications, name mangling, POSIX extension interoperability, DFS attributes, large SMB1 reads, alternate data stream errors, session handling, and malformed SMB1 message paths. The local tests exercise Samba utility libraries without requiring a share, including substitution formatting, base64, gencache, rb-tree dbwrap, charset conversion, SID parsing/formatting, NTFS stream-name parsing, memcache, winbind client request fan-out, dbwrap transactions, tevent poll setup, hex encoding, duplicate-address removal, TDB stress loops, and path canonicalization.

The final harness code lets a user select individual tests by name or run `ALL`, applies global options such as username/password, workgroup, protocol cap, socket options, concurrency, encryption, and target filename, then returns process success or failure from the aggregate test result.

## Important APIs, Types, And Functions

Core Samba client APIs used across the network tests include `torture_open_connection()`, `torture_open_connection_flags()`, `open_nbt_connection()`, `torture_close_connection()`, `cli_ntcreate()`, `cli_openx()`, `cli_close()`, `cli_unlink()`, `cli_rmdir()`, `cli_mkdir()`, `cli_list()`, `cli_qpathinfo*()`, `cli_writeall()`, `cli_read()`, `cli_session_setup_creds()`, `cli_ulogoff()`, `cli_tree_connect()`, `smbXcli_negprot()`, `smbXcli_conn_create()`, `smb1cli_req_send()`, and `tevent_req_poll_ntstatus()`.

Important asynchronous request state types in this slice:

- `struct torture_createdel_state` and `torture_createdel_send()/recv()` create a file with `FILE_DELETE_ON_CLOSE`, then close it.
- `struct torture_createdels_state` and `torture_createdels_send()/recv()` keep a bounded pipeline of create/delete operations in flight for notification benchmarks.
- `struct swallow_notify_state` and `swallow_notify_send()` issue `cli_notify_send()` repeatedly and call a user callback for each returned `notify_change`.
- `struct pidtest_state` and `pid_echo_send()/recv()` send an SMB1 echo with an explicit 32-bit PID and validate the returned low/high PID header fields.
- `struct session_setup_nt1_truncated_state` and `smb1_session_setup_nt1_truncated_send()/recv()` manually craft a truncated SMB1 NT1 session setup request.
- `struct smb1_negotiate_exit_state` and `smb1_negotiate_exit_send()/recv()` manually send an SMB1 `SMBexit` request after negotiation.

Important network test functions defined in this range:

- `run_error_map_extract()` compares NT-status and DOS-error session setup failures by deliberately using usernames derived from NT status codes.
- `run_sesssetup_bench()` repeatedly performs session setup and logoff on one connection.
- `run_chain1()` and `run_chain2()` submit chained SMB1 requests for open/write/close and guest session setup/tree connect.
- `run_notify_bench()` combines repeated notify reads with parallel create/delete operations, optionally across multiple UNC targets from `-b`.
- `run_mangle1()` and `run_mangle_illegal()` validate short-name access and illegal-character POSIX-created file handling through Windows-style SMB names.
- `run_windows_write()` writes sparse-style blocks by writing the last byte first and pushing zero-filled data.
- `run_large_readx()` verifies SMB1 `CAP_LARGE_READX` reply sizes under normal and signing-required NT1 sessions.
- `run_msdfs_attribute()` checks that a named DFS link appears as both directory and reparse point.
- `run_cli_echo()` and `run_cli_splice()` test SMB echo and server-side/client-assisted copy semantics.
- `run_uid_regression_test()` checks bad UID/TID behavior after logoff and tree disconnect.
- `run_shortname_test()` verifies when short names should and should not be created for special characters.
- `run_tldap()` connects to LDAP/LDAPS/StartTLS as configured, performs SASL/GENSEC bind, paged search, complex-filter search, and extended-DN GUID formatting checks.
- `run_dir_createtime()` verifies directory create time and inode-return behavior across SMB1 and SMB2.
- `run_streamerror()` checks errors for querying and opening a stream on a directory.
- `run_pidhigh()` checks SMB1 PID high/low round-trip handling.
- `run_symlink_open_test()` verifies Windows open of a dangling POSIX symlink returns not-found errors instead of hanging.
- `run_smb1_wild_mangle_unlink_test()` and `run_smb1_wild_mangle_rename_test()` guard against wildcard/mangled-name operations touching the wrong POSIX-created file.
- `run_smb1_truncated_sesssetup()`, `run_smb1_negotiate_exit()`, `run_smb1_negotiate_tcon()`, and `run_ign_bad_negprot()` hand-build low-level SMB1 sequences for malformed or unusual negotiation/session/tree paths.

Important local test functions defined in this range:

- `run_local_substitute()` and `timesubst_test()` check `%` substitution and UTC time formatting.
- `run_local_base64()` round-trips random blobs from length 1 through 1999.
- `run_local_gencache()` checks string and blob cache set/get/delete behavior and type safety.
- `run_local_rbtree()` checks `db_open_rbt()` record store flags, updates, traversal, and deletion.
- `run_local_convert_string()` verifies `convert_string_error()` length and NUL-conversion behavior.
- `run_local_string_to_sid()`, `run_local_sid_to_string()`, and `run_local_binary_to_sid()` check SID parser rejection, formatting, and binary bounds.
- `split_ntfs_stream_name()`, `test_stream_name()`, and `run_local_stream_name()` specify the local canonicalization rules for NTFS stream names and `$DATA`.
- `run_local_memcache()` checks replacement, purge accounting, talloc ownership transfer, and leak-sensitive overwrite paths.
- `run_wbclient_multi_ping()` sends many asynchronous `WINBINDD_PING` requests across `torture_nprocs` winbind contexts.
- `run_local_dbtrans()` repeatedly increments a dbwrap record inside transactions in `transtest.tdb`.
- `run_local_tevent_poll()`, `run_local_hex_encode_buf()`, `run_local_remove_duplicate_addrs2()`, `run_local_tdb_opener()`, `run_local_tdb_writer()`, and `run_local_canonicalize_path()` cover focused utility behavior and stress loops.

The registry and harness use:

- `#define FLAG_MULTIPROC 1` to mark tests that should run through `create_procs()`.
- `torture_ops[]`, a name/function/flags table ending in `{ .name = NULL }`.
- `run_test()` to resolve a requested test name, run one test or recurse over all tests for `ALL`, time each run, and report failures.
- `main()` to parse the target UNC, options, credentials, and selected test names.

## Control Flow

Most individual tests follow the same pattern: open one or more `cli_state` connections, set socket options, clean any test paths from previous runs, create or query server state, assert exact `NTSTATUS` results or returned metadata, clean up files/directories, and close connections. Failure paths usually print a diagnostic and return `false`; many functions jump to an `out:` label so cleanup still runs.

The asynchronous notify/create-delete benchmark has a nested tevent flow. `run_notify_bench()` opens a directory, starts a repeating `swallow_notify_send()` request, starts `torture_createdels_send()` with ten parallel create/delete operations, and spins `tevent_loop_once()` until every configured share finishes. `torture_createdels_done()` keeps the pipeline full by replacing each completed subrequest with a new file name until the requested operation count is reached.

The large-read test creates a 20 MiB file, then runs two NT1 read scenarios: ordinary signing-if-required and signing-required. It negotiates a fresh connection for each scenario, optionally enables encryption or Unix extensions, opens the file read-only, and checks several request sizes through `check_read_call()`. `calc_expected_return()` constrains expected bytes by Unix large-read capability, signing, encryption, and SMB1 PDU overhead.

The LDAP test computes transport and GENSEC features from `client ldap sasl wrapping`, resolves the host, optionally upgrades to TLS or StartTLS, fetches RootDSE, binds with `torture_creds`, performs an asynchronous paged search, then validates complex search-filter parsing and extended-DN GUID formatting for control values absent, zero, and one.

The malformed SMB1 tests bypass high-level `cli_state` setup where needed. They resolve the host, open a raw TCP socket to port 445, wrap it in an `smbXcli_transport`, build an `smbXcli_conn`, negotiate a specific dialect, and send handcrafted SMB1 requests using `smb1cli_req_send()` or `smb1cli_session_setup_nt1_send()`.

At the harness level, `main()` initializes logging, locale, fault handling, loadparm state, interfaces, host/share parsing, defaults, and credentials. It parses options with `getopt()`, prompts for a password unless Kerberos or `-U user%pass` supplied one, initializes `torture_creds`, then calls `run_test("ALL")` or `run_test()` for each requested test argument. `run_test()` dispatches through `torture_ops[]`; tests marked `FLAG_MULTIPROC` run through `create_procs()`, which forks `torture_nprocs` children, synchronizes startup through anonymous shared memory, and aggregates child boolean results.

## State And Persistence Behavior

Network tests create transient files and directories on the selected SMB share. Examples include `\\notify-bench`, `\\MANGLE_ILLEGAL`, `\\writetest.txt`, `\\large_readx.dat`, `\\splice_src.dat`, `\\splice_dst.dat`, `\\uid_reg_test`, `\\shortname`, `\\testdir_createtime`, `\\testdir_streamerror`, `dangling_symlink`, and several SMB1 wildcard-mangle directories. Most tests explicitly unlink, remove directories, or call `torture_deltree()` before and after execution.

Some tests intentionally alter connection/session state: `run_sesssetup_bench()` repeatedly changes UID via session setup/logoff; `run_uid_regression_test()` mutates saved UID/TID values to check bad session behavior; `run_chain1()` and `run_chain2()` submit dependent SMB1 requests in a single chain; raw SMB1 tests leave normal `cli_state` flows and manage lower-level `smbXcli_conn` objects directly.

Local tests persist or mutate process-local and filesystem state. `run_local_gencache()` installs a global memcache via `memcache_set_global()`. `run_local_dbtrans()` creates and repeatedly updates `transtest.tdb`. `run_local_tdb_opener()` and `run_local_tdb_writer()` loop forever against `test.tdb` by design, making them stress/debug tests rather than normal finite regression checks. `timesubst_test()` temporarily sets `TZ=UTC` and restores the original timezone only when one was present.

Global harness variables configured in `main()` and earlier file scope affect this range: `host`, `share`, `username`, `password`, `workgroup`, `myname`, `sockops`, `torture_numops`, `torture_nprocs`, `torture_blocksize`, `test_filename`, `use_kerberos`, `do_encrypt`, `use_multishare_conn`, `multishare_conn_fname`, `signing_state`, and `torture_creds`.

## Dependencies And Integration Points

This chunk integrates with several Samba subsystems:

- SMB client libraries: `cli_state`, SMB1 request builders, SMB2-capable open/query helpers, signing/encryption state, transport creation, dialect negotiation, and tree/session helpers.
- POSIX extension client APIs: `torture_setup_unix_extensions()`, `cli_posix_open()`, `cli_posix_unlink()`, `cli_posix_symlink()`, and `cli_posix_mkdir()`.
- Event and async infrastructure: `tevent_context`, `tevent_req`, callback-data helpers, request polling, and loops.
- LDAP stack: `tldap_context`, RootDSE fetch, paged search, controls, TLS tstreams, StartTLS, and GENSEC SASL wrapping.
- Samba utility libraries: talloc, DATA_BLOB, base64, gencache, memcache, dbwrap, TDB, rb-tree DB, SID parsing/formatting, charset conversion, address de-duplication, path canonicalization, and time formatting.
- Winbind client stack: `wb_context`, `wb_trans_send()`, `wb_trans_recv()`, and `WINBINDD_PING`.
- Loadparm and runtime configuration: `loadparm_init_s3()`, `lp_load_global()`, `lpcfg_set_cmdline()`, `lpcfg_set_option()`, `lp_client_smb_transports()`, `lp_workgroup()`, and `SMB_CONF_PATH`.

The test table also references many functions defined outside this exact line range, including locking, oplock, POSIX ACL, SMB2, DFS, cleanup, messaging, g-lock, idmap, quota, path, and RPC-scale tests. The table is therefore the central integration point for the whole file, not only for functions defined in this chunk.

## Risks And Maintenance Notes

- The file is explicitly legacy: `usage()` warns that the Samba4 torture suite is more complete. New coverage may belong in the modern torture suite unless this exact source3 client path is required.
- Many tests are environment-sensitive. They depend on server dialect support, SMB1 availability, POSIX extensions, DFS links, LDAP/LDAPS configuration, credentials, winbind availability, signing/encryption policy, and share filesystem semantics.
- Several tests assume clean share paths and can fail if previous runs left files behind, cleanup failed due to permissions, or parallel users share the same target.
- SMB1-specific tests can fail or be inapplicable when SMB1 is disabled, when port 445 is blocked, or when a server rejects old dialects before the intended edge case.
- `run_large_readx()` has subtle expected-size logic around large-read capability, signing, encryption, and Windows server behavior. Changes to client buffer constants or SMB1 signing/encryption behavior can produce false regressions if the expected PDU math is not updated.
- Name-mangling tests depend on POSIX-created names that are illegal or wildcard-like from a Windows SMB perspective. A bug here can delete or rename the wrong file, so cleanup paths and test directories need to stay tightly scoped.
- `run_local_dbtrans()`, `run_local_tdb_opener()`, and `run_local_tdb_writer()` are unbounded loops in normal success flow. They should be invoked intentionally, usually under supervision or a timeout.
- `run_wbclient_multi_ping()` passes `&i` as callback data while also using `i` as loop and completion counter. This is intentional in the current code path but is easy to misread and fragile if the surrounding loop structure changes.
- `timesubst_test()` restores `TZ` only if it was originally present; if no `TZ` existed, the process remains with `TZ=UTC` for later tests in the same run.
- `create_procs()` forks children that open connections and run test functions. Tests used with `FLAG_MULTIPROC` must tolerate concurrent access to the same share and global path patterns.

## Test Signals

The primary test signal is the `smbtorture` process exit code: `main()` returns `0` only if every selected `run_test()` call returns true. For individual tests, useful positive signals are exact `NTSTATUS` matches, no unexpected diagnostics, cleanup completion, and the printed timing line `<TEST> took <secs> secs`.

Representative targeted invocations from this chunk include:

```sh
smbtorture //server/share -U user%pass DIR1
smbtorture //server/share -U user%pass SESSSETUP_BENCH
smbtorture //server/share -U user%pass CHAIN1 CHAIN2
smbtorture //server/share -U user%pass NOTIFY-BENCH
smbtorture //server/share -U user%pass MANGLE1 MANGLE-ILLEGAL
smbtorture //server/share -U user%pass LARGE_READX
smbtorture //server/share -U user%pass SMB1-TRUNCATED-SESSSETUP SMB1-NEGOTIATE-EXIT
smbtorture //server/share LOCAL-SUBSTITUTE LOCAL-BASE64 LOCAL-RBTREE LOCAL-MEMCACHE LOCAL-CANONICALIZE-PATH
```

Expected focused assertions include:

- `DIR1` sees the expected directory listing counts for wildcard and must-have attribute filters.
- `LARGE_READX` prints success only after all requested read lengths return the calculated or Windows-capped sizes.
- `MSDFS-ATTRIBUTE` requires `-f` to name a DFS link and expects `FILE_ATTRIBUTE_REPARSE_POINT` plus `FILE_ATTRIBUTE_DIRECTORY`.
- `WINDOWS-BAD-SYMLINK` accepts only `NT_STATUS_OBJECT_NAME_NOT_FOUND` or `NT_STATUS_OBJECT_PATH_NOT_FOUND`.
- `SMB1-WILD-MANGLE-UNLINK` and `SMB1-WILD-MANGLE-RENAME` verify the non-wildcard sibling remains present after Windows operations on a mangled wildcard-like name.
- `PIDHIGH` requires the returned SMB1 header PID low/high fields to be `0xBEEF` and `0xDEAD`.
- Local SID tests reject malformed SIDs and round-trip accepted strings exactly.
- Local stream-name tests define accepted forms such as `bla`, `bla::$DATA`, `bla:$DATA`, `bla:x:$DATA`, and `bla:x`, and reject invalid explicit stream types.

For build or harness validation, the important structural signal is that every `torture_ops[]` entry has a non-NULL function pointer until the sentinel and that `usage()` lists the same names that `run_test()` can dispatch.
