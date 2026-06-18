# Group Research: group_197_9front_sources_os_plan9_9front_sys_src_cmd_yacc_c_sources_os_plan9_9_f7f4d6982c42

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/yacc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/yacc.c

## Read Status
Complete: 2,954 lines read.

## Purpose
This file is a complete Plan 9 yacc implementation. It reads yacc grammar files, parses declarations and grammar rules, builds LALR-style parser states with lookahead sets, detects and resolves conflicts, packs action/goto tables, and emits generated C parser output using `/sys/lib/yaccpar` or `/sys/lib/yaccpars`.

## Main Responsibilities
- Command-line setup for yacc output: `-v`, `-d`, `-D`, `-o`, `-s`, and `-S`.
- Grammar declaration parsing: tokens, precedence, associativity, types, `%union`, `%start`, and copied code blocks.
- Grammar rule parsing, including embedded actions rewritten as synthetic empty productions.
- Symbol table management for terminals and nonterminals.
- FIRST set and nullable/non-empty derivation analysis.
- LR item closure and state generation.
- Shift/reduce and reduce/reduce conflict reporting and precedence handling.
- Action and goto table generation, packing, optimization, and C array emission.
- Parser skeleton copying and insertion of generated semantic actions.

## Key Data Structures
- `Symb`: symbol name and numeric token/nonterminal value.
- `Lkset`: terminal bitset used for lookahead sets.
- `Item`: LR item pointer plus associated lookahead set.
- `Wset`: temporary working-set item used during closure and state construction.
- Global fixed-size arrays such as `tokset`, `nontrst`, `prdptr`, `pstate`, `lkst`, `amem`, and `mem0` hold most compiler state.

## Important Functions
- `main`: orchestrates setup, grammar analysis, state generation, table output, optimization, and parser skeleton completion.
- `setup`: parses command-line arguments and the yacc input file, builds productions, symbols, type data, and semantic action temp files.
- `gettok`: lexer for yacc grammar syntax, identifiers, string/char literals, declarations, comments, numbers, and section markers.
- `cpyunion`, `cpycode`, `cpyact`: copy user C fragments into output, translating yacc semantic variables like `$$`, `$1`, and `$name`.
- `cpres`, `cempty`, `cpfir`: compute production lists by nonterminal, nullable symbols, and FIRST sets.
- `closure`, `state`, `stagen`: compute closures, canonical states, and gotos.
- `output`, `wract`, `wrstate`, `precftn`: emit per-state actions, diagnose conflicts, and apply precedence/associativity rules.
- `go2out`, `go2gen`: generate nonterminal goto data.
- `callopt`, `stin`, `gin`, `nxti`: table-packing optimizer.
- `others`: writes final parser arrays, token translation tables, generated action code, and parser skeleton.

## Dependencies and Interactions
- Uses Plan 9 headers and runtime APIs: `<u.h>`, `<libc.h>`, `<bio.h>`, `<ctype.h>`.
- Uses `Biobuf` for all main file IO.
- Reads parser skeleton files from `/sys/lib/yaccpar` or `/sys/lib/yaccpars`.
- Writes generated `tab.c`, optional `tab.h`, optional `output`, optional `debug`, and temporary files for actions/tables.
- Uses Plan 9 private-use Unicode token values beginning at `0xE000`.

## Design Notes
- This is an old-style C program built around global fixed-size arrays rather than dynamically sized containers.
- Several comments acknowledge portability constraints, especially reusing `mem0` for both production integers and `Item` storage.
- Error handling is mostly fatal through `error`, which summarizes, removes temp files, and exits.
- The implementation assumes limits such as `NSTATES`, `NPROD`, `NTERMS`, `NNONTERM`, `ACTSIZE`, and `MEMSIZE`; large grammars fail with explicit diagnostics.
- The file is not a filesystem component itself, but it is part of the 9front source tree tooling included in subset A.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/yacc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/auth.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/auth.c

## Read Status
Complete: 203 lines read.

## Purpose
Implements lib9p authentication support using Plan 9 factotum. It handles `Tauth` setup, auth fid reads/writes, auth fid destruction, and authenticated attach validation.

## Main Responsibilities
- Allocate an auth helper state (`Afid`) for each auth fid.
- Open `/mnt/factotum/rpc` and start a factotum auth protocol.
- Expose auth RPC exchange over 9P read/write on `QTAUTH` fids.
- Verify returned `AuthInfo` user identity against requested uname.
- Ensure `Tattach` uses the same uname/aname and has completed authentication.

