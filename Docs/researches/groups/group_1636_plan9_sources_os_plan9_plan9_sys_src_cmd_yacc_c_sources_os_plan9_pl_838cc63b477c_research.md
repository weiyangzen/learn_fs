# Group Research: group_1636_plan9_sources_os_plan9_plan9_sys_src_cmd_yacc_c_sources_os_plan9_pl_838cc63b477c

Scope verified against `Docs/research_subset_a.md`: all files are under the included `sources/os/plan9/plan9` source tree. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/yacc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/yacc.c

This is the Plan 9 yacc implementation. It reads a yacc grammar, builds LALR parsing states and lookahead sets, resolves conflicts, packs parser action/goto tables, emits C parser tables, then copies the parser skeleton from `/sys/lib/yaccpar` or `/sys/lib/yaccpars`.

Key behavior:
- Uses fixed-size global arrays for grammar symbols, productions, states, lookahead sets, working sets, and packed parser tables.
- `setup` handles options, opens output/temp files, scans declarations, reads grammar rules, copies user `%{...%}` code, handles `%union`, `%type`, precedence declarations, and embedded rule actions.
- `gettok`, `cpycode`, `cpyunion`, `skipcom`, and `cpyact` implement yacc-specific lexical handling and C action copying, including `$`, `$$`, typed semantic values, and named references.
- `cpres`, `cempty`, and `cpfir` compute nonterminal production lists, empty-string derivability, and first sets.
- `stagen`, `closure`, `state`, `putitem`, and `flset` build LR item sets, merge equivalent states, and intern lookahead sets.
- `output`, `wract`, `wrstate`, and `precftn` generate parser actions and diagnostics, including shift/reduce and reduce/reduce conflict reporting.
- `go2out`, `callopt`, `gin`, `stin`, and `nxti` pack shift and goto tables into compact arrays.
- `others`, `warray`, `arout`, and `aoutput` emit `yyact`, `yypact`, `yypgo`, `yyr1`, `yyr2`, `yychk`, `yydef`, token translation tables, and copied parser code.

Important dependencies:
- Plan 9 libraries: `<u.h>`, `<libc.h>`, `<bio.h>`, `<ctype.h>`.
- Parser skeleton files: `/sys/lib/yaccpar` and `/sys/lib/yaccpars`.
- Output conventions: default `y.tab.c`, optional `y.tab.h`, `y.output`, and debug token/state output.

Notable details:
- Token values default into the Unicode private-use range via `PRIVATE`.
- Lookahead bitsets are 32-bit integer arrays sized from terminal count.
- The implementation reuses `mem0` for both production storage and item/state storage, with an explicit portability warning about pointer-vs-int assumptions.
- Temporary files store actions and intermediate table data, then are removed by `cleantmp`.
- Generated parser tables use old yacc conventions such as `yyexca`, `YYNPROD`, `YYPRIVATE`, `YYLAST`, and `YYMAXDEPTH`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/yacc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/auth.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/auth.c

This file implements factotum-backed 9P authentication support for lib9p servers.

Key behavior:
- Defines per-auth-fid `Afid` state containing an `AuthRpc`, requested user/aname, completion flag, and factotum fd.
- `auth9p` allocates an auth fid, opens `/mnt/factotum/rpc`, starts an auth RPC using `Srv.keyspec` or default `proto=p9any role=server`, assigns a synthetic `QTAUTH` qid, and attaches `Afid` to the fid.
- `_authread` drives the factotum read phase, copies challenge data to the client, and marks auth successful once `auth_getinfo` succeeds.
- `authread` and `authwrite` expose auth fid I/O through normal 9P read/write requests.
- `authdestroy` frees auth RPC state, strings, and fd when an auth fid is destroyed.
- `authattach` validates that attach uses a completed auth fid and that uname/aname match the original auth request.

Important dependencies:
- Plan 9 auth APIs: `auth_allocrpc`, `auth_rpc`, `auth_getinfo`, `auth_freerpc`.
- lib9p request/fid lifecycle: `Req`, `Fid`, `respond`, `responderror`.

Notable details:
- `authgen` starts at the high bit and increments for distinct auth qid paths.
- Attach can force completion by calling `_authread` with a zero-length buffer if authentication has not yet reached `ARdone`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/dirread.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/dirread.c

This file provides `dirread9p`, a helper for implementing 9P directory reads from a generator callback.

