# subset-b-009902 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/client/cifsddio.c -->
# sources/user-network-fs/samba/source4/client/cifsddio.c

## Purpose
Implements the concrete I/O backends for Samba's `cifsdd` utility: POSIX file descriptor access, SMB/CIFS file access, and the block-buffer fill/flush helpers used by the dd-style copy loop. The file turns local paths or UNC paths into a common `struct dd_iohandle` with `io_read`, `io_write`, and `io_seek` callbacks.

## Important APIs, types, and functions
- `struct fd_handle` embeds `struct dd_iohandle` and stores a local `fd`; `IO_HANDLE_TO_FD()` relies on the embedded handle being at offset zero.
- `struct cifs_handle` embeds `struct dd_iohandle`, owns an `smbcli_state`, an SMB file number, and a logical offset.
- `open_fd_handle()` opens local files with `O_DIRECT` and `O_SYNC` when requested by `DD_DIRECT_IO` and `DD_SYNC_IO`, and with read or write/create flags from `DD_WRITE`.
- `init_smb_session()` calls `smbcli_full_connection()` with global command-line credentials, loadparm context, resolver, tevent context, SMB options, session options, and GENSEC settings.
- `open_smb_file()` issues `RAW_OPEN_NTCREATEX`, maps cifsdd options into access, create disposition, write-through/no-buffering flags, share access, and optional oplock request.
- `dd_open_path()` chooses local I/O if `file_exist(path)` is true, otherwise parses UNC paths with `smbcli_parse_unc()` and opens SMB, falling back to local open for non-UNC paths.
- `dd_fill_block()` and `dd_flush_block()` implement the copy buffer contract and update global `dd_stats`.

## Control flow
Local reads/writes call `read()`/`write()` once per requested block and return the actual byte count. SMB reads/writes build raw READX/WRITEX unions and maintain the current offset in `struct cifs_handle`; `smb_seek_func()` only updates that cached offset. Opening a CIFS path first creates a session, then opens the remote file, then returns the embedded generic handle.

The buffering helpers are higher-level. `dd_fill_block()` keeps appending `block_size` reads until the caller's buffer has `need_size` bytes or reaches EOF. `dd_flush_block()` writes either a requested partial block or as many full blocks as fit, counts full/partial output blocks, and moves any remainder to the start of the buffer for the next copy iteration.

## State and persistence behavior
Persistent external state is limited to local files and remote SMB files. In-memory state includes file descriptors, SMB session handles, SMB fnums, offsets, `DD_END_OF_FILE` in the handle flags, and global `dd_stats`. There is no close/destructor path in this file, so ownership and cleanup are expected from surrounding cifsdd code or process teardown.

## Dependencies and integration points
The file depends on Samba's `libcli` raw SMB client, command-line credential/loadparm globals, resolver and tevent contexts, and definitions from `cifsdd.h` such as `dd_iohandle`, `DD_*` flags, `PROGNAME`, and `dd_stats`. It integrates with `cifsdd.c` as the device abstraction layer and with `test_cifsdd.sh` for blackbox local/remote copy coverage.

## Risks and edge cases
- `dd_open_path()` treats any existing local path as local even if the string resembles a UNC path, and missing local paths that are not UNC are opened as local, which may surprise callers.
- `open_cifs_handle()` logs a missing share-relative path but does not immediately return after the error message.
- SMB offset advancement asserts against integer wrap for reads but not writes.
- `open_smb_file()` returns `-1` on failure, but `open_cifs_handle()` still returns a handle with that fnum; later I/O will fail rather than open failing atomically.
- The direct-I/O block-size alignment requirements are delegated to the caller and platform.

## Test signals
`test_cifsdd.sh` exercises local-to-local, local-to-remote, remote-to-local, and remote-to-remote copies over block sizes `512`, `4k`, and `48k`, then validates with `cmp`. That gives broad blackbox coverage of the path selection and fill/flush behavior, but not explicit error handling, partial writes, direct/sync I/O, oplocks, or invalid UNC handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/client/cifsddio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/client/client.c -->
# sources/user-network-fs/samba/source4/client/client.c

## Purpose
Implements the Samba4 `smbclient` command-line program. It supports interactive and scripted SMB file operations, share enumeration, NetBIOS message sending, file metadata inspection, LSA name/SID/privilege calls, readline completion, and legacy protocol compatibility options.