## Important Functions
- `auth9p`: initializes factotum auth RPC state and returns an auth qid.
- `_authread`: internal auth RPC read step; marks authentication complete on `ARdone`.
- `authread`: 9P auth fid read handler.
- `authwrite`: 9P auth fid write handler.
- `authdestroy`: frees auth RPC state attached to a fid.
- `authattach`: validates an attach against a completed auth fid.

## Dependencies and Interactions
- Uses `<auth.h>` and factotum RPC APIs: `auth_allocrpc`, `auth_rpc`, `auth_getinfo`, `auth_freerpc`.
- Intended to be wired into `Srv.auth`, `Srv.read`, `Srv.write`, and fid destroy paths.
- Shares response flow with `respond` and `responderror` from `srv.c`.

## Notes
- `authgen` generates synthetic auth qid paths starting in the high path range.
- Authentication defaults to `proto=p9any role=server` unless `srv->keyspec` is set.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/dirread.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/dirread.c

## Read Status
Complete: 39 lines read.

## Purpose
Provides a helper for implementing directory reads from a callback-style directory generator.

## Main Responsibilities
- Track directory entry index across reads using `r->fid->dirindex`.
- Call a `Dirgen` callback to fill `Dir` records.
- Pack directory entries with `convD2M` into the response buffer.
- Free dynamically allocated `Dir` string fields after packing.

## Important Function
- `dirread9p`: fills `r->ofcall.data` with serialized directory entries until the request buffer is full or the generator is exhausted.

## Dependencies and Interactions
- Used by 9P server implementations that do not use lib9p’s built-in `File` tree readdir path.
- Relies on 9P `Dir` serialization rules and `BIT16SZ` minimum packed-size check.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/dirread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/fid.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/fid.c

## Read Status
Complete: 81 lines read.

## Purpose
Implements fid pool allocation, lookup, reference management, and removal for lib9p servers.

## Main Responsibilities
- Allocate `Fidpool` objects backed by `Intmap`.
- Allocate new `Fid` objects and insert them by numeric fid.
- Look up fids while incrementing references.
- Remove fids from the pool.
- Close fids and release associated resources.

## Important Functions
- `allocfidpool`, `freefidpool`: create and destroy fid maps.
- `allocfid`: allocate a fid, initialize `omode = -1`, and insert it uniquely.
- `lookupfid`: find a fid by id.
- `removefid`: delete a fid mapping and return the fid.
- `closefid`: decrements reference count and frees directory readers, files, uid strings, and custom destroy state.

## Dependencies and Interactions
- Uses `Intmap` from `intmap.c` with `incfidref` as the lookup reference hook.
- Calls `closedirfile` and `closefile` for tree-backed fids.
- Optional `pool->destroy` hook lets servers clean custom fid state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/fid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/file.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/file.c

## Read Status
Complete: 425 lines read.

## Purpose
Implements lib9p’s in-memory `Tree` and `File` hierarchy helpers. This gives 9P servers a default file tree model with creation, walking, removal, stat data, reference management, and directory iteration.

## Main Responsibilities
- Allocate and recycle `File` objects.
- Maintain parent/child relationships through linked `Filelist` entries.
- Preserve creation order during directory iteration.
- Safely remove files while active directory readers may still reference list nodes.
- Provide path walking helpers.
- Build and free whole trees.
- Provide directory open/read/close helpers for server reads.

## Important Functions
- `allocfile`, `freefile`: internal file allocator/free-list management.
- `createfile`: creates a child under a directory, assigns qid path/type, ownership, mode, and timestamps.
- `removefile`: removes a leaf file from its parent and handles reference release.
- `walkfile1`, `walkfile`: walk one path element or slash-separated paths.
- `alloctree`: creates a root directory tree with ownership and mode.
- `freetree`, `_freefiles`: recursively destroy a tree.
- `opendirfile`, `readdirfile`, `closedirfile`: support serialized directory reads.

## Data Structures
- `Filelist`: linked child entry, possibly retained with `f == nil` while readers exist.
- `Readdir`: directory read cursor containing a directory and current `Filelist` position.
- `Tree`: holds root file, qid generator, and destroy callback.

## Dependencies and Interactions
- Used by `srv.c` when `srv->tree` is set.
- `convD2M` serializes `File` directory metadata into 9P stat records.
- `hasperm` from `uid.c` checks permissions for open/create/remove paths.
- Lock ordering is explicitly documented: lock child before parent; do not lock files while holding the free-file lock.