Key behavior:
- Uses `r->ifcall.offset` and `r->fid->dirindex` to preserve directory iteration position.
- Calls a `Dirgen` callback with a numeric index and caller-provided aux pointer.
- Converts each generated `Dir` to wire format using `convD2M`.
- Stops when the generator ends or the next encoded directory entry will not fit.
- Frees generated `Dir` string fields after each conversion.
- Sets `r->ofcall.count` and updates `fid->dirindex`.

Notable details:
- Offset zero resets iteration to entry zero.
- Nonzero offsets resume from the fid’s saved index rather than deriving an index from byte offset.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/dirread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/fid.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/fid.c

This file manages lib9p fid allocation, lookup, reference counting, removal, and destruction.

Key behavior:
- `allocfidpool` creates an integer map whose lookup callback increments fid references.
- `allocfid` creates a `Fid`, initializes `fid`, `omode = -1`, and inserts it into the pool only if the key is unused.
- `lookupfid` returns a referenced fid by numeric id.
- `removefid` deletes a fid from the pool map and returns the referenced object.
- `closefid` releases directory-read state, calls the pool destroy hook, closes attached `File`, frees uid, and frees the fid when the refcount reaches zero.
- `freefidpool` frees the map and applies the configured fid destroy hook.

Important dependencies:
- Uses `Intmap` from `intmap.c`.
- Uses `closedirfile` and `closefile` for tree-backed fids.

Notable details:
- `allocfid` takes two references: one for the map and one for the caller/request.
- Duplicate fid insertion backs out both references and returns `nil`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/fid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/file.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/file.c

This file implements lib9p’s in-memory `Tree`/`File` hierarchy used by simple tree-backed 9P servers.

Key behavior:
- Maintains a global free list of `File` objects allocated in batches.
- `alloctree` creates a root directory with uid/gid defaults and a destroy callback.
- `createfile` creates child files/directories, preserves creation order, assigns qids, initializes owner/mode/times, links into the parent, and returns a referenced file.
- `walkfile` and `walkfile1` resolve path elements and `..`, returning referenced files.
- `removefile` unlinks a leaf file from its parent, refuses root removal and non-empty directories, handles list tombstones, and drops tree/parent/caller refs.
- `opendirfile`, `readdirfile`, and `closedirfile` support stable directory iteration over the `Filelist`.
- `freetree` recursively destroys all files and frees the tree.

Important dependencies:
- Wire stat conversion via `convD2M`, relying on `File` layout embedding or matching `Dir` fields.
- Refcounting and locks from Plan 9 threading primitives.
- Destroy callbacks supplied by the embedding server.

Notable details:
- Locking rule is documented: lock child before parent; do not lock files while holding the free-file lock.
- Deleted entries remain as empty slots while directory readers exist, then `cleanfilelist` removes tombstones later.
- Directory qid/version bookkeeping is simple: qid paths come from `Tree.qidgen`; `Tree.dirqidgen` is initialized but not used in this file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/ftest.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/ftest.c

This is a small test program for the in-memory lib9p file tree.

Key behavior:
- Creates a tree with `mktree`.
- Creates two root directories, `hello` and `goodbye`.
- Creates `world` files under both directories.
- Dumps the tree with `fdump`.
- Removes one `world` file and dumps the tree again.

Role:
- Exercises basic create, nested create, remove, and tree dump behavior.
- Depends on test/helper APIs visible through `9p.h`, including `mktree`, `fcreate`, `fremove`, and `fdump`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/ftest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/intmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/intmap.c

This file implements a small locked hash map from `ulong` ids to arbitrary pointers.

Key behavior:
- Uses 128 hash buckets with linked `Intlist` chains.
- `allocmap` stores an optional increment callback used by lookups.
- `lookupkey` read-locks, finds an id, calls the increment callback while locked, and returns the object.
- `insertkey` inserts or replaces an entry, returning the old value without destroying it.
- `caninsertkey` inserts only if absent and returns success/failure.
- `deletekey` removes an entry and returns its value.
- `freemap` walks all buckets, calls an optional destroy callback on each aux pointer, and frees nodes/map.

Important dependencies:
- Used by fid and request pools.
- Relies on callers’ object refcount increment functions being safe under the map lock.

Notable details:
- The source comment explicitly says the map lock protects tree/map structure, not object references; `inc` must provide its own locking discipline.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/intmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/listen.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/listen.c

This file implements network-listening support for lib9p servers.

Key behavior:
- `_listensrv` copies a `Srv`, stores the listen address, and starts `listenproc` through the configured `_forker`.
- `listenproc` announces the address, loops accepting connections, creates a per-connection `Srv` copy, initializes connection fds and transient buffers/pools to nil, and starts `srvproc`.
- `srvproc` runs `srv`, closes the data fd, then frees the per-connection address and server copy.
- `getremotesys` reads the Plan 9 network connection `remote` file and stores the remote system prefix before `!`, defaulting to `"unknown"`.