## Important APIs, types, and functions
- `struct smbclient_context` stores remote current directory, `smbcli_state`, filename mask, newer-than filter, prompt/recurse/lowercase/translation flags, archive handling, print mode, and I/O buffer size.
- `do_connect()` parses UNC service names, initializes `remote_cur_dir`, stores the global readline context, and calls `smbcli_full_connection()`.
- `commands[]` maps command names, handlers, help strings, and completion hints; `process_tok()` allows unambiguous abbreviations.
- File transfer APIs include `do_get()`, `do_put()`, `cmd_get()`, `cmd_put()`, `cmd_mget()`, `cmd_mput()`, `cmd_reget()`, and `cmd_reput()`.
- Directory and listing logic centers on `do_list()`, `do_list_helper()`, the global NUL-separated `do_list_queue`, `cmd_dir()`, and `cmd_du()`.
- Metadata and administration commands include `cmd_fsinfo()`, `cmd_allinfo()`, `cmd_eainfo()`, `cmd_acl()`, `cmd_lookup()`, and privilege add/delete/list handlers.
- UNIX extension commands include `cmd_link()`, `cmd_symlink()`, `cmd_chmod()`, and `cmd_chown()`, guarded by `CAP_UNIX`.
- Entry points are `main()`, `process_command_string()`, and `process_stdin()`.

## Control flow
`main()` initializes talloc, command-line parsing, Samba config and credentials, SMB options, GENSEC, and tevent. It then follows one of three paths: `-L` share query through `do_host_query()`, `-M` message sending through `do_message_op()`, or normal service connection through `do_connect()`. After connecting it optionally changes the starting remote directory, then runs `-c` semicolon-separated commands or the readline loop.

Interactive command processing tokenizes shell-like arguments with `str_list_make_shell()`, resolves abbreviations through `commands[]`, and invokes command handlers. Recursive remote listing uses a process-global queue rather than call-stack recursion. CNAME-like command aliasing is done by multiple table rows, for example `ls` uses `cmd_dir()` and `rm` uses `cmd_del()`.

## State and persistence behavior
The program persists remote filesystem changes through SMB create, write, unlink, mkdir/rmdir, rename, NT create/open/close, ACL/info queries, UNIX extension calls, and LSA RPC calls. Local persistence includes downloaded files, temporary pager files, local cwd changes via `lcd`, local recursive scans for `mput`, environment-driven password lookup, and shell execution through `!`. In-memory state is mostly in `smbclient_context`, but listing, completion, readline keepalive, transfer totals, and directory totals use file-scope globals.

## Dependencies and integration points
This file integrates Samba's raw SMB client, srvsvc DCERPC share enumeration, LSA helpers, NDR-generated structures, readline wrapper, resolver, GENSEC, loadparm, and credential command-line support. `test_smbclient.sh` blackbox-tests many commands. It also exercises legacy protocol negotiation via `-m LANMAN1` and `-m LANMAN2`.

## Risks and edge cases
- Several helpers use process-global state (`rl_ctx`, listing queue globals, totals), so concurrent or reentrant use is not supported.
- Some talloc usage is legacy by design (`TALLOC_DEPRECATED`, `talloc_append_string(NULL, ...)`) and may leak until process exit.
- `cmd_mget()` appears to build a mask from `remote_cur_dir`, then immediately replaces it with `args[i]`; path handling deserves regression tests.
- `cmd_reput()` builds `local_name` using the remote current directory prefix, which looks suspicious for a local-file operation.
- Shell escape (`!`) intentionally executes local commands from interactive input.
- Error returns are inconsistent: many commands print and return success even when individual SMB operations fail.
- Raw string manipulation of DOS paths, recursion, and local path trimming is fragile around unusual names.

## Test signals
`test_smbclient.sh` covers listing with authentication and anonymous mode, `mput`/`mget`/`put`/`get`, alternate names, `allinfo`, EA info, mkdir/cd/rmdir/rename/deltree, many `fsinfo` levels, SID/name lookup, old protocol listings, `pwd`, and credential sources (`--authentication-file`, `PASSWD_FILE`, `PASSWD`, `USER`). Gaps include readline completion, shell escape, ACL/privilege mutation, UNIX extensions, recursive transfer edge cases, message mode, and many failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/client/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/client/http_test.c -->
# sources/user-network-fs/samba/source4/client/http_test.c