## Notes
- Removed children are marked empty first, then list entries are cleaned only when no directory readers remain.
- `closefile` invokes the tree destroy callback when the final reference disappears.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/ftest.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/ftest.c

## Read Status
Complete: 28 lines read.

## Purpose
Small test/demo program for file tree creation, dumping, and removal.

## Main Responsibilities
- Create an in-memory tree.
- Add directories `hello` and `goodbye`.
- Add files named `world` under each directory.
- Dump the tree, remove one file, then dump again.

## Important Function
- `main`: exercises tree helpers through calls such as `mktree`, `fcreate`, `fdump`, and `fremove`.

## Notes
- This file uses older or wrapper-style names and includes `"9p.h"` rather than `<9p.h>`, so it appears to be a local test harness or historical test rather than core library implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/ftest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/intmap.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/intmap.c

## Read Status
Complete: 164 lines read.

## Purpose
Provides a small thread-safe integer-keyed map used by fid and request pools.

## Main Responsibilities
- Store `ulong` ids to arbitrary pointers.
- Provide insert, conditional insert, lookup, delete, and full-map free.
- Increment object references on lookup through a caller-supplied callback.
- Protect table structure with an `RWLock`.

## Important Functions
- `allocmap`: creates a map and installs an optional increment callback.
- `freemap`: destroys all buckets and optionally calls a destroy callback for values.
- `lookupkey`: finds a value and calls `inc` while holding the read lock.
- `insertkey`: inserts or replaces an id, returning the old value.
- `caninsertkey`: inserts only if the id is absent.
- `deletekey`: removes an id and returns its value.

## Data Structures
- `Intmap`: `RWLock`, fixed 128-bucket hash table, and `inc` callback.
- `Intlist`: bucket-chain node containing id, value, and next link.

## Dependencies and Interactions
- Used by `fid.c` and `req.c`.
- The comment clarifies that value reference increments must be independently safe because they happen while the map lock is held.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/intmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/listen.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/listen.c

## Read Status
Complete: 118 lines read.

## Purpose
Adds network-listening support for lib9p servers. It announces a network address, accepts connections, clones the server template, and runs each connection as a 9P service.

## Main Responsibilities
- Duplicate an input `Srv` as a listener template.
- Announce and listen on a Plan 9 network address.
- Accept client connections.
- Create per-connection `Srv` instances with separate fd state.
- Determine remote system name from the network directory.
- Free per-connection resources on server close.

## Important Functions
- `listensrv`: prepares a listener `Srv` and starts `listenproc`.
- `listenproc`: announce/listen/accept loop.
- `srvproc`: invokes `srv`.
- `srvfree`: closes connection fd and frees address/server copy.
- `getremotesys`: reads `ndir/remote` and extracts the remote system component.

## Dependencies and Interactions
- Uses Plan 9 network primitives: `announce`, `listen`, `accept`.
- Uses `Srv.forker`, defaulting to `srvforker`, so callers can choose process or thread-style execution.
- Each accepted connection runs through the common `srv.c` service loop.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/listen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/mem.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/mem.c

## Read Status
Complete: 42 lines read.

## Purpose
Provides fatal-on-failure allocation helpers for lib9p.

## Main Responsibilities
- Allocate zeroed memory.
- Reallocate memory with fatal error handling.
- Duplicate strings with fatal error handling.
- Set Plan 9 allocation/reallocation tags for debugging.

## Important Functions
- `emalloc9p`: `malloc`, zero-fill, tag, or `sysfatal`.
- `erealloc9p`: `realloc`, tag, or `sysfatal`.
- `estrdup9p`: `strdup`, tag, or `sysfatal`.

## Dependencies and Interactions
- Used throughout lib9p for simpler error paths.
- Allocation failures terminate the process rather than returning errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/mount.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/mount.c

## Read Status
Complete: 22 lines read.

## Purpose
Provides a convenience function to post a 9P server and optionally mount it.

## Main Responsibilities
- Call `postsrv` to create a pipe-backed server endpoint.
- Mount the returned fd at a mount point with `amount`.
- Close the service fd when no mount point is supplied.

## Important Function
- `postmountsrv`: posts `Srv` under an optional `/srv` name and mounts it at `mtpt` with the supplied flags.

## Dependencies and Interactions
- Uses `postsrv` from `post.c`.
- Uses Plan 9 `amount`; fatal errors terminate with `sysfatal`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/parse.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/parse.c