Important dependencies:
- Requires `_forker` to have been set by `rfork.c` or `thread.c`.
- Uses Plan 9 network primitives `announce`, `listen`, and `accept`.

Notable details:
- Each accepted connection gets a shallow copy of the original `Srv`; per-connection pools and buffers are reset so `srv` allocates its own.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/listen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/mem.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/mem.c

This file provides fatal allocation helpers for lib9p.

Key behavior:
- `emalloc9p` allocates zeroed memory or exits with `"mem"`.
- `erealloc9p` reallocates memory or exits with `"mem"`.
- `estrdup9p` duplicates strings or exits with `"mem"`.

Notable details:
- Uses Plan 9 allocation tagging helpers `setmalloctag` and `setrealloctag`.
- Callers do not need to check for allocation failure because these helpers terminate on failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/parse.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/parse.c

This file implements control-command parsing helpers for lib9p servers.

Key behavior:
- `parsecmd` copies a written command buffer, strips a trailing newline, tokenizes whitespace-separated fields, and returns a `Cmdbuf`.
- `ncmdfield` estimates the number of fields to size the `Cmdbuf` allocation.
- `respondcmderror` reconstructs a quoted command string and appends it to an error response.
- `lookupcmd` matches the first parsed field against a `Cmdtab`, supports `*` wildcard commands, and validates argument count when `narg` is nonzero.

Important dependencies:
- Uses Plan 9 `tokenize`, `quotefmtinstall`, and formatted error helpers.
- Responds through lib9p `respond`.

Notable details:
- UTF is explicitly irrelevant to field splitting; bytes are tested only against ASCII whitespace.
- `Cmdbuf`, pointer array, and copied command string are allocated as one block.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/post.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/post.c

This file implements posting and optional mounting of a lib9p server through a pipe.

Key behavior:
- `_postmountsrv` creates a pipe unless `Srv.nopipe` is set, assigns server and kernel-side fds, and optionally posts the server fd in `/srv`.
- Starts `postproc` through `_forker` with `RFNAMEG`.
- Unless `leavefdsopen` is set, it switches fd groups, synchronizes with the server process via `rendezvous`, and closes server-side pipe fds before mounting.
- If a mount point is provided, it mounts with `amount`; otherwise it closes `srvfd`.
- `postproc` optionally isolates note group/fd handling, closes the kernel-side fd, and runs `srv`.

Important dependencies:
- Requires `_forker` set by process or thread wrappers.
- Uses `postfd` from `srv.c`.

Notable details:
- The long comment documents the fd-lifetime issue: keeping the server half open in the mounting process can make a mount hang after server death.
- `leavefdsopen` is an escape hatch for programs where fd bookkeeping is impractical.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/post.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/ramfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/ramfs.c

This file is a simple lib9p-backed in-memory file server example/application.

Key behavior:
- Defines `Ramfile` with a data buffer and byte length.
- `fsread` reads from a file’s in-memory buffer respecting offset/count.
- `fswrite` reallocates storage as needed, writes request data, updates file length, and reports bytes written.
- `fscreate` creates a tree-backed file with `createfile`, attaches a new `Ramfile`, updates fid state, and returns the qid.
- `fsopen` handles `OTRUNC` by clearing in-memory length and visible file length.
- `fsdestroyfile` frees per-file data.
- `main` creates an alloctree root, parses `-D`, `-a`, `-s`, and `-m`, then serves by network listen and/or postmount.

Important dependencies:
- Uses the in-memory tree from `file.c`.
- Uses listen/postmount wrappers from `listen.c`, `post.c`, `rfork.c`, or `thread.c`.

Notable details:
- The server requires at least one of address, service name, or mount point.
- Permission enforcement is mostly delegated to generic `srv.c` handling and tree metadata.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/ramfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/req.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/req.c

This file manages request pools, request lookup, reference counting, and request destruction.

Key behavior:
- `allocreqpool` creates an `Intmap` keyed by 9P tag with lookup ref increments.
- `allocreq` creates and inserts a `Req`, taking one map reference and one caller reference.
- `lookupreq` returns a referenced request by tag.
- `removereq` removes a request from the pool map.
- `closereq` releases fids, newfids, afids, old flush target refs, delayed flush requests, stat buffers, copied `Dir` strings, custom destroy hook, request buffers, and the request itself.
- `freereqpool` frees the map and applies the configured request destroy hook.