## Purpose
Provides a small Samba HTTP client test utility. It connects to an HTTP or HTTPS endpoint, optionally uses Basic auth from Samba credentials, sends a POST request to a configurable URI, reads a bounded response, and prints the response body.

## Important APIs, types, and functions
- `struct http_client_info` stores connection, port/address, TLS params, credentials, loadparm context, and URI.
- `send_http_request()` builds an `HTTP_REQ_POST`, adds `User-Agent` and `Accept` headers, calls `http_send_auth_request_send()` with `HTTP_AUTH_BASIC`, then reads the response with `http_read_response_send()`.
- `main()` parses `--usetls`, `--ip-address`, `--port`, `--cacart`, `--uri`, and `--rsize` plus common Samba and credential options.

## Control flow
The program initializes talloc and Samba command-line config, sets defaults (`localhost`, `/_search?pretty`, port `8080`, response size about 8 MiB), configures credentials, creates a tevent context, then retries the connection up to four times. With TLS enabled, it creates client TLS parameters from the CA certificate before `http_connect_send()`. After a successful connection, it sends one request and returns success only for HTTP status 200 with a non-empty body.

## State and persistence behavior
The utility is stateless beyond its process memory and network connection. It may allocate a copy of non-anonymous credentials. It prints response bodies to stdout and debug/errors through Samba logging macros. No files are written except any implicit TLS/config access from Samba libraries.

## Dependencies and integration points
Uses Samba HTTP client APIs, tevent polling helpers, TLS helper APIs, command-line credentials, and loadparm. It is likely intended for blackbox or manual testing of Samba services exposing HTTP endpoints.

## Risks and edge cases
- The option is named `--cacart` in code and help text, likely a typo for `--cacert`; scripts must use the implemented spelling.
- TLS requires a CA file and does not use system CAs in this code path.
- Connection polling lacks an explicit timeout around `http_connect_send()`, while request and response operations use 10-second endtimes.
- It hardcodes POST with an empty body, so it is not a general HTTP client.
- It treats non-200 and zero-length responses as failures after printing diagnostic text.

## Test signals
No direct test script is in this subset. Useful tests would cover anonymous and credentialed Basic auth, TLS CA validation, retry behavior on initial connection failure, response-size limits, non-200 status handling, and the `--uri`/`--rsize` options.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/client/http_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/client/tests/test_cifsdd.sh -->
# sources/user-network-fs/samba/source4/client/tests/test_cifsdd.sh

## Purpose
Blackbox test script for `cifsdd`, validating that the utility can copy data through local and SMB-backed inputs/outputs without content changes.

## Important APIs, types, and functions
- Sources `testprogs/blackbox/subunit.sh` for `testit` reporting.
- `runcopy()` invokes `$BINDIR/cifsdd` with Samba config, debug level, domain, username, and password.
- `compare()` wraps `cmp` under subunit.

## Control flow
The script requires `SERVER USERNAME PASSWORD DOMAIN`. It creates a temporary source file in `$SELFTEST_TMPDIR` using `dd if=$DD` with 50 KiB of data, then loops over block sizes `512`, `4k`, and `48k`. For each block size it tests local-to-local, local-to-remote then remote-to-local, and remote-to-remote then remote-to-local, comparing the final destination with the source after each scenario.

## State and persistence behavior
Creates local temp files named with `$$` under `SELFTEST_TMPDIR` and remote files in the `tmp` share. It removes local temp files at the end but does not explicitly delete the remote temp files.

## Dependencies and integration points
Depends on a working Samba selftest environment, `$BINDIR/cifsdd`, `$CONFIGURATION`, optional `$VALGRIND`, credentials accepted by `//$SERVER/tmp`, and `/bin/dd`/`cmp`.

## Risks and edge cases
- Remote files are not cleaned up, which can leave state behind across failures or repeated runs.
- The source data comes from the `cifsdd` binary, not random or sparse data.
- It does not test direct I/O, sync I/O, invalid UNC paths, short writes, EOF corner cases, or permission failures.

## Test signals
Strong signal for normal copy integrity across local and SMB I/O paths at three block sizes. It is especially relevant to `cifsddio.c` buffer and path backend behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/client/tests/test_cifsdd.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/client/tests/test_smbclient.sh -->
# sources/user-network-fs/samba/source4/client/tests/test_smbclient.sh

## Purpose
Blackbox test script for Samba4 `smbclient`, covering share enumeration, common file operations, metadata queries, protocol compatibility, and credential source behavior.