## Read Status
Complete: 116 lines read.

## Purpose
Implements parsing and dispatch helpers for text control commands written to 9P control files.

## Main Responsibilities
- Count whitespace-separated command fields.
- Allocate a combined command buffer, argv vector, and copied command text.
- Tokenize command text.
- Build detailed command error responses quoting original arguments.
- Match parsed commands against a command table.

## Important Functions
- `parsecmd`: returns a `Cmdbuf` with tokenized fields.
- `respondcmderror`: formats an error message including the reconstructed command.
- `lookupcmd`: finds a matching `Cmdtab`, supports wildcard `*`, and validates argument counts.

## Dependencies and Interactions
- Used by servers implementing ctl-style files.
- Uses `tokenize`, `%q` formatting via `quotefmtinstall`, and lib9p `respond`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/post.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/post.c

## Read Status
Complete: 48 lines read.

## Purpose
Posts a 9P server through a pipe, optionally advertising the read fd in `/srv`.

## Main Responsibilities
- Create a pipe for client/server communication.
- Optionally create `/srv/<name>` and write the client-side fd number.
- Configure `Srv.infd` and `Srv.outfd` to the server-side pipe fd.
- Start the server in a separate execution context.
- Return the client-side fd to the caller.

## Important Functions
- `postsrv`: main posting helper.
- `postproc`: child/server entry that rendezvous-closes the client fd and runs `srv`.

## Dependencies and Interactions
- Uses `rendezvous` to coordinate fd ownership.
- Uses `srvforker` unless `Srv.forker` is already set.
- Called by `postmountsrv`, `postsharesrv`, and thread wrappers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/post.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/queue.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/queue.c

## Read Status
Complete: 104 lines read.

## Purpose
Implements a request queue with a worker proc for serializing potentially interruptible request handlers.

## Main Responsibilities
- Create a queue backed by a Plan 9 proc.
- Push requests with handler callbacks.
- Remove or interrupt queued/current requests on flush.
- Shut down the queue by pushing a sentinel request.

## Important Functions
- `reqqueuecreate`: allocates queue and starts `_reqqueueproc`.
- `reqqueuepush`: appends a request and wakes the worker.
- `reqqueueflush`: interrupts the current request or removes a queued request and responds `"interrupted"`.
- `reqqueuefree`: sends a nil-handler sentinel to terminate the worker.
- `_reqqueueproc`: worker loop that pops requests and runs callbacks.

## Dependencies and Interactions
- Uses `proccreate`, `threadint`, `rsleep`, `rwakeup`, `QLock`.
- Writes `nointerrupt` to `/proc/<pid>/ctl` before waiting to avoid interruption while idle.
- The queue node is embedded in `Req` as `r->qu`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/queue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/ramfs.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/ramfs.c

## Read Status
Complete: 169 lines read.

## Purpose
A small in-memory 9P file server built on lib9p’s tree helpers. It can listen on a network address, post itself in `/srv`, and/or mount itself.

## Main Responsibilities
- Store file contents in per-file `Ramfile` buffers.
- Implement read, write, create, open/truncate, and file destruction callbacks.
- Build an all-writable root tree.
- Parse command-line options for debug, address, service name, and mount point.
- Start the server via `listensrv` and/or `postmountsrv`.

## Important Functions
- `fsread`: reads from `Ramfile.data` using request offset/count.
- `fswrite`: grows file data with `realloc`, updates length, and writes bytes.
- `fscreate`: creates a tree file and attaches a new `Ramfile`.
- `fsopen`: handles `OTRUNC`.
- `fsdestroyfile`: frees `Ramfile` content.
- `main`: initializes `Srv fs`, creates the root tree, parses options, and starts service endpoints.

## Dependencies and Interactions
- Uses `alloctree`, `createfile`, `postmountsrv`, and `listensrv`.
- `Srv fs` installs `.open`, `.read`, `.write`, and `.create` callbacks.
- Demonstrates lib9p’s default tree-backed server flow.

## Notes
- This is a simple example/server, not a persistent filesystem.
- File growth uses `int ndata`, so it is suitable for small in-memory files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/ramfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/req.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/req.c

## Read Status
Complete: 112 lines read.

## Purpose
Implements request pool allocation, lookup, reference management, removal, and cleanup for active 9P requests.