Important dependencies:
- Uses `Intmap` from `intmap.c`.
- Coordinates with flush and response handling in `srv.c`.

Notable details:
- If a request is destroyed while flush requests are queued, `closereq` responds to those flushes with success.
- Debug tracing is gated by `chatty9p > 1`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/req.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/rfork.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/rfork.c

This file provides process-based serving wrappers for lib9p.

Key behavior:
- Defines `rforker`, which starts a function in a new process using `rfork(RFPROC|RFMEM|RFNOWAIT|flag)`.
- Child processes run the supplied function and call `_exits(0)`.
- `listensrv` sets global `_forker` to `rforker` and delegates to `_listensrv`.
- `postmountsrv` sets `_forker` to `rforker` and delegates to `_postmountsrv`.

Role:
- Selects process/rfork concurrency for listening and postmount serving.
- Complements `thread.c`, which selects libthread process creation instead.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/rfork.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/srv.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/srv.c

This is the core lib9p 9P2000 server dispatcher. It reads incoming 9P messages, creates `Req` objects, dispatches by message type, applies generic fid/tree semantics, calls server callbacks, serializes responses, and cleans up pools.

Key behavior:
- Maintains global `_forker` used by listen/postmount helpers.
- `changemsize` resizes shared read/write buffers under locks.
- `getreq` reads a 9P message, decodes it into `Fcall`, allocates a tagged request, and creates a fake request for duplicate tags.
- `srv` initializes fmt handlers, fid/request pools, default msize, buffers, then loops over requests and dispatches `Tversion`, `Tauth`, `Tattach`, `Tflush`, `Twalk`, `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tclunk`, `Tremove`, `Tstat`, and `Twstat`.
- Tree-backed operation support handles attach-to-root, file walking, permission checks, directory open/read, remove, stat copying, and qid/version updates.
- Callback-driven operation support allows servers to provide `auth`, `attach`, `flush`, `walk`, `walk1`, `clone`, `open`, `create`, `read`, `write`, `remove`, `stat`, and `wstat`.
- `respond` runs per-message postprocessing, converts errors to `Rerror`, serializes with `convS2M`, writes replies under `wlock`, removes requests from the pool, and releases delayed flush replies.
- `responderror` converts current `%r` state into a 9P error response.
- `postfd` posts a server fd under `/srv/<name>`.

Important dependencies:
- `fid.c`, `req.c`, `file.c`, `uid.c`, and `mem.c`.
- Plan 9 wire conversion: `read9pmsg`, `convM2S`, `convS2M`, `convD2M`, `convM2D`.
- Uses `fcallfmt` and `dirfmt` for debug output.

Notable details:
- Flush handling is special: a flush reply can be delayed until the old request responds.
- Partial walks are treated as successful with no error when at least one element was walked.
- Directory reads require offset zero or the current tracked directory offset.
- Wstat prevalidates immutable fields before calling the server’s `wstat`.
- The generic remove path removes the fid from the pool before invoking callbacks, matching 9P remove semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/thread.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/thread.c

This file provides libthread-based serving wrappers for lib9p.

Key behavior:
- Defines `tforker`, which starts work with `procrfork` and a 32 KiB stack.
- `threadlistensrv` sets global `_forker` to `tforker` and delegates to `_listensrv`.
- `threadpostmountsrv` sets `_forker` to `tforker` and delegates to `_postmountsrv`.

Role:
- Selects libthread process creation for listen and postmount server helpers.
- Complements `rfork.c`, which uses raw `rfork`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/thread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/uid.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/uid.c

This file implements simple permission checking for lib9p tree-backed files.

Key behavior:
- `hasperm` checks requested access bits against other, owner, and group permissions.
- Owner match is `strcmp(f->uid, uid) == 0`.
- Group match is simplified to `strcmp(f->gid, uid) == 0`.
- Returns true when any applicable permission class satisfies the requested mask.

Notable details:
- The comment states the simplification: each user is assumed to be the leader/member of her own group.
- Permissions are additive: matching owner or group ORs those permission bits with the already-checked other bits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/uid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/lib9p/util.c

This file provides small read-response helpers for lib9p servers.

Key behavior:
- `readbuf` copies a bounded slice from a memory buffer into `r->ofcall.data` based on request offset/count.
- If offset is past the end, it returns zero bytes.
- If requested data extends past the end, it truncates count.
- `readstr` applies `readbuf` to a NUL-terminated string using `strlen`.

Role:
- Convenience for simple synthetic-file read handlers.
- Does not call `respond`; callers set up data and respond separately.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/lib9p/util.c -->