## Important APIs, types, and functions
- Uses `testit` from `testprogs/blackbox/subunit.sh`.
- `runcmd()` executes `$smbclient //$SERVER/tmp -c "$cmd"` with config, domain, and credentials, then emits simple success/failure markers.
- Direct `testit` calls cover share listing and credential-source variants.

## Control flow
After argument parsing, the script lists shares authenticated and anonymously, copies the `smbclient` binary into `$PREFIX/tmpfile`, and uses it as test data. It runs `mput`, `altname`, `allinfo`, `mget`, `rm`, `mkdir`, `cd`, `rmdir`, nested directory creation/removal, `rename`, `deltree`, a series of `fsinfo` levels, `put`, `get`, `eainfo`, renamed put/get, SID/name lookup, LANMAN1/LANMAN2 listing, `pwd`, and several credential sourcing tests.

## State and persistence behavior
Creates and deletes files in `$PREFIX` and in the remote `tmp` share. It writes temporary authentication and password files under `$PREFIX`, exports `PASSWD_FILE`, `PASSWD`, and `USER` for parts of the run, then cleans the local files and restores variables.

## Dependencies and integration points
Requires a built `smbclient`, Samba selftest config, credentials, writable `tmp` share, old protocol support for LANMAN checks, and local `diff`. It directly exercises many handlers in `client.c`.

## Risks and edge cases
- `runcmd()` manually prints `test:`/`success:`/`failure:` rather than using `testit`, which may provide weaker subunit structure for those cases.
- It assumes old dialects and NTLM option combinations remain supported in the test environment.
- It does not validate command output content for metadata calls, only command success.
- Privilege tests are commented out, and ACL, UNIX extensions, recursion prompts, shell escape, and message mode are not covered.

## Test signals
Provides broad smoke coverage for normal `smbclient` workflows and credential plumbing. Failures here point at command dispatch, connection setup, transfer integrity, remote filesystem commands, or authentication regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/client/tests/test_smbclient.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/cluster/cluster.c -->
# sources/user-network-fs/samba/source4/cluster/cluster.c

## Purpose
Implements the public cluster abstraction dispatch layer. It forwards cluster ID creation, temporary database opening, backend handle access, and inter-node messaging calls to the currently installed `cluster_ops` backend, defaulting to local non-cluster operations.

## Important APIs, types, and functions
- File-scope `static struct cluster_ops *ops` stores the active backend.
- `cluster_set_ops()` installs a backend.
- `cluster_init()` lazily installs the local backend by calling `cluster_local_init()` if no backend exists.
- `cluster_backend_handle()`, `cluster_id()`, `cluster_db_tmp_open()`, `cluster_message_init()`, and `cluster_message_send()` are public wrappers.

## Control flow
Most public calls first ensure initialization, then call the corresponding function pointer. `cluster_backend_handle()` is the exception: it dereferences `ops` directly and assumes a backend was already installed.

## State and persistence behavior
The only state is the process-global backend pointer. Persistence is delegated to the backend, particularly temporary DB creation through `cluster_db_tmp_open()`. Messaging behavior is entirely backend-defined.

## Dependencies and integration points
Depends on `cluster.h`, `cluster_private.h`, generated server ID types, and the local backend from `local.c`. Other Samba subsystems use this file to avoid hard-coding CTDB/local differences.

## Risks and edge cases
- `cluster_backend_handle()` can crash if called before any other cluster API initializes `ops`.
- No locking protects backend installation, so dynamic backend changes are process-global and not thread-safe.
- Function pointer contracts are trusted; invalid backend structs will crash callers.