## Main Responsibilities
- Allocate `Reqpool` objects backed by `Intmap`.
- Allocate requests by tag and reject duplicate tags.
- Look up active requests while incrementing references.
- Remove requests from the pool.
- Close requests and release all related fid, flush, stat, buffer, and custom state.

## Important Functions
- `allocreqpool`, `freereqpool`: manage request maps.
- `allocreq`: allocate and insert a request by tag.
- `lookupreq`: find an active request by tag.
- `removereq`: remove an active request from the pool.
- `closereq`: release request references and free associated resources at zero refs.

## Dependencies and Interactions
- Uses `Intmap` from `intmap.c`.
- Used heavily by `srv.c` for duplicate tag detection, `Tflush`, and response cleanup.
- Optional `pool->destroy` hook allows server-specific request cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/req.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/rfork.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/rfork.c

## Read Status
Complete: 19 lines read.

## Purpose
Default process-style forker for lib9p servers.

## Main Responsibilities
- Start a function in a new Plan 9 process sharing memory.
- Apply caller-supplied `rfork` flags.
- Fatal out if process creation fails.

## Important Function
- `srvforker`: wraps `rfork(RFPROC|RFMEM|RFNOWAIT|flag)`, runs `fn(arg)` in the child, then exits.

## Dependencies and Interactions
- Used as the default `Srv.forker` by `srv.c`, `post.c`, and `listen.c`.
- Alternative thread-style behavior is supplied by `thread.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/rfork.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/share.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/share.c

## Read Status
Complete: 33 lines read.

## Purpose
Posts a 9P server and optionally advertises it through the Plan 9 share namespace.

## Main Responsibilities
- Optionally create a share directory under `#σc/<mtpt>`.
- Optionally create a share descriptor file under that directory.
- Post the service with `postsrv`.
- Write the posted fd to the share descriptor.
- Close the service fd after publishing.

## Important Function
- `postsharesrv`: posts and shares a server by name, mount point, and descriptor.

## Dependencies and Interactions
- Uses `postsrv` from `post.c`.
- Uses Plan 9 synthetic share namespace path `#σc`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/share.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/srv.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/srv.c

## Read Status
Complete: 948 lines read.

## Purpose
Core lib9p 9P server engine. It reads 9P messages, manages request/fid lifetimes, dispatches protocol operations to server callbacks or default tree-backed handlers, writes responses, handles flushes, negotiates msize, and closes server resources.

## Main Responsibilities
- Read and decode 9P messages from `Srv.infd`.
- Allocate active `Req` objects keyed by tag.
- Dispatch all major 9P2000 messages: version, auth, attach, flush, walk, open, create, read, write, clunk, remove, stat, and wstat.
- Provide default behavior for tree-backed servers.
- Enforce fid state, open modes, directory rules, offset/count bounds, and permissions.
- Call server callback hooks where supplied.
- Perform response post-processing per message type.
- Serialize responses and write them to `Srv.outfd`.
- Handle delayed `Tflush` responses.
- Manage server worker references and cleanup.

## Important Functions
- `srv`: initializes formatters, pools, msize buffers, callbacks, forker, refs, and enters `srvwork`.
- `srvwork`: main read/dispatch loop.
- `getreq`: reads one 9P message, decodes it, allocates a request, and handles duplicate tags.
- `respond`: central response finalizer and writer; performs message-specific completion hooks.
- `responderror`: responds with current system error string.
- `walkandclone`: helper for callback-based walk/clone servers.
- `srvacquire`, `srvrelease`: external locking/reference helpers.
- `srvclose`: frees server buffers and pools after refs drain.

## Protocol Dispatch Helpers
- `sversion`/`rversion`: version negotiation and msize update.
- `sauth`/`rauth`: auth fid allocation and cleanup.
- `sattach`/`rattach`: attach fid allocation and tree root setup.
- `sflush`/`rflush`: flush lookup and delayed response handling.
- `swalk`/`rwalk`: fid walking, cloning, partial walk behavior, and default tree walks.
- `sopen`/`ropen`: permission checking, directory constraints, iounit calculation, and open state.
- `screate`: create prechecks and callback dispatch.
- `sread`/`rread`: read checks, iounit clamping, directory read support, diroffset update.
- `swrite`/`rwrite`: write checks and qid version bump.
- `sclunk`/`rclunk`: fid removal.
- `sremove`/`rremove`: remove permission and tree removal.
- `sstat`/`rstat`: stat preparation and serialized stat output.
- `swstat`/`rwstat`: wstat validation and callback dispatch.