## Test signals
No direct tests are in this subset. Useful coverage would verify default local initialization, custom backend installation, and the pre-init behavior of `cluster_backend_handle()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/cluster/cluster.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/cluster/cluster.h -->
# sources/user-network-fs/samba/source4/cluster/cluster.h

## Purpose
Public header for the source4 cluster abstraction. It defines equality macros for cluster-aware server identifiers, declares the message callback type, and exposes the public cluster wrapper APIs.

## Important APIs, types, and functions
- `cluster_id_equal(id_1, id_2)` compares `pid`, `task_id`, and `vnn`.
- `cluster_node_equal(id1, id2)` compares only `vnn`.
- `cluster_message_fn_t` is a callback taking `struct imessaging_context *` and `DATA_BLOB`.
- Public prototypes include `cluster_id()`, `cluster_db_tmp_open()`, `cluster_backend_handle()`, `cluster_message_init()`, and `cluster_message_send()`.

## Control flow
This header has no runtime control flow, but its macros are evaluated inline and may evaluate arguments more than once if callers pass expressions with side effects.

## State and persistence behavior
No state is stored in the header. The APIs it declares can create cluster-aware server IDs, open temporary databases, and send/register messages through the active backend.

## Dependencies and integration points
Includes generated `server_id.h` and forward-declares `imessaging_context`. It is the stable public include used by cluster consumers.

## Risks and edge cases
- Equality macros compare only selected fields; `unique_id` is intentionally not part of equality here, which matters when mixing source3/server-id semantics.
- Macros do not guard NULL pointers.

## Test signals
Tests should confirm intended equality semantics, especially non-cluster IDs with `NONCLUSTER_VNN` and caller expectations around `unique_id`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/cluster/cluster.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/cluster/cluster_private.h -->
# sources/user-network-fs/samba/source4/cluster/cluster_private.h

## Purpose
Private header defining the backend vtable for the source4 cluster abstraction and private initialization hooks.

## Important APIs, types, and functions
- `struct cluster_ops` contains function pointers for server ID creation, temporary DB opening, backend handle retrieval, message endpoint initialization, message sending, and backend `private_data`.
- Private prototypes expose `cluster_set_ops()` and `cluster_local_init()` to backend implementations.

## Control flow
The header itself has no control flow. Runtime dispatch is performed by `cluster.c` through this vtable.

## State and persistence behavior
`private_data` lets a backend retain process-local state such as a CTDB context. Persistent database or messaging behavior is delegated to function pointers.

## Dependencies and integration points
Included by `cluster.c` and `local.c`; other real cluster backends can use the same contract to plug into Samba's cluster APIs.

## Risks and edge cases
- There is no versioning or size field on `cluster_ops`, so backend and caller must be compiled against the same contract.
- Function pointer signatures must match exactly; there are no runtime checks for missing methods.

## Test signals
Testing should use a fake backend to ensure every public wrapper calls the expected vtable slot and passes arguments unchanged.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/cluster/cluster_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/cluster/local.c -->
# sources/user-network-fs/samba/source4/cluster/local.c

## Purpose
Provides the default local/non-cluster backend for the cluster abstraction.

## Important APIs, types, and functions
- `local_id()` builds a `server_id` with caller-supplied `pid` and `task_id`, `NONCLUSTER_VNN`, and `SERVERID_UNIQUE_ID_NOT_TO_VERIFY`.
- `local_db_tmp_open()` builds a `.tdb` name under `smbd_tmp_path()`, computes configured hash size and TDB flags, and opens it with `dbwrap_local_open()`.
- `local_backend_handle()` returns `NULL`.
- `local_message_init()` succeeds without doing work.
- `local_message_send()` returns `NT_STATUS_INVALID_DEVICE_REQUEST`.
- `cluster_local_init()` installs `cluster_local_ops`.

## Control flow
The backend is a static `cluster_ops` table. Public calls from `cluster.c` land on these functions when no cluster backend overrides them.

## State and persistence behavior
There is no private backend state. Temporary DBs are real local TDB files under Samba's tmp path, opened with mode `0600`. Local messaging send is not supported by this backend.

## Dependencies and integration points
Uses dbwrap, system file flags, loadparm helpers, `smbd_tmp_path()`, and generated server ID constants. It is built into the private `cluster` library by `wscript_build`.

## Risks and edge cases
- `local_db_tmp_open()` allocates `dbname` on `mem_ctx` rather than `tmp_ctx`, so the constructed name lives longer than the path-building temporary context.
- Local message init returning success while send is unsupported can hide missing backend support until a send is attempted.
- The comment says “server a server_id”, a documentation typo only.

## Test signals
Tests should verify tmp DB path/flags integration, server ID fields, and that local messaging send fails predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/cluster/local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/cluster/wscript_build -->
# sources/user-network-fs/samba/source4/cluster/wscript_build

## Purpose
Build definition for the source4 private `cluster` library.

## Important APIs, types, and functions
Declares `bld.SAMBA_LIBRARY('cluster', source='cluster.c local.c', deps='dbwrap samba-hostconfig talloc', private_library=True)`.

## Control flow
No runtime flow. Waf reads this file during configuration/build to include the cluster dispatch and local backend objects.

## State and persistence behavior
No runtime state. Build output is a private Samba library, not a public installed library.

## Dependencies and integration points
Links the library against `dbwrap`, `samba-hostconfig`, and `talloc`. The dependency set matches `local_db_tmp_open()` and backend initialization needs.

## Risks and edge cases
Any future cluster backend source added under this directory will not be built unless this file is updated. Since the library is private, external consumers should not depend on it.

## Test signals
Build-system validation should confirm the `cluster` private library is produced and linked into consumers needing cluster APIs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/cluster/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dlz_bind9.c -->
# sources/user-network-fs/samba/source4/dns_server/dlz_bind9.c

## Purpose
Implements Samba's BIND9 DLZ driver. It exposes Active Directory DNS zones stored in Samba's `sam.ldb` to BIND, supports lookups and zone transfers, configures writable zones, and handles secure dynamic DNS updates using Kerberos/GENSEC authorization.

## Important APIs, types, and functions
- `struct dlz_bind9_data` is the driver state: parsed options, `samdb`, event/loadparm contexts, transaction token, SOA serial, writable zone list, Kerberos/auth state, cached update session info, and BIND helper callbacks.
- Public DLZ entry points include `dlz_version()`, `dlz_create()`, `dlz_destroy()`, `dlz_findzonedb()`, `dlz_lookup()`, `dlz_allowzonexfr()`, `dlz_allnodes()`, `dlz_newversion()`, `dlz_closeversion()`, `dlz_configure()`, `dlz_ssumatch()`, `dlz_addrdataset()`, `dlz_subrdataset()`, and `dlz_delrdataset()`.
- `b9_format()` converts Samba `dnsp_DnssrvRpcRecord` records into BIND text data.
- `b9_parse()` parses BIND SDLZ record strings back into Samba DNS RPC records.
- `b9_find_zone_dn()` and `b9_find_name_dn()` safely construct LDB DNs for zones/names under known AD DNS containers.
- `b9_set_session_info()` and `b9_reset_session_info()` temporarily switch LDB session info for authorized updates.

## Control flow
`dlz_create()` is the initialization hub. It captures BIND helper callbacks from varargs, disables Samba signal handlers, redirects Samba debug to BIND logging, parses options, initializes loadparm, Kerberos, GENSEC, auth context, locates `dns/sam.ldb`, connects to `samdb`, and stores singleton global state with reference counting.

Lookup paths use `b9_find_zone_dn()` for zone existence and `dlz_lookup_types()` for node lookups. Zone transfer uses `dlz_allowzonexfr()` for allow/deny policy and `dlz_allnodes()` to search all `dnsNode` objects and emit named records. Dynamic update paths require `dlz_newversion()` to start an LDB transaction; BIND then calls add/sub/delete dataset functions; `dlz_closeversion()` commits or cancels.

Secure update authorization runs through `dlz_ssumatch()`: it decodes the GSS key data using DNS keytab credentials, creates session info from the PAC, maps the requested DNS name to an existing node or parent DN, performs a DSDB ACL check for self-write or create-child, then caches the session for the following mutation.

## State and persistence behavior
State is process-global and singleton (`dlz_bind9_state`, refcount), plus mutable per-driver state. Persistent changes are LDB transactions against Samba DNS records. Dynamic update delete operations tombstone individual record values rather than necessarily deleting whole objects. The code caches the current SOA serial from SOA formatting and passes it into `dns_common_replace()` for update-side serial handling.

## Dependencies and integration points
This file bridges BIND's dlopen DLZ ABI (`dlz_minimal.h`) with Samba DSDB, auth/session, GENSEC/Kerberos, dnsserver common helpers, loadparm DNS transfer allow/deny settings, and BIND callback functions such as `putrr`, `putnamedrr`, and `writeable_zone`.

## Risks and edge cases
- Singleton global state and mutable `session_info`/`update_name` are not safe for arbitrary concurrent updates unless BIND's call pattern serializes this driver.
- `dlz_addrdataset()` checks `if (i == UINT16_MAX)` after a `uint16_t` loop, but the intended overflow condition is subtle and depends on `num_recs`.
- `b9_parse()` handles TXT quoting simply and may not fully match all DNS master-file escaping rules.
- Dynamic update correctness depends on `dlz_ssumatch()` being called before mutation; otherwise session info validation fails.
- Zone transfer defaults to deny, which is secure but can surprise deployments without explicit allow lists.
- The driver supports a fixed set of record types; unsupported types fail or are omitted.

## Test signals
No tests are included in this subset. Relevant coverage would include BIND DLZ lookup/allnodes behavior, safe DN construction with hostile names, transfer allow/deny combinations, GSS update authorization, add/modify/delete/tombstone semantics, transaction rollback, duplicate zone handling, and parsing/formatting for every supported record type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dlz_bind9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dlz_minimal.h -->
# sources/user-network-fs/samba/source4/dns_server/dlz_minimal.h

## Purpose
Provides a local minimal copy of the BIND DLZ dlopen ABI needed to compile Samba's DLZ module across supported BIND versions.

## Important APIs, types, and functions
- Version gates define `DLZ_DLOPEN_VERSION`, `DNS_CLIENTINFO_VERSION`, and `ISC_BOOLEAN_AS_BOOL` for BIND 9.10, 9.11, 9.12, 9.14, 9.16, and 9.18.
- Defines `isc_result_t`, `isc_boolean_t`, `dns_ttl_t`, result codes, boolean constants, log levels, and opaque BIND handle types.
- Defines `dns_clientinfo_t` and `dns_clientinfomethods_t` differently for client-info ABI v1 and v2.
- Declares callback types `log_t`, `dns_sdlz_putrr_t`, `dns_sdlz_putnamedrr_t`, and `dns_dlz_writeablezone_t`.
- Declares the DLZ entry point prototypes implemented by `dlz_bind9.c`.

## Control flow
Compile-time preprocessor selection rejects unsupported BIND versions and old 9.8/9.9 versions. There is no runtime control flow.

## State and persistence behavior
No state or persistence. The header fixes ABI constants and type signatures used when BIND loads the Samba module.

## Dependencies and integration points
Includes standard integer/bool headers and expects the build system to define exactly one supported `BIND_VERSION_*` macro. It is tightly coupled to BIND's external DLZ ABI and to `dlz_bind9.c`.

## Risks and edge cases
- New BIND versions fail compilation until explicitly added.
- ABI drift in BIND can break the copied definitions.
- `isc_boolean_t` changes between `int` and `bool` depending on version, which affects function signatures and binary compatibility.

## Test signals
Build matrix coverage against every supported BIND version is the main signal. Runtime smoke tests should load the module into each BIND version and exercise lookup and dynamic update entry points.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dlz_minimal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dns_crypto.c -->
# sources/user-network-fs/samba/source4/dns_server/dns_crypto.c

## Purpose
Handles TSIG verification and signing for Samba's internal DNS server, using GSS-TSIG/TKEY state stored in `dns_server_tkey` objects.

## Important APIs, types, and functions
- `dns_find_tkey()` searches the circular TKEY store by DNS key name using Samba DNS name equality.
- `dns_verify_tsig()` validates an incoming TSIG additional record and marks the request state authenticated.
- `dns_tsig_compute_mac()` builds the RFC TSIG signing buffer and calls `gensec_sign_packet()`.
- `dns_sign_tsig()` appends a TSIG record to an outgoing packet, including MAC data when there is no TSIG error.
- `dns_copy_tsig()` deep-copies TSIG record fields between `dns_res_rec` structures.

## Control flow
Verification finds a TSIG in the additional section, enforces that it is last, copies it into request state, removes it from the packet's additional count, finds the negotiated TKEY, checks the algorithm (`gss-tsig` or `gss.microsoft.com`), reconstructs the signed data by combining the original packet without TSIG and a fake TSIG record, decrements ARCOUNT in the raw packet bytes, and calls `gensec_check_packet()`. Access denied maps to BADSIG/REFUSED; success marks the request authenticated.

Signing creates a response TSIG. If no TSIG error is pending, it finds the TKEY, computes the MAC over optional request MAC, outgoing packet bytes, and fake TSIG data, then appends a real TSIG additional record to the packet. For `gss-tsig`, the request MAC length prefix is included; for Microsoft compatibility it is omitted.

## State and persistence behavior
No persistent storage is written. The code mutates `dns_request_state` (`sign`, `tsig`, `key_name`, `tsig_error`, `authenticated`) and the outgoing packet's additional records. TKEY state comes from the DNS server's in-memory circular store.

## Dependencies and integration points
Depends on generated DNS NDR encoders, GENSEC packet signing/checking, DNS request/server structures from `dns_server.h`, byte-order helpers, and WERROR/NTSTATUS conversion. It pairs with `dns_query.c` TKEY creation/acceptance.

## Risks and edge cases
- Time/fudge fields are copied into the MAC input, but there is no visible freshness check in this file.
- `dns_find_tkey()` assumes a valid store with `TKEY_BUFFER_SIZE` entries and scans modulo the fixed constant.
- The function mutates `packet->arcount` during verification, so later code sees TSIG removed.
- TSIG must be last; otherwise the request fails format validation.
- Algorithm string handling is exact and supports only two names.

## Test signals
Important tests include valid GSS-TSIG verification, BADKEY, BADSIG, TSIG-not-last format error, response signing with and without request MAC, both algorithm names, and interaction with TKEY negotiation in `dns_query.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dns_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dns_query.c -->
# sources/user-network-fs/samba/source4/dns_server/dns_query.c