## Dependencies and Interactions
- Uses `fid.c`, `req.c`, `file.c`, `uid.c`, and `mem.c`.
- Uses 9P serialization APIs: `read9pmsg`, `convM2S`, `convS2M`, `convD2M`, `convM2D`, `sizeD2M`.
- Uses Plan 9 locks, refs, setjmp/longjmp, and fcall/dir formatters.
- Tree-backed default behavior is activated when `srv->tree` is set.
- Callback-based behavior is activated through fields such as `auth`, `attach`, `walk`, `walk1`, `clone`, `open`, `create`, `read`, `write`, `remove`, `stat`, `wstat`, `flush`, `start`, `end`, `free`.

## Notes
- `Tversion` is only accepted while the request ref count indicates the first request.
- Response generation converts successful replies to request type + 1; errors become `Rerror`.
- `respond` closes/removes requests before writing responses for pooled requests, then releases flush waiters and request/server refs.
- Service concurrency is bounded with `sref`; workers can stop when the server has many refs and they are not the original process.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/thread.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/thread.c

## Read Status
Complete: 11 lines read.

## Purpose
Provides a thread/proc-library forker alternative for lib9p servers.

## Important Function
- `threadsrvforker`: runs a server function with `procrfork`, 32 KiB stack, and caller-supplied flags.

## Dependencies and Interactions
- Used by thread-prefixed wrappers to set `Srv.forker`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/thread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/threadlistensrv.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/threadlistensrv.c

## Read Status
Complete: 13 lines read.

## Purpose
Thread-style wrapper for network-listening 9P servers.

## Important Function
- `threadlistensrv`: installs `threadsrvforker` if no forker is set, then calls `listensrv`.

## Dependencies and Interactions
- Thin adapter around `listen.c` and `thread.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/threadlistensrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/threadpostmountsrv.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/threadpostmountsrv.c

## Read Status
Complete: 13 lines read.

## Purpose
Thread-style wrapper for posting and mounting a 9P server.

## Important Function
- `threadpostmountsrv`: installs `threadsrvforker` if needed, then calls `postmountsrv`.

## Dependencies and Interactions
- Thin adapter around `mount.c` and `thread.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/threadpostmountsrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/threadpostsharesrv.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/threadpostsharesrv.c

## Read Status
Complete: 13 lines read.

## Purpose
Thread-style wrapper for posting a shared 9P server.

## Important Function
- `threadpostsharesrv`: installs `threadsrvforker` if needed, then calls `postsharesrv`.

## Dependencies and Interactions
- Thin adapter around `share.c` and `thread.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/threadpostsharesrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/threadpostsrv.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/threadpostsrv.c

## Read Status
Complete: 13 lines read.

## Purpose
Thread-style wrapper for posting a 9P server.

## Important Function
- `threadpostsrv`: installs `threadsrvforker` if needed, then returns `postsrv`.

## Dependencies and Interactions
- Thin adapter around `post.c` and `thread.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/threadpostsrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/threadsrv.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/threadsrv.c

## Read Status
Complete: 13 lines read.

## Purpose
Thread-style wrapper for running a 9P server.

## Important Function
- `threadsrv`: installs `threadsrvforker` if needed, then calls `srv`.

## Dependencies and Interactions
- Thin adapter around `srv.c` and `thread.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/threadsrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/uid.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/uid.c

## Read Status
Complete: 33 lines read.

## Purpose
Provides simple permission checking for lib9p tree-backed files.

## Important Function
- `hasperm`: checks requested access bits against other, owner, and group permission bits.

## Behavior
- Starts with “other” permissions.
- Adds owner bits if `uid` matches `f->uid`.
- Adds group bits if `uid` matches `f->gid`.
- Assumes each user is the leader of their own group, as noted in the file comment.

## Dependencies and Interactions
- Used by `srv.c` to validate open, create, and remove behavior on tree-backed fids.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/uid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/util.c -->
# File Research: sources/os/plan9/9front/sys/src/lib9p/util.c

## Read Status
Complete: 24 lines read.

## Purpose
Provides simple read response helpers for static buffers and strings.

## Important Functions
- `readbuf`: copies a byte range from a buffer into `r->ofcall.data` according to request offset/count and clamps at EOF.
- `readstr`: calls `readbuf` for a NUL-terminated string.

## Dependencies and Interactions
- Intended for simple 9P read handlers serving static text or memory buffers.
- Sets `r->ofcall.count` but does not call `respond`; caller remains responsible for responding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/lib9p/util.c -->