## Purpose
Processes DNS queries for Samba's internal DNS server. It answers authoritative records from Samba DNS storage, follows CNAMEs with bounded recursion, forwards non-authoritative or CNAME-target queries to configured forwarders, adds authority records, and handles TKEY negotiation for GSS-TSIG.

## Important APIs, types, and functions
- `add_response_rr()` converts `dnsp_DnssrvRpcRecord` values into wire-response `dns_res_rec` records.
- `add_dns_res_rec()` deep-copies forwarded response records into local response arrays.
- `ask_forwarder_send/recv()` wraps asynchronous DNS client forwarding.
- `handle_authoritative_send/recv()` looks up local records and processes each through `handle_dnsrpcrec_send()`.
- `handle_dnsrpcrec_send()` filters record types, emits CNAMEs, and recursively resolves CNAME targets locally or through a forwarder, capped by `MAX_Q_RECURSION_DEPTH`.
- `create_tkey()`, `accept_gss_ticket()`, and `handle_tkey()` implement TKEY negotiation and populate the TKEY store.
- `dns_server_process_query_send/recv()` is the public async query-processing API.

## Control flow
`dns_server_process_query_send()` rejects packets without exactly one question, rejects QCLASS_NONE with NOT_IMPLEMENTED, handles TKEY questions immediately, builds a forwarder list from loadparm, then chooses authoritative handling, recursive forwarding, or NAME_ERROR. Authoritative processing initializes answer and authority arrays, resolves records from LDB-backed DNS helpers, follows CNAMEs for A/AAAA, and adds the zone SOA authority record before completion. Forwarder failures remove the current forwarder from the list and try the next one.

`handle_tkey()` expects the TKEY RR to be the last additional or answer RR. For GSSAPI mode it creates or reuses a TKEY, runs GENSEC update, stores reply key data on success, and marks the request for signing. Unsupported modes return DNS TKEY errors.

## State and persistence behavior
Normal queries do not persist changes. They allocate response arrays on tevent request contexts and move them to the caller in `dns_server_process_query_recv()`. TKEY negotiation mutates the DNS server's in-memory circular TKEY store and stores GENSEC/session state for later TSIG verification/signing.

## Dependencies and integration points
Uses Samba task context, loadparm DNS forwarder settings, DNS client library, DSDB DNS lookup helpers, generated DNS/DNSP NDR types, GENSEC server setup, DLIST list helpers, and tevent asynchronous request patterns. It integrates with `dns_crypto.c` through the shared TKEY store and request-state signing flags.

## Risks and edge cases
- Only one question per query is supported.
- CNAME recursion is silently capped by returning success with no deeper records when depth reaches 20.
- Forwarded additional records are moved in `ask_forwarder_recv()` but not copied into final answers during CNAME forwarded handling; only answers and NS records are copied in that path.
- TKEY delete mode is acknowledged but not implemented.
- `accept_gss_ticket()` maps MORE_PROCESSING_REQUIRED to OK auth error internally, but `handle_tkey()` then sets BADKEY for that status; multi-leg negotiation behavior needs protocol tests.
- Forwarder list handling removes failed entries but does not free with special cleanup beyond talloc ownership.

## Test signals
Needed coverage includes authoritative A/AAAA/CNAME/SRV/SOA/MX/TXT/PTR/NS answers, wildcard lookup, NAME_ERROR with SOA authority, forwarding and multi-forwarder fallback, recursion flags, CNAME local and forwarded resolution, TKEY GSS success/failure/mode handling, and TSIG signing handoff to `dns_crypto.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dns_query.c -->
