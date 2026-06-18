# Research: subset-b-007010

Grouped research for Coda update-server, utility-library, recoverable-structure, and vcodacon monitor sources. Each source file section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/update/updatesrv.cc -->
# sources/distributed-fs/coda/coda-src/update/updatesrv.cc

## Purpose
`updatesrv.cc` is the Coda update server daemon. It listens on the update RPC2 subsystem, authenticates clients with the shared `db/update.tk` token, checks whether requested server database/configuration files have changed, and transfers changed regular files back to callers with RPC2 SmartFTP side effects.

## Important APIs, Types, And Functions
The daemon entry point is `main()`, with setup helpers `ReadConfigFile()` and `ReadExportList()`. `flist`, `namelist`, `checknames`, `InList()`, and `AccessAllowed()` implement the optional `db/files.export` allowlist and reject pathnames containing `..`. RPC callbacks include `Update_GetKeys()`, `Update_AuthFail()`, `UpdateNewConnection()`, and service method `UpdateFetch()`. `ServerLWP()` is the worker loop that calls `RPC2_GetRequest()` and dispatches `update_ExecuteRequest()`.

## Control Flow
Startup parses `-d`, `-l`, `-port`, and `-p`, loads `server.conf`, initializes `vice_config_path()` from `vicedir`, reads exported names, creates `misc`, detaches, redirects logs, changes to the serving prefix, writes `updatesrv.pid`, initializes LWP/RPC2/SFTP, exports `SUBSYS_UPDATE`, and spawns worker LWPs. Each worker waits for authenticated RPC2 requests, rejects open-kimono peers, executes update RPCs, logs failures, and unbinds bad connections. `UpdateFetch()` copies the requested name into a bounded buffer, checks access, stats the file, reports current server time, and only starts a SmartFTP server-to-client transfer when the file is regular and the caller's mtime differs.

## State And Persistence
Persistent external state is the Coda server tree under `vicedir`, especially `db/files.export`, `db/update.tk`, `misc/UpdateSrvLog`, and `misc/updatesrv.pid`. In-process state includes the export-name linked list, `prefix`, debug levels, token cache inside `secret_state`, and RPC2/LWP worker state. The daemon does not persist request history.

## Dependencies And Integration Points
This file integrates Coda's config layer, `vice_file` path construction, `getsecret`, RPC2, SmartFTP, LWP, service lookup, `update.h` generated stubs, and libutil logging/detach helpers. It is part of the server-to-server database update channel.

## Risks
Access control depends on a flat exact-name export list; if `files.export` is absent, all names under the working prefix are allowed. Path rejection only searches for adjacent dots and should not be treated as a full canonicalization layer. Worker creation passes the address of loop variable `i`, so logged worker ids can race. Token caching is mtime-based and the shared `secret_state` is static across workers. SmartFTP failures below `RPC2_ELIMIT` force unbinds, so transport errors can terminate sessions.

## Test Signals
Exercise startup with explicit/default ports, missing and populated `db/files.export`, bad and good `update.tk`, allowed and denied names, unchanged mtimes, changed regular files, missing files, `..` paths, multiple LWP workers, unauthenticated peers, SIGHUP/SIGUSR1/SIGQUIT behavior, and successful SmartFTP transfer completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/update/updatesrv.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/Makefile.am -->
# sources/distributed-fs/coda/coda-src/util/Makefile.am

## Purpose
This Automake fragment builds the private Coda utility library `libutil.la`, collecting generic containers, recoverable/RVM containers, logging, daemonization, paths, secrets, histograms, and small testsupport utilities used by Coda server and client programs.

## Important APIs, Types, And Functions
`noinst_LTLIBRARIES = libutil.la` makes the library internal to the build. `libutil_la_SOURCES` lists every source and public header in this subset, including `arrlist`, `bitmap`, `bitvect`, `bstree`, `dhash`, `dict`, `dlist`, `ohash`, `olist`, `rec_*`, `rvmlib`, `util`, `vice_file`, `vmindex`, and `bitmap7`. `AM_CPPFLAGS` pulls RVM/RPC2 flags and the base include directory.

## Control Flow
Automake expands this source list into compile and archive rules. Downstream `coda-src` programs link against `libutil.la` instead of rebuilding these primitives independently.

## State And Persistence
The file has no runtime state. Its build state is the membership of `libutil.la`, which controls which utility APIs are available to Coda components.

## Dependencies And Integration Points
It depends on configured `$(RVM_RPC2_CFLAGS)` and `lib-src/base` headers. Integration points include update server, volume/server code, RVM-backed metadata structures, and utility tests.

## Risks
Because headers and implementations are explicitly enumerated, adding a new utility file without updating this list will compile locally only if included elsewhere. RVM/RPC2 include flags are shared by many sources, so configuration drift can break unrelated utility builds.

## Test Signals
Run Automake/configure builds, verify `libutil.la` contains each listed object, build clients such as `updatesrv` and tests such as `proctest`, and test with RVM enabled/disabled configuration matrices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/arrlist.cc -->
# sources/distributed-fs/coda/coda-src/util/arrlist.cc

## Purpose
Implements `arrlist`, a simple growable array of unowned `void *` pointers, and `arrlist_iterator`, a sequential iterator over the populated prefix.

## Important APIs, Types, And Functions
Constructors call `init()` with either an explicit size or default 32. `Grow()` doubles capacity or adds a requested increase. `add()` appends one pointer. `arrlist_iterator::operator()()` returns the next stored pointer until `NULL`.

## Control Flow
Initialization allocates and zero-fills the pointer array. `add()` grows when `cursize >= maxsize`, stores the pointer at `list[cursize]`, and increments `cursize`. Iteration tracks a previous index and reads from `list[0..cursize)`.

## State And Persistence
State is process-local: `list`, `maxsize`, and `cursize`. The container owns only the array storage, not the pointed-to objects. No RVM or disk persistence is involved.

## Dependencies And Integration Points
Depends on `malloc/free`, `CODA_ASSERT`, and `arrlist.h`. It is a generic helper for older Coda code that wants a minimal pointer vector without templates.

## Risks
No copy constructor or assignment protection is defined, so accidental copying would shallow-copy ownership and double-free. Iterators are invalidated by mutation and explicitly do not support deleting current entries. Allocation failures assert rather than returning errors.

## Test Signals
Construct with zero, default, and custom sizes; append past capacity; verify preserved entries and zero-filled new slots; iterate exactly `cursize` elements; destroy empty and populated lists under leak checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/arrlist.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/arrlist.h -->
# sources/distributed-fs/coda/coda-src/util/arrlist.h

## Purpose
Declares the `arrlist` pointer-vector utility and its sequential iterator.

## Important APIs, Types, And Functions
`arrlist` exposes public fields `list`, `maxsize`, and `cursize`, plus `init()`, `Grow()`, constructors, destructor, and `add()`. `arrlist_iterator` stores the target list and previous index and implements `operator()()`.

## Control Flow
Callers create an `arrlist`, append with `add()`, and scan with `arrlist_iterator`. The iterator returns raw stored pointers and stops with `NULL`.

## State And Persistence
The header defines only in-memory state. It has no ownership contract for pointed-to objects and no persistent format.

## Dependencies And Integration Points
This is standalone C++ utility code and is included by code that needs a simple non-template dynamic pointer array.

## Risks
Public mutable fields make invariants easy to break. The iterator contract warns that deletion of the current entry is unsafe. Copying is not prohibited at the type level.

## Test Signals
Compile users against the declarations, verify ABI expectations for public fields, and run append/iteration tests with mutation avoided during scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/arrlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bitmap.cc -->
# sources/distributed-fs/coda/coda-src/util/bitmap.cc

## Purpose
Implements the original `bitmap` class for tracking allocation/free status of indexed elements, with optional RVM-backed allocation and mutation logging.

## Important APIs, Types, And Functions
Custom `operator new(size_t,int)` allocates either heap or recoverable memory. `Resize()`, `Grow()`, `GetFreeIndex()`, `SetIndex()`, `FreeIndex()`, range helpers, `CopyRange()`, `Value()`, `Count()`, `Size()`, `purge()`, assignment, inequality, and print methods provide bitmap operations.

## Control Flow
Construction infers whether the object came from custom `new`, records `recoverable`, allocates `mapsize = (inputmapsize + 7) >> 3`, and zeroes the map. Mutators call `rvmlib_set_range()` before changing recoverable bytes. `GetFreeIndex()` scans bytes for a zero bit, sets the high-to-low bit, and returns the index. Resize allocates a fresh map, copies overlapping bytes, frees the old map, and updates object fields.

## State And Persistence
State is `recoverable`, `malloced`, `mapsize`, and `map`. With `recoverable` set, object and map bytes live in RVM and must be changed inside transactions; otherwise they are ordinary heap state. `Size()` reports byte capacity times eight, not the originally requested logical index count.

## Dependencies And Integration Points
Depends on `rvmlib`, `util.h`, `CODA_ASSERT`, and C runtime allocation. It is used by Coda components that allocate ids or slots and can place the allocation bitmap in recoverable storage.

## Risks
The stack-vs-new detection is a historical hack and the destructor asserts the object was allocated via custom `new`. `CopyRange()` appears to call `SetValue()` on `this` instead of destination `b` in the all-bit path. `SetRangeValue()` uses `memset(..., value, ...)`, so a set range writes `0x01` rather than `0xff` for full bytes. Logical size is rounded up to whole bytes, so trailing spare bits can be allocated.

## Test Signals
Run `testbitmap`, allocation until full, resize grow/shrink, range set/free/copy on byte-aligned and unaligned ranges, recoverable transaction tests, destructor/purge paths, and checks that spare trailing bits do not leak into callers that expect exact logical size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bitmap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bitmap.h -->
# sources/distributed-fs/coda/coda-src/util/bitmap.h

## Purpose
Declares the original recoverable-capable `bitmap` class used to track occupied/free indices.

## Important APIs, Types, And Functions
The type defines allocation markers `BITMAP_NOTVIANEW` and `BITMAP_VIANEW`, bit constants `ALLOCMASK` and `HIGHBIT`, private `SetValue()` and `SetRangeValue()`, custom placement-like `new` with a recoverable flag, and public resize, allocation, range, count, assignment, comparison, purge, and print APIs.

## Control Flow
Callers allocate with `new bitmap(size, recable)` when heap or RVM ownership is needed, mutate bits through index/range APIs, and free with `delete` or `purge()`.

## State And Persistence
The declaration exposes no map internals but defines in-object flags that control heap versus RVM-backed persistence. Mutating APIs are annotated with transaction attributes where needed.

## Dependencies And Integration Points
Depends on `stdint.h`, `stdio.h`, and `coda_tsa.h` transaction annotations. The implementation binds it to `rvmlib`.

## Risks
The API reports rounded capacity, not an exact logical length. Copy/assignment and range operations require destination maps to be appropriately sized. The custom allocation contract is nonstandard and fragile for stack instances.

## Test Signals
Compile transaction-annotated callers, verify recoverable and nonrecoverable allocation, and exercise all index/range methods through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bitmap7.cc -->
# sources/distributed-fs/coda/coda-src/util/bitmap7.cc

## Purpose
Implements `bitmap7`, a revised bitmap that preserves the requested logical bit count in `indexsize` while retaining RVM-capable allocation semantics.

## Important APIs, Types, And Functions
The implementation mirrors `bitmap` with custom recoverable `new/delete`, `Resize()`, `Grow()`, `GetFreeIndex()`, `SetIndex()`, `FreeIndex()`, range methods, `CopyRange()`, `Value()`, `Count()`, `Size()`, `purge()`, assignment, inequality, and print helpers.

## Control Flow
Construction records both `mapsize` and `indexsize`. Resize creates a new zeroed map, copies overlapping bytes, frees the old map, updates `indexsize`, and clears bits from the logical end to the rounded byte end. Range copy/set calculate `end_bit`, `start_byte`, and `end_byte` to bulk-copy or bulk-fill whole bytes and handle edge bits individually. Recoverable operations log touched object/map ranges.

## State And Persistence
State is in-memory or RVM-backed depending on `recoverable`. `indexsize` is intended to make operations with `len < 0` stop at the logical end rather than the rounded storage end.

## Dependencies And Integration Points
Depends on `rvmlib`, `util.h`, transaction annotations, and C runtime allocation. It is likely intended as a safer replacement for `bitmap` in code that needs exact logical bounds.

## Risks
`GetFreeIndex()` still scans all rounded storage bits and can return an index beyond `indexsize` if trailing bits are free. `Size()` still returns `mapsize << 3` rather than `indexsize`. Assignment only updates `indexsize` when `mapsize` changes, so same-byte-size assignments with different logical sizes can leave stale logical length.

## Test Signals
Compare behavior against `bitmap`, especially non-multiple-of-eight sizes, grow/shrink cleanup, `len < 0` range operations, allocation at the logical end, recoverable mutation logging, and assignment between maps with equal `mapsize` but different `indexsize`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bitmap7.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bitmap7.h -->
# sources/distributed-fs/coda/coda-src/util/bitmap7.h

## Purpose
Declares `bitmap7`, the exact-size-aware variant of the Coda bitmap allocator.

## Important APIs, Types, And Functions
It adds `indexsize` to the original bitmap state, retains `recoverable`, `malloced`, `mapsize`, and `map`, and exposes the same custom allocation, index, range, copy, count, comparison, purge, and print interface as `bitmap`.

## Control Flow
Callers create a bitmap with a requested bit count, use index/range methods to mark occupancy, and can request recoverable storage through the second constructor/new argument.

## State And Persistence
The header distinguishes logical bit count from storage byte count. Recoverable mutations are marked with transaction annotations for RVM users.

## Dependencies And Integration Points
Includes `stddef.h`, `stdint.h`, `stdio.h`, and `coda_tsa.h`; implementation uses `rvmlib`.

## Risks
The public `Size()` contract can be ambiguous because implementation returns rounded storage capacity. The same custom allocation caveats as `bitmap` apply.

## Test Signals
Compile and run exact-size boundary tests, especially sizes 0, 1, 7, 8, and 9, plus recoverable construction and range updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bitmap7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bitvect.c -->
# sources/distributed-fs/coda/coda-src/util/bitvect.c

## Purpose
Provides a C bit-vector abstraction with LWP read/write locks for concurrent access to fixed-length bit sets.

## Important APIs, Types, And Functions
`struct Bitv_s` stores `length`, an array of `unsigned long` words, and a `Lock`. Public functions allocate/free, read length, count set bits, get/put/clear/set bits, find-and-set a free bit, and print the words.

## Control Flow
`Bitv_new()` allocates the struct, zeroes enough words for the requested length, and initializes the lock. Accessors take read locks; `Bitv_put()` and `Bitv_getfree()` take write locks. `Bitv_getfree()` scans words for a zero bit, sets it, and returns its global bit index.

## State And Persistence
State is heap-only and protected by the embedded LWP lock. It has no RVM persistence. `Bitv_free()` releases word storage and the struct but does not null out the caller's pointer.

## Dependencies And Integration Points
Depends on `lwp/lock.h`, libutil lock macros from `util.h`, `CODA_ASSERT`, and C allocation. It is a C alternative to the C++ bitmap classes.

## Risks
`Bitv_getfree()` and `Bitv_count()` examine all bits in the rounded last word, so indexes at or beyond `length` may be returned or counted. Shifts use literal `1`, which can overflow for bit positions beyond `int` width on wide `unsigned long`. `Bitv_free()` calls `PRE_EndCritical()` on NULL input, which is an unusual side effect.

## Test Signals
Create lengths around word boundaries, set/clear/get each valid bit, call `getfree()` until exhaustion, validate no out-of-range returns, run with multiple LWP readers/writers, and check lock/unlock balance under assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bitvect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bitvect.h -->
# sources/distributed-fs/coda/coda-src/util/bitvect.h

## Purpose
Declares the opaque C `Bitv` bit-vector API.

## Important APIs, Types, And Functions
`typedef struct Bitv_s *Bitv` hides implementation state. Functions are `Bitv_new`, `Bitv_free`, `Bitv_length`, `Bitv_count`, `Bitv_put`, `Bitv_clear`, `Bitv_set`, `Bitv_getfree`, and `Bitv_print`.

## Control Flow
Callers allocate a fixed-length vector, use bit operations by index, optionally find a free bit, print diagnostics, and free through `Bitv_free(&b)`.

## State And Persistence
The API promises heap-resident in-memory bit state only. Synchronization is implementation-owned.

## Dependencies And Integration Points
This header is standalone except for `FILE` being expected from includers or C library context. Implementation integrates with LWP locks and libutil.

## Risks
No declaration for `Bitv_get()` appears even though the implementation exports it, so callers without a prototype may be broken under modern C. Bounds semantics for `getfree()` are not described.

## Test Signals
Compile strict-prototype builds, exercise all declared functions, and verify callers that need `Bitv_get()` either include a declaration or fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bitvect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bstree.cc -->
# sources/distributed-fs/coda/coda-src/util/bstree.cc

## Purpose
Implements an intrusive binary search tree where user objects derive from `bsnode` and ordering is supplied by a callback.

## Important APIs, Types, And Functions
`bstree` implements `insert`, `remove`, `first`, `last`, `get`, `clear`, `count`, `IsMember`, `IsOrdered`, and printing. `bsnode` tracks its tree, parent, and children. `bstree_iterator` traverses ascending or descending.

## Control Flow
Insertion rejects nodes already in a tree, walks from the root using `CmpFn`, and breaks equal-key ties by object address. Removal uses standard BST splice logic, promoting the minimum node from the right subtree for two-child removals. `get()` removes min or max. Iteration starts at first/last and follows successor/predecessor links.

## State And Persistence
State is entirely intrusive: the tree owns only topology pointers and counters, not object memory. Statistics count inserts, removes, and gets. No persistence exists.

## Dependencies And Integration Points
Depends on `bstree.h`, C stdio/unistd/string, and caller-provided comparison functions. It is a base utility for sorted object registries in older Coda code.

## Risks
The tree is unbalanced, so sorted insertion can degrade to linear depth. Iterators are unsafe if the current node is deleted. Address tie-breaking makes ordering process-address-dependent. Destruction calls `clear()` and silently detaches nodes rather than deleting derived objects.

## Test Signals
Insert unique and duplicate-key nodes, remove leaf/one-child/two-child/root nodes, iterate in both orders, check `IsOrdered()`, clear populated trees, and run mutation-during-iteration tests to document unsafe cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bstree.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bstree.h -->
# sources/distributed-fs/coda/coda-src/util/bstree.h

## Purpose
Declares the intrusive binary search tree utility.

## Important APIs, Types, And Functions
`BSTCFN` is the comparison callback. `BstGetType` chooses min or max removal. `bstree`, `bsnode`, and `bstree_iterator` define the tree, embedded node base class, and traversal order.

## Control Flow
Callers derive objects from `bsnode`, provide a comparator, insert nodes, remove known nodes or min/max nodes, and scan with `bstree_iterator`.

## State And Persistence
Tree membership is stored inside each `bsnode` through private parent/child/tree pointers. The tree does not own derived objects or persist anything.

## Dependencies And Integration Points
Includes C `stdio.h` for print overloads and is consumed by C++ Coda utilities requiring sorted intrusive storage.

## Risks
Copy construction and assignment abort only at runtime. There is no balancing, locking, or safe-delete iterator contract. Derived destructors must ensure nodes are removed before object destruction.

## Test Signals
Compile derived-node users, validate comparator behavior, and test tree membership and ordering invariants after every operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/bstree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/daemonizer.c -->
# sources/distributed-fs/coda/coda-src/util/daemonizer.c

## Purpose
Implements daemon startup helpers: double-fork detachment, pidfile creation/locking, and a parent notification pipe for readiness.

## Important APIs, Types, And Functions
`daemonize()` forks into the background and returns the child-to-parent pipe fd to the final daemon. `update_pidfile()` writes and locks the pidfile. `gogogo()` writes a readiness byte to the parent. `check_child_completion()` waits in the original parent for that byte.

## Control Flow
`daemonize()` creates a pipe, forks; the parent waits for pipe readiness and exits with success/failure. The first child calls `setsid()`, changes to `/`, forks again, exits in the intermediate process, closes most fds in the final child, redirects stdin, and returns the pipe writer. `update_pidfile()` opens/locks/truncates/writes the pid and keeps the lock fd open. `gogogo()` sends the readiness byte and closes the pipe.

## State And Persistence
Persistent state is the pidfile and, on Cygwin, a companion `.lk` lockfile. In-process static fd state keeps locks alive. No other daemon state is persisted.

## Dependencies And Integration Points
Depends on Unix process, fd, select, and `coda_flock` portability wrappers. Used by Coda daemons that want controlled background startup.

## Risks
If the daemon never calls `gogogo()`, the launching parent blocks indefinitely. Only stdin is redirected; stdout/stderr remain caller-managed. `daemonize()` closes fds up to `FD_SETSIZE`, which may miss higher descriptors. Pid string assumes pid fits in 10 characters plus newline.

## Test Signals
Start daemons that call and omit `gogogo()`, verify parent exit codes, pidfile locking prevents duplicate starts, Cygwin lockfile path behavior, closed fd inheritance, working directory `/`, and stdout/stderr redirection by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/daemonizer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/daemonizer.h -->
# sources/distributed-fs/coda/coda-src/util/daemonizer.h

## Purpose
Declares daemonization and pidfile helpers for Coda daemons.

## Important APIs, Types, And Functions
The public C API is `daemonize()`, `update_pidfile(const char *)`, and `gogogo(int)`.

## Control Flow
Callers typically call `daemonize()`, perform initialization, call `update_pidfile()`, redirect logs as desired, then call `gogogo(parent_fd)` when ready.

## State And Persistence
The API manages pidfile and lockfile state through the implementation; no state is visible in the header.

## Dependencies And Integration Points
The header is C/C++ compatible and used by daemon programs across the Coda tree.

## Risks
Readiness notification is caller-driven, so incorrect ordering can report success before the service is actually listening or leave the parent blocked.

## Test Signals
Compile from C and C++, run daemon startup success/failure paths, and verify pidfile lock lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/daemonizer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/dhash.cc -->
# sources/distributed-fs/coda/coda-src/util/dhash.cc

## Purpose
Implements `dhashtab`, a fixed-size power-of-two hash table whose buckets are sorted or unsorted intrusive `dlist` instances.

## Important APIs, Types, And Functions
The constructor takes a bucket count, hash function, and dlist comparison function. Operations are `insert`, `prepend`, `append`, `remove`, `first`, `last`, `get`, `clear`, `count`, `IsMember`, `bucket`, `print`, and `dhashtab_iterator`.

## Control Flow
Construction verifies the requested size is already a power of two, allocates a `dlist` array, and assigns each bucket's comparison callback. Operations compute `hfn(key) & (sz - 1)` and delegate to the chosen bucket. Iterators can scan one bucket or all buckets in ascending/descending bucket order.

## State And Persistence
State is the bucket array, hash callback, and total count. Entries are caller-owned intrusive `dlink` objects. No persistence is provided.

## Dependencies And Integration Points
Depends on `dhash.h` and `dlist.h`. Used when Coda needs hash lookup combined with dlist ordering within buckets.

## Risks
`remove()` and `get()` decrement `cnt` unconditionally even when the bucket does not contain the requested object or is empty for that key. Table size must be a power of two, otherwise construction aborts. There is no resizing or locking.

## Test Signals
Construct invalid and valid sizes, insert into multiple buckets, remove present and absent entries, check count integrity, iterate all/single buckets in both orders, and clear populated tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/dhash.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/dhash.h -->
# sources/distributed-fs/coda/coda-src/util/dhash.h

## Purpose
Declares the intrusive doubly-linked hash table.

## Important APIs, Types, And Functions
`dhashtab` owns an array of `dlist` buckets and exposes insertion variants, removal, min/max-style bucket get, membership, bucket computation, printing, and counting. `DhIterOrder` and `dhashtab_iterator` support table or bucket scans.

## Control Flow
Callers provide a hash function and optional bucket comparator, insert `dlink`-derived objects under a key, and iterate by key or whole table.

## State And Persistence
Only bucket topology and counts are stored. Objects remain caller-owned and in-memory only.

## Dependencies And Integration Points
Depends on `dlist.h`; it is a C++ utility primitive for Coda's object registries.

## Risks
The API requires stable keys and intrusive link ownership discipline. It has no type safety, resizing, or synchronization.

## Test Signals
Compile users with custom hash/comparison callbacks and validate count, bucket, membership, and iterator behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/dhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/dict.cc -->
# sources/distributed-fs/coda/coda-src/util/dict.cc

## Purpose
Implements an abstract dictionary layer on top of `dlist`, adding reference counting and delayed destruction for `assoc` entries plus `assocrefs` arrays of held references.

## Important APIs, Types, And Functions
`dictionary::Add`, `Remove`, `Find`, `Put`, and `Kill` manage entries. `assoc::Hold`, `Release`, and `Suicide` manage reference lifetime. `assocrefs::Attach`, `Detach`, `Kill`, `Index`, and `assocrefs_iterator` manage arrays of references to associations.

## Control Flow
An `assoc` constructor records its dictionary, inserts itself, starts with refcount 1, and is not dying. `Find()` scans the list, compares keys, holds the found object, and returns it. `Put()` releases and nulls a caller reference. `Suicide()` marks an entry dying; the final `Release()` removes it from the dictionary and deletes it. `assocrefs` grows its pointer array, holds attached assocs, and releases or suicides references during detach/kill.

## State And Persistence
State is in-memory reference counts, dying flags, key/value pointers, dictionary membership, and reference arrays. No persistent storage or locking is provided.

## Dependencies And Integration Points
Depends on `dict.h`, `dlist`, and `CODA_ASSERT`. It is intended for old Coda subsystems with object dictionaries and cross-reference sets.

## Risks
The package is explicitly not multithread-capable. `assocrefs::Detach(0)` and `Kill(0)` dereference `Assoc` in the all-case path instead of `assocs[i]`, which is a serious null-pointer bug if used. The base `assoc` destructor asserts, so every concrete derived class must implement a virtual destructor. Array growth zeroing after `realloc` appears to use `max - ActualGrowSize` as a byte offset, which can clear the wrong region.

## Test Signals
Create derived key/value/assoc types, find/put/kill entries, verify delayed deletion after outstanding refs, attach/detach indexed refs, test all-reference operations, and run under sanitizers for null and realloc clearing bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/dict.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/dict.h -->
# sources/distributed-fs/coda/coda-src/util/dict.h

## Purpose
Declares an abstract reference-counted dictionary framework.

## Important APIs, Types, And Functions
Core classes are `dictionary`, `assockey`, `assocval`, `assoc`, `assocrefs`, and `assocrefs_iterator`. `dictionary` inherits privately from the intrusive list implementation through its public base and uses `assoc` entries that privately derive from `dlink`.

## Control Flow
Derived assoc objects provide concrete keys/values, insert themselves into a dictionary at construction, are held by lookups and reference arrays, and are physically deleted only after suicide plus final release.

## State And Persistence
The declarations define in-memory object relationships only. Persistence, locking, and key storage are left to derived users.

## Dependencies And Integration Points
Depends on `coda_assert` and `dlist.h`. It is a reusable base for typed dictionaries elsewhere in Coda.

## Risks
Many required operations are enforced by runtime assertions instead of compile-time abstract pure virtuals. Users must respect the hold/release protocol exactly to avoid leaks or premature deletion.

## Test Signals
Compile concrete subclasses, check key equality dispatch, reference count transitions, iterator index reporting, and dictionary removal on last release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/dict.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/dlist.cc -->
# sources/distributed-fs/coda/coda-src/util/dlist.cc

## Purpose
Implements an intrusive circular doubly-linked list with optional sorted insertion.

## Important APIs, Types, And Functions
`dlist` provides `insert`, `prepend`, `append`, `remove`, `first`, `last`, `get`, `clear`, `count`, `IsMember`, and print methods. `dlist_iterator` traverses ascending or descending. `dlink` is the embedded base object.

## Control Flow
Insertion rejects already-linked nodes, then either initializes a singleton circular list or splices around `head`/tail. Sorted insertion walks with `CmpFn` until the new node should precede the current node. Removal rewires predecessor/successor links and resets the removed node. Iteration starts at head or tail and stops after wrapping.

## State And Persistence
The list stores `head`, `cnt`, and comparator. Each node stores `next`/`prev`. It does not own or delete derived objects and has no persistence.

## Dependencies And Integration Points
Depends on `dlist.h`, `coda_assert`, and POSIX `write()` for diagnostics. Hash tables reuse `dlist` buckets and friend access to set `CmpFn`.

## Risks
The iterator is unsafe for deletion of the current entry. `remove()` assumes a non-empty list and a linked node; removing a node not on this list can corrupt memory. Destruction clears membership but does not free containing objects.

## Test Signals
Append/prepend/insert sorted objects, remove head/tail/middle/singleton, detect double insertion aborts, iterate both directions, clear lists, and validate behavior with null comparator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/dlist.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/dlist.h -->
# sources/distributed-fs/coda/coda-src/util/dlist.h

## Purpose
Declares the intrusive circular doubly-linked list primitive.

## Important APIs, Types, And Functions
`CFN` is the ordering callback. `DlGetType` selects head/tail removal. `dlist`, `dlist_iterator`, and `dlink` define container, traversal, and embedded link state.

## Control Flow
Callers derive from `dlink`, add objects to one list at a time, remove explicitly or through `get()`, and traverse with an iterator.

## State And Persistence
Membership state lives in private `next` and `prev` pointers inside each `dlink`. There is no persistence or ownership of derived objects.

## Dependencies And Integration Points
Includes `stdio.h` for print overloads and is used by `dhash`, `dict`, and many Coda intrusive structures.

## Risks
The `is_linked()` check only tests `next != NULL`; damaged half-linked nodes are possible if users mutate internals indirectly. No locking or safe-delete iteration is provided.

## Test Signals
Compile derived classes, verify one-list-at-a-time enforcement, ordering callback behavior, and print diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/dlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/getsecret.cc -->
# sources/distributed-fs/coda/coda-src/util/getsecret.cc

## Purpose
Implements helpers for turning token files or random bytes into RPC2 encryption keys.

## Important APIs, Types, And Functions
`HashSecret()` MD5-hashes arbitrary bytes into an `RPC2_EncryptionKey`. `GetSecret()` reads a token file, caches the derived key in `secret_state`, and refreshes on mtime changes. `GenerateSecret()` fills a key with `rpc2_NextRandom()` bytes.

## Control Flow
`GetSecret()` stats the file, compares `statbuf.st_mtime` with cached `state->mtime`, reads up to 512 bytes when stale, hashes the bytes, and updates the cached mtime unless the file was modified in the current second. It then copies the cached key to the caller.

## State And Persistence
Persistent input is the token file. In-process cache state is `secret_state::mtime` and `secret_state::key`. No lock protects shared state.

## Dependencies And Integration Points
Depends on RPC2 key types/randomness, Coda MD5 wrappers, logging through `LogMsg`/`SrvDebugLevel`, and file I/O. `updatesrv` uses it for update-token authentication.

## Risks
MD5 is legacy cryptography; this code derives fixed-size RPC2 keys rather than modern password hashes. Reads are capped at 512 bytes. Shared `secret_state` use across concurrent workers would need external synchronization. Mtime granularity can delay cache refresh by design.

## Test Signals
Read missing/unreadable token files, token changes across same-second and later mtimes, binary token contents, exact 512-byte files, generated secrets, and authentication success/failure in RPC2 users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/getsecret.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/getsecret.h -->
# sources/distributed-fs/coda/coda-src/util/getsecret.h

## Purpose
Declares RPC2 secret hashing, token-file loading, and random key generation helpers.

## Important APIs, Types, And Functions
`HashSecret()`, `GetSecret()`, `GenerateSecret()`, and `struct secret_state` are the public contract. `secret_state` stores cached file mtime and key bytes.

## Control Flow
Callers pass a token file and persistent state to `GetSecret()`; the implementation refreshes the key only when the file's mtime changes.

## State And Persistence
The header defines caller-owned cache state. The token file is the durable secret source.

## Dependencies And Integration Points
Includes `rpc2/rpc2.h` and C system types. Used by RPC2-authenticated Coda daemons.

## Risks
Callers must initialize `secret_state` and serialize access if used across threads. The API exposes no key length negotiation beyond `RPC2_KEYSIZE`.

## Test Signals
Compile C and C++ callers, initialize zeroed state, and verify cached and refreshed token behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/getsecret.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/histo.c -->
# sources/distributed-fs/coda/coda-src/util/histo.c

## Purpose
Implements numeric histograms with linear, log2, or log10 bucket layouts, summary statistics, and plotting text output.

## Important APIs, Types, And Functions
`InitHisto()` allocates and initializes buckets. `ClearHisto()` resets counts and sums. `UpdateHisto()` and `MUpdateHisto()` add samples. `PrintHisto()` prints mean/stddev/90% confidence interval and populated buckets. `PlotHisto()` emits a graph description with histogram points.

## Control Flow
Initialization validates limits and log constraints, derives bucket boundaries, allocates `histo` buckets, and calls `ClearHisto()`. Updates route values to underflow, overflow, or first bucket with `newval < hival`, updating count/sum/sum2 for in-range samples. Printing derives statistics from accumulated sums and emits textual ranges.

## State And Persistence
State is heap-allocated bucket arrays and counters in caller-owned `hgram`. There is no free function in this file, so callers must manage `hg->buckets` lifetime.

## Dependencies And Integration Points
Depends on `math.h`, `stdio`, `stdlib`, `coda_assert`, and `histo.h`. Used for performance or behavior distributions in diagnostics.

## Risks
`PlotHisto()` divides by `totalcount` without guarding zero populated buckets. Confidence factors index a static table for low degrees of freedom. Linear initialization does not reject nonpositive `bucketcount`. Updates use linear bucket search.

## Test Signals
Initialize valid/invalid linear/log histograms, add underflow/overflow/in-range samples, clear and reuse, print one and many samples, plot empty/nonempty histograms, and check bucket boundary inclusivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/histo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/histo.h -->
# sources/distributed-fs/coda/coda-src/util/histo.h

## Purpose
Declares histogram data structures and functions for linear and logarithmic distributions.

## Important APIs, Types, And Functions
`enum htype` defines `LINEAR`, `LOG2`, and `LOG10`. `struct histo` stores one bucket range and count. `struct hgram` stores buckets, underflow/overflow buckets, counts, and sums. Public functions initialize, clear, update, print, and plot.

## Control Flow
Callers allocate an `hgram`, call `InitHisto()`, update with samples, and print or plot the collected distribution.

## State And Persistence
State is caller-owned and heap-backed through the `buckets` pointer. No persistence is implied.

## Dependencies And Integration Points
Macros require `pow()` from libm in users of the header. The implementation links with math functions.

## Risks
The header does not expose a destructor/free API for bucket storage. `char *` plot labels are mutable in the prototype even though callers may pass literals.

## Test Signals
Compile with libm, verify all public functions, and check memory ownership conventions in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/histo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/mkpath.c -->
# sources/distributed-fs/coda/coda-src/util/mkpath.c

## Purpose
Creates the directory path leading to a file name, similar to a recursive `mkdir -p` for parent directories only.

## Important APIs, Types, And Functions
`mkpath(const char *name, mode_t mode)` is the single function. It finds the last slash, temporarily truncates the string there, recursively ensures the parent path, and creates the current directory.

## Control Flow
If there is no slash, the function succeeds. Otherwise it replaces the last slash with NUL, stats the parent path, restores the slash on each return path, checks existing paths are directories, recurses for missing parents, and calls `mkdir()` for the final parent.

## State And Persistence
Persistent state is the filesystem directories created with `mode`. There is no global state.

## Dependencies And Integration Points
Depends on `string.h`, `errno.h`, `sys/stat.h`, and recursive filesystem calls. Used by Coda utilities that need to ensure parent directories before file creation.

## Risks
The prototype takes `const char *` but the implementation mutates the buffer in place; passing a string literal or read-only memory is unsafe. Concurrent creators can make `mkdir()` return `EEXIST`, which is treated as failure. Absolute root and trailing slash edge cases need care.

## Test Signals
Pass mutable paths with no parent, existing parent, nested missing parents, parent component that is a file, absolute paths, trailing slashes, concurrent creation, and read-only string inputs under sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/mkpath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/mkpath.h -->
# sources/distributed-fs/coda/coda-src/util/mkpath.h

## Purpose
Declares the recursive parent-directory creation helper.

## Important APIs, Types, And Functions
`int mkpath(const char *name, mode_t mode)` returns 0 on success and -1 with `errno` set on failure.

## Control Flow
Callers invoke it before creating a file to ensure the containing directory hierarchy exists.

## State And Persistence
The API affects filesystem directory state through the implementation.

## Dependencies And Integration Points
Requires `mode_t` to be visible from included system headers. Used by C and C++ code.

## Risks
The `const` qualifier does not match implementation behavior, which temporarily writes into `name`.

## Test Signals
Compile users with proper `mode_t` includes and test mutable path buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/mkpath.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/ohash.cc -->
# sources/distributed-fs/coda/coda-src/util/ohash.cc

## Purpose
Implements `ohashtab`, a fixed-size power-of-two hash table backed by intrusive singly-linked `olist` buckets.

## Important APIs, Types, And Functions
Public operations are `insert`, `append`, `remove`, `first`, `last`, `get`, `clear`, `count`, `IsMember`, `FindObject`, `bucket`, print methods, and `ohashtab_iterator`.

## Control Flow
Construction validates a power-of-two size, allocates bucket lists, and stores the hash function. Operations hash the key with `hfn(key) & (sz - 1)` and delegate to that bucket. `FindObject()` hashes one key but compares an arbitrary tag through the bucket's object tag matcher. Iteration scans one bucket or all buckets in ascending order.

## State And Persistence
State is in-memory bucket array, count, and hash callback. Entries are caller-owned `olink` objects and can be on only one list at a time.

## Dependencies And Integration Points
Depends on `ohash.h` and `olist.h`. Used for lightweight intrusive hash maps where sorted buckets are unnecessary.

## Risks
`remove()` and `get()` decrement count unconditionally even when no object is removed. `get()` does not check table count before removing from a possibly empty bucket. No resizing, locking, or type safety exists.

## Test Signals
Insert/remove present and absent entries, verify count integrity, use `FindObject()` with separate key/tag fields, iterate single/all buckets, and reject non-power-of-two sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/ohash.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/ohash.h -->
# sources/distributed-fs/coda/coda-src/util/ohash.h

## Purpose
Declares the intrusive singly-linked hash table.

## Important APIs, Types, And Functions
`ohashtab` owns `olist` buckets and exposes head/tail insertion, removal, first/last/get, clear, count, membership, `FindObject()`, bucket calculation, and printing. `ohashtab_iterator` scans one bucket or all buckets.

## Control Flow
Callers provide a hash function, store `olink`-derived objects under keys, and optionally search by tag within a key's bucket.

## State And Persistence
All state is process-local. Object ownership remains with callers.

## Dependencies And Integration Points
Includes `stdint.h`, `stdio.h`, and `olist.h`. It complements `dhash` for cheaper bucket linkage.

## Risks
Keys must remain stable while objects are in the table. There is no dynamic resizing or synchronization.

## Test Signals
Compile with pointer/integer hash callbacks, validate bucket selection, tag lookup, and iterator behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/ohash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/olist.cc -->
# sources/distributed-fs/coda/coda-src/util/olist.cc

## Purpose
Implements an intrusive circular singly-linked list with tail pointer, head insertion, tail append, removal, tag search, and iteration.

## Important APIs, Types, And Functions
`olist` provides `insert`, `append`, `remove`, `first`, `last`, `get`, `clear`, `count`, `IsMember`, `FindObject`, and print methods. `olist_iterator` scans the circular list. `olink` is the embedded link base and supports `otagmatch()`.

## Control Flow
Insertion and append reject already-linked objects, initialize singleton lists by pointing a node to itself, or splice after tail. Removal walks from tail to find the predecessor, rewires links, resets `p->next`, and updates tail. Iteration begins at `tail->next` and stops after returning tail.

## State And Persistence
State is `tail`, `cnt`, and each node's `next` pointer. The list does not own derived objects and has no persistence.

## Dependencies And Integration Points
Depends on `olist.h`, `coda_assert`, and POSIX writes for diagnostics. `ohash` and other utilities use it as an intrusive bucket/list primitive.

## Risks
Current-entry deletion is explicitly unsafe for the iterator. `FindObject()` relies on caller-provided compare functions and `olink::otagmatch()` passes `(this, tag)` despite comments implying tag/object order. Copy constructor and assignment abort at runtime.

## Test Signals
Insert/append/remove singleton, head, tail, and middle nodes; search by tag; iterate to exactly tail; clear lists; and verify double insertion aborts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/olist.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/olist.h -->
# sources/distributed-fs/coda/coda-src/util/olist.h

## Purpose
Declares the intrusive circular singly-linked list utility.

## Important APIs, Types, And Functions
`otagcompare_t` supports tag matching. `olist`, `olist_iterator`, and `olink` provide list operations, traversal, embedded link state, and tag matching.

## Control Flow
Objects derive from `olink`, enter one list with `insert()` or `append()`, leave through `remove()` or `get()`, and are scanned with `olist_iterator`.

## State And Persistence
Only in-memory next pointers and a tail pointer are stored. Derived object lifetime remains external.

## Dependencies And Integration Points
Includes `stdio.h`; used by `ohash` and recoverable-list analogues.

## Risks
No compile-time prevention of copying, no locking, and no safe-delete iterator guarantee.

## Test Signals
Compile derived users and run list membership, tag matching, and iterator reset tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/olist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_bstree.cc -->
# sources/distributed-fs/coda/coda-src/util/rec_bstree.cc

## Purpose
Implements the recoverable/RVM-backed analogue of `bstree`, preserving intrusive tree mutations transactionally.

## Important APIs, Types, And Functions
`rec_bstree` supports recoverable `new/delete`, `Init`, `DeInit`, `SetCmpFn`, `ClearStatistics`, `insert`, `remove`, `first`, `last`, `get`, `count`, `IsMember`, `IsOrdered`, and printing. `rec_bsnode` is the embedded recoverable node. `rec_bstree_iterator` traverses in order.

## Control Flow
The algorithm matches `bstree`: unbalanced insertion by comparator with address tie-breaks, splice-based removal, min/max get, and successor/predecessor iteration. Every persistent pointer/count/stat mutation is preceded by `RVMLIB_REC_OBJECT()` when `RvmType` requires logging.

## State And Persistence
Tree and node topology can live in RVM through `rvmlib_rec_malloc` and transaction range logging. Compare-function pointers may be nonrecoverable and can be reset outside a transaction when needed.

## Dependencies And Integration Points
Depends on `rec_bstree.h`, `rvmlib`, and ordinary `bstree` enums. Used by Coda metadata structures that need recoverable sorted indexes.

## Risks
All structural mutations require an active transaction for RAWIO/UFS RVM modes. Like the ordinary tree, it is unbalanced and iterator deletion is unsafe. Function pointers are not persistent data and must be restored after restart or reinitialization.

## Test Signals
Run insert/remove/get/order tests inside RVM transactions, simulate abort/recovery, reset comparison function after restart, verify statistics clearing persists, and compare behavior with ordinary `bstree`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_bstree.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_bstree.h -->
# sources/distributed-fs/coda/coda-src/util/rec_bstree.h

## Purpose
Declares the recoverable intrusive binary search tree.

## Important APIs, Types, And Functions
`RBSTCFN`, `rec_bstree`, `rec_bsnode`, and `rec_bstree_iterator` mirror the ordinary tree with transaction annotations and recoverable allocation operators.

## Control Flow
Callers allocate/initialize a recoverable tree, derive objects from `rec_bsnode`, mutate inside transactions, and restore nonpersistent comparator functions when needed.

## State And Persistence
Tree topology and counters are intended for RVM persistence. Comparator pointers are explicitly treated as potentially nonrecoverable.

## Dependencies And Integration Points
Includes `bstree.h` for shared enums and `rvmlib.h` for RVM APIs.

## Risks
Using the API outside transactions in persistent modes can fail assertions. Node lifetime and one-tree membership are caller responsibilities.

## Test Signals
Compile with transaction annotations, allocate from RVM, and validate recovery of topology after committed transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_bstree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_dhash.cc -->
# sources/distributed-fs/coda/coda-src/util/rec_dhash.cc

## Purpose
Implements a recoverable hash table with `rec_dlist` buckets for RVM-backed intrusive objects.

## Important APIs, Types, And Functions
`rec_dhashtab` provides recoverable allocation, `Init`, `DeInit`, `SetHFn`, `SetCmpFn`, insertion variants, `remove`, `first`, `last`, `get`, `count`, `IsMember`, `bucket`, print, and `rec_dhashtab_iterator`.

## Control Flow
Initialization validates power-of-two size, allocates a recoverable array of `rec_dlist`, and initializes each bucket. Operations log the table object, hash the key, delegate to a bucket, and update `cnt`. Iteration wraps `rec_dlist_iterator` and can scan all buckets in ascending or descending order.

## State And Persistence
The table object and bucket array are RVM allocated. Structural changes are transaction logged. Hash and comparison function pointers are not inherently persistent and can be reset.

## Dependencies And Integration Points
Depends on `rec_dhash.h`, `rec_dlist`, and `rvmlib`. Used for persistent object indexes with doubly-linked bucket ordering.

## Risks
`remove()` and `get()` decrement `cnt` unconditionally like the nonrecoverable version. `DeInit()` requires empty buckets and frees the bucket array transactionally. Function pointers must be reinstalled after restart if addresses change.

## Test Signals
Transactionally insert/remove entries, verify count after failed removes, iterate across buckets, run commit/abort recovery tests, and check `SetHFn`/`SetCmpFn` after process restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_dhash.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_dhash.h -->
# sources/distributed-fs/coda/coda-src/util/rec_dhash.h

## Purpose
Declares the recoverable doubly-linked hash table.

## Important APIs, Types, And Functions
`RHFN`, `rec_dhashtab`, and `rec_dhashtab_iterator` mirror `dhashtab` with `rec_dlink` entries, `rec_dlist` buckets, recoverable allocation, and transaction annotations.

## Control Flow
Persistent callers initialize with power-of-two bucket count and callbacks, mutate inside transactions, and iterate by key or whole table.

## State And Persistence
Bucket topology and counts are intended to persist in RVM. Callback addresses are process state.

## Dependencies And Integration Points
Includes `dhash.h`, `rec_dlist.h`, and `rvmlib.h`.

## Risks
Requires strict transaction discipline and stable key hashing. No resizing or synchronization exists.

## Test Signals
Compile RVM users, test power-of-two validation, and verify committed bucket changes survive recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_dhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_dlist.cc -->
# sources/distributed-fs/coda/coda-src/util/rec_dlist.cc

## Purpose
Implements a recoverable circular doubly-linked intrusive list.

## Important APIs, Types, And Functions
`rec_dlist` supports recoverable allocation, `Init`, `DeInit`, `SetCmpFn`, `insert`, `prepend`, `append`, `remove`, `first`, `last`, `get`, `count`, `IsMember`, and printing. `rec_dlink` has `Init()` and print helpers. `rec_dlist_iterator` scans ascending/descending.

## Control Flow
List algorithms match `dlist`, but every changed list/link object is logged with `RVMLIB_REC_OBJECT()`. `SetCmpFn()` conditionally logs when a transaction exists because callback pointers may be volatile process state.

## State And Persistence
The list head/count and link next/prev pointers are recoverable state. Derived objects embedding `rec_dlink` are expected to live in recoverable storage when persistence is desired.

## Dependencies And Integration Points
Depends on `rec_dlist.h` and `rvmlib`. Used by recoverable hash tables and Coda RVM metadata lists.

## Risks
`DeInit()` aborts when entries remain. Mutations require transactions. Iteration is not safe for deleting the current node. Comparator pointer persistence must be managed by callers.

## Test Signals
Run all ordinary `dlist` operations inside transactions, verify RVM abort rolls back topology, call `DeInit()` on empty/nonempty lists, and test comparator reset after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_dlist.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_dlist.h -->
# sources/distributed-fs/coda/coda-src/util/rec_dlist.h

## Purpose
Declares the recoverable intrusive doubly-linked list.

## Important APIs, Types, And Functions
`RCFN`, `rec_dlist`, `rec_dlist_iterator`, and `rec_dlink` mirror ordinary `dlist` types with transaction annotations and RVM allocation operators.

## Control Flow
Callers initialize a list, insert `rec_dlink`-derived objects inside transactions, remove/get entries, and iterate in either order.

## State And Persistence
List topology and counters are designed for RVM persistence. The comparison callback is process state.

## Dependencies And Integration Points
Includes `dlist.h` for shared enums and `rvmlib.h`.

## Risks
Using stack or nonrecoverable embedded links with recoverable lists can make recovery invalid. There is no locking.

## Test Signals
Compile transaction-annotated users and validate persisted head/tail/count behavior after recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_dlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_ohash.cc -->
# sources/distributed-fs/coda/coda-src/util/rec_ohash.cc

## Purpose
Implements a recoverable hash table with singly-linked `rec_olist` buckets.

## Important APIs, Types, And Functions
`rec_ohashtab` provides recoverable allocation, `Init`, `DeInit`, `SetHFn`, `insert`, `append`, `remove`, `first`, `last`, `get`, `count`, `IsMember`, `bucket`, print, and `rec_ohashtab_iterator` with `Reset()`.

## Control Flow
Initialization logs the table, validates power-of-two size, allocates recoverable bucket storage, and initializes each `rec_olist`. Mutators log the table, hash keys to buckets, delegate list changes, and update count. Iteration walks one bucket or all buckets in increasing order.

## State And Persistence
Bucket array, list topology, and count can be RVM persistent. Hash function pointer is process-local and can be reset.

## Dependencies And Integration Points
Depends on `rec_ohash.h`, `rec_olist`, and `rvmlib`. Used where persistent hash lookup does not need doubly-linked bucket ordering.

## Risks
`remove()` and `get()` decrement `cnt` even if no object is returned. `DeInit()` frees buckets but does not explicitly clear all fields. Function pointer restoration is required after restart.

## Test Signals
Transactionally add/remove/get entries, verify count integrity, reset iterator, recover after commit/abort, and compare behavior against `ohash`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_ohash.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_ohash.h -->
# sources/distributed-fs/coda/coda-src/util/rec_ohash.h

## Purpose
Declares the recoverable singly-linked hash table.

## Important APIs, Types, And Functions
`rec_ohashtab` stores `rec_olist` buckets and exposes hash-table operations with RVM allocation and transaction annotations. `rec_ohashtab_iterator` supports bucket or whole-table scans and reset.

## Control Flow
Callers initialize with a power-of-two bucket count and hash function, mutate in transactions, and iterate over persistent `rec_olink` entries.

## State And Persistence
Hash topology and count are persistent-capable; callback pointer state is not durable.

## Dependencies And Integration Points
Includes `ohash.h`, `rec_olist.h`, and `rvmlib.h`.

## Risks
No resizing, no synchronization, and no type safety. Key hash function must be restored consistently.

## Test Signals
Compile RVM callers and verify bucket choice, iteration, and recovery of committed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_ohash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_olist.cc -->
# sources/distributed-fs/coda/coda-src/util/rec_olist.cc

## Purpose
Implements the recoverable singly-linked circular intrusive list.

## Important APIs, Types, And Functions
`rec_olist` supports recoverable allocation, `Init`, `DeInit`, `insert`, `append`, `remove`, `first`, `last`, `get`, `count`, `IsMember`, and printing. `rec_olink` has recoverable `Init()` and print helpers. `rec_olist_iterator` scans the list.

## Control Flow
List operations mirror `olist` but log the list, tail, predecessor, and changed node before pointer/count updates. `remove()` walks predecessor links from tail and handles singleton tail removal. `get()` removes the head.

## State And Persistence
`tail`, `cnt`, and each link's `next` pointer can be RVM persistent. No derived objects are freed by the list.

## Dependencies And Integration Points
Depends on `rec_olist.h`, `rvmlib`, and POSIX writes. Used by `rec_ohash` and persistent Coda structures.

## Risks
`DeInit()` aborts if nonempty. Iterator comments claim safe deletion support, but it does not precompute the next link, unlike `rec_smolist_iterator`; deleting current entries can still be risky. All mutations require transactions.

## Test Signals
Transactionally insert/append/remove/get singleton and multi-entry lists, test current-entry deletion behavior, verify abort recovery, and ensure `DeInit()` catches nonempty lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_olist.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_olist.h -->
# sources/distributed-fs/coda/coda-src/util/rec_olist.h

## Purpose
Declares the recoverable intrusive singly-linked list.

## Important APIs, Types, And Functions
`rec_olist`, `rec_olist_iterator`, and `rec_olink` mirror `olist` with RVM allocation and transaction annotations.

## Control Flow
Callers initialize or allocate lists in recoverable storage, insert and remove `rec_olink` objects inside transactions, and scan with an iterator.

## State And Persistence
The tail pointer, count, and link pointers are intended to be persistent. Object ownership remains external.

## Dependencies And Integration Points
Includes `olist.h` for conceptual parity and `rvmlib.h` for persistence.

## Risks
The iterator safety claim should be verified against implementation before deleting entries during traversal. No locks are provided.

## Test Signals
Compile persistent users and run recovery tests for singleton, head, tail, and clear paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_olist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_smolist.cc -->
# sources/distributed-fs/coda/coda-src/util/rec_smolist.cc

## Purpose
Implements `rec_smolist`, a minimal recoverable circular singly-linked list designed to occupy only one pointer in persistent structures.

## Important APIs, Types, And Functions
`rec_smolist` implements `insert`, `append`, `remove`, `get`, `IsEmpty`, and print methods. `rec_smolist_iterator` precomputes the next link so current-entry removal during iteration is supported. `rec_smolink_print()` prints raw link state.

## Control Flow
Insert/append assert the link is not already in a list, then use `RVMLIB_MODIFY` to update the new link and list `last`. Removal finds the predecessor, updates predecessor and removed link, and fixes `last`. `get()` removes the head directly. The iterator starts at `last->next`, stores `nlink`, and stops after the last entry.

## State And Persistence
Only `last` in the list and `next` in each link are persistent topology. There is no count, constructor initialization, or object ownership. The header notes users must perform their own initialization.

## Dependencies And Integration Points
Depends on `rvmlib`, `util.h`, and transaction macros. It was designed for volume vnode arrays where compact recoverable list heads mattered.

## Risks
The constructor intentionally does not initialize `last`; callers must zero persistent storage before first use. No count makes corruption harder to detect. The list is single-membership by convention via `p->next == 0`.

## Test Signals
Initialize zeroed persistent list heads, insert/append/remove/get under transactions, remove current entries during iteration, recover after commit/abort, and verify uninitialized heads fail visibly in tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_smolist.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_smolist.h -->
# sources/distributed-fs/coda/coda-src/util/rec_smolist.h

## Purpose
Declares the compact recoverable singly-linked list and documents its relationship to `rec_olist`.

## Important APIs, Types, And Functions
`rec_smolist` exposes only a `last` pointer internally and public insertion, append, removal, get, empty, and print operations. `rec_smolist_iterator` stores current and next links. `struct rec_smolink` contains a single `next` pointer.

## Control Flow
Callers embed `rec_smolist` as a small persistent list head and `rec_smolink` in list members, then mutate through transaction-annotated methods.

## State And Persistence
The type is designed for RVM persistence with very small per-list overhead. Initialization is caller-managed.

## Dependencies And Integration Points
Includes `coda_tsa.h` for transaction annotations and is used by Coda volume metadata structures.

## Risks
Absence of a count and constructor initialization makes misuse harder to diagnose. Link objects can belong to only one list at a time.

## Test Signals
Validate zero-initialized persistent list heads, safe-delete iteration, and committed recovery behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rec_smolist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/recvarl.cc -->
# sources/distributed-fs/coda/coda-src/util/recvarl.cc

## Purpose
Implements `recvarl`, a recoverable variable-length allocation object with an inline length header and flexible payload area.

## Important APIs, Types, And Functions
Custom `operator new(size_t,int)` allocates `payload_size + sizeof(recvarl_length_t)` with `rvmlib_rec_malloc`. The normal `operator new(size_t)` and destructor assert. Constructor records and zeroes payload. `size()`, `end()`, and `destroy()` report total size, pointer past end, and free the recoverable object.

## Control Flow
Callers allocate with `new (payload_len) recvarl(payload_len)`. Construction logs the full allocation range, stores `length`, and zero-fills `vfld`. Destruction is not via `delete`; callers use `destroy()`.

## State And Persistence
State is recoverable allocation containing `length` and variable payload bytes. It must be created and destroyed under RVM transaction discipline.

## Dependencies And Integration Points
Depends on `rvmlib`, `util.h`, and transaction annotations. Used for persistent variable-length fields in Coda metadata.

## Risks
The dummy normal `new`, destructor, and `operator delete` all assert, so ordinary C++ lifetime management is invalid. Payload alignment is based on `unsigned long vfld[1]` but allocation size is byte-oriented. `destroy()` has a comment questioning correctness.

## Test Signals
Allocate several payload sizes in transactions, verify zeroed bytes, `size()` and `end()`, committed recovery, abort rollback, and `destroy()` freeing through RVM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/recvarl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/recvarl.h -->
# sources/distributed-fs/coda/coda-src/util/recvarl.h

## Purpose
Declares the recoverable variable-length object wrapper.

## Important APIs, Types, And Functions
`recvarl_length_t`, `class recvarl`, custom `new` overloads, `length`, `vfld`, `size()`, `end()`, and `destroy()` define the API.

## Control Flow
Callers allocate with the sized recoverable `new`, use the inline payload, and free with `destroy()` rather than `delete`.

## State And Persistence
The length and payload are intended to live in RVM and be transactionally initialized.

## Dependencies And Integration Points
Includes `coda_tsa.h`; implementation uses `rvmlib`.

## Risks
The API is nonstandard C++ and easy to misuse with ordinary `new/delete`. There is no bounds helper for payload access.

## Test Signals
Compile allocation syntax in callers and validate payload size/alignment assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/recvarl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rvmlib.c -->
# sources/distributed-fs/coda/coda-src/util/rvmlib.c

## Purpose
Provides Coda's wrapper layer around RVM/RDS transactions, per-LWP transaction state, recoverable allocation/free, and range logging.

## Important APIs, Types, And Functions
Global `RvmType` selects `UNSET`, `RAWIO`, `UFS`, or `VM`. APIs include `rvmlib_init_threaddata`, `rvmlib_thread_data`, `rvmlib_set_thread_data`, `_rvmlib_begin_transaction`, `rvmlib_end_transaction`, `rvmlib_abort`, `rvmlib_set_range`, `rvmlib_modify_bytes`, `rvmlib_strdup`, `rvmlib_malloc`, `rvmlib_free`, `rvmlib_check_trans`, and `rvmlib_in_transaction`.

## Control Flow
For RAWIO/UFS, thread data is stored in an LWP rock. Beginning a transaction initializes a tid, remembers file/line, and calls `rvm_begin_transaction()`. Ending commits with or without flush and coordinates delayed RDS frees. Aborting calls `rvm_abort_transaction()` and clears pending frees. Set-range and modify functions log bytes before mutation. Allocation dispatches to `malloc` in VM mode or `rds_malloc` in persistent modes; free uses `free` or queues an RDS fake free.

## State And Persistence
Per-thread state includes active tid, RDS intention list, and transaction start location. Persistent state is managed by RVM/RDS when `RvmType` is RAWIO/UFS. VM mode treats recoverable operations as ordinary heap operations and does not start real transactions.

## Dependencies And Integration Points
Depends on RVM, RDS, LWP rocks, `util.h`, and `coda_assert`. Every `rec_*` data structure and RVM-backed bitmap/varl object integrates through this layer.

## Risks
Many functions assert or abort on misuse rather than returning errors. `rvmlib_in_transaction()` returns false in VM mode, which can surprise generic checks. Transaction nesting is rejected. `rvmlib_free` is declared inline in a C file, which can be toolchain-sensitive. Function assumes per-LWP rock setup before persistent operations.

## Test Signals
Run begin/end/abort in VM, RAWIO, and UFS modes; nested begin failure; set-range without transaction; allocation/free with flush and no_flush; RDS delayed free paths; per-thread isolation; and recovery after committed and aborted mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rvmlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rvmlib.h -->
# sources/distributed-fs/coda/coda-src/util/rvmlib.h

## Purpose
Declares the RVM utility abstraction used by Coda's recoverable data structures.

## Important APIs, Types, And Functions
`rvm_type_t`, `rvm_perthread_t`, global `RvmType`, transaction begin/end/abort APIs, range/byte modification, recoverable malloc/free/strdup wrappers, thread-data functions, `RVMLIB_REC_OBJECT`, `RVMLIB_MODIFY`, and transaction assertion macros define the contract.

## Control Flow
Callers initialize thread data, begin a transaction, mark ranges or use `RVMLIB_MODIFY`, allocate/free recoverable memory, and end or abort the transaction.

## State And Persistence
The header defines per-thread transaction state and integration with RVM/RDS persistent storage. In VM mode operations degrade to ordinary memory.

## Dependencies And Integration Points
Includes RVM, RDS, LWP, util, and transaction annotation headers. It is included by all recoverable container headers.

## Risks
Macros evaluate object lvalues directly and require correct transaction context. `RvmType` is a global mode switch supplied by programs, so mixed-mode misuse can be catastrophic.

## Test Signals
Compile C and C++ recoverable users, verify annotations, and run transaction lifecycle tests around each macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rvmlib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rvmtesting.cc -->
# sources/distributed-fs/coda/coda-src/util/rvmtesting.cc

## Purpose
Contains optional `RVMTESTING` instrumentation for debugging writes to protected memory on old Mach/MIPS environments.

## Important APIs, Types, And Functions
When compiled with `RVMTESTING`, it defines `ClobberAddress`, `protect_page()`, `unprotect_page()`, `GPR()`, instruction decoding helper `getNextPc()`, `StoreInLoadDelay`, and signal handler `my_sigBus()`.

## Control Flow
Pages are protected with Mach `vm_protect`. On SIGBUS, `my_sigBus()` decodes the current or delay-slot instruction, determines whether a store targets `ClobberAddress`, zombies on illegal or targeted writes, otherwise temporarily unprotects the target, emulates simple byte/halfword/word stores, reprotects, and advances the saved PC through branch/jump decoding.

## State And Persistence
Debug-only global state includes `ClobberAddress`, `savedInstruction`, and debug level. It has no durable persistence and is compiled out unless `RVMTESTING` is defined.

## Dependencies And Integration Points
Depends on Mach VM APIs, MIPS instruction formats, `struct sigcontext`, `zombie()`, and Coda logging. It is historical diagnostic support for RVM corruption hunts.

## Risks
The code is architecture- and OS-specific, uses old-style casts and integer pointer truncation, and does not emulate `swl/swr`. The header exposes functions even when the implementation may compile to nothing. Modern platforms are unlikely to build this path.

## Test Signals
Only test on the intended Mach/MIPS configuration: protect/unprotect a page, trigger non-target and target stores, branch delay-slot handling, unaligned store handling, and build exclusion when `RVMTESTING` is unset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rvmtesting.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rvmtesting.h -->
# sources/distributed-fs/coda/coda-src/util/rvmtesting.h

## Purpose
Declares optional RVM memory-write debugging hooks.

## Important APIs, Types, And Functions
The header declares `protect_page`, `unprotect_page`, and `my_sigBus`.

## Control Flow
Debug builds install/use these functions to protect memory and handle SIGBUS diagnostics.

## State And Persistence
No state is declared here; implementation state is debug-only and process-local.

## Dependencies And Integration Points
Requires platform definitions for `struct sigcontext`. Intended for conditional `RVMTESTING` builds.

## Risks
The closing `#endif _RVMTESTING_H` is nonstandard trailing token style. Declarations may be unavailable or incompatible on modern systems.

## Test Signals
Compile with and without `RVMTESTING` on supported platforms and verify signal-handler signature compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/rvmtesting.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/testbitmap.cc -->
# sources/distributed-fs/coda/coda-src/util/testbitmap.cc

## Purpose
Provides a small manual test program for the original `bitmap` class.

## Important APIs, Types, And Functions
The program defines `RvmType = 3` for VM mode, allocates/deletes a `bitmap`, prints it, sets and frees indexes, grows the bitmap, repeatedly calls `GetFreeIndex()`, and deletes the object.

## Control Flow
Execution exercises construction/destruction, print, `SetIndex`, `FreeIndex`, `Grow`, and free-index allocation until exhaustion. It also contains an invalid-looking `delete[100] c` expression in the source snapshot.

## State And Persistence
All state is transient heap state in VM-mode `rvmlib`.

## Dependencies And Integration Points
Depends on `bitmap.h` and a compatible C++ compiler/runtime. It is not listed in `util/tests` but is part of the utility source list.

## Risks
The program uses old K&R-style `main()` without return type and questionable array delete syntax, so it is more historical smoke test than modern unit test. It does not assert expected values automatically.

## Test Signals
Modernize or compile with legacy-tolerant flags, run under ASAN/Valgrind, and compare printed maps against expected allocation/free/grow sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/testbitmap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/tests/Makefile.am -->
# sources/distributed-fs/coda/coda-src/util/tests/Makefile.am

## Purpose
Builds the `proctest` utility test program under `coda-src/util/tests`.

## Important APIs, Types, And Functions
`noinst_PROGRAMS = proctest`, `proctest_SOURCES = proctest.cc`, and `proctest_LDADD` links against `coda-src/util/libutil.la`.

## Control Flow
Automake converts this file into local test build rules for `proctest`.

## State And Persistence
No runtime state is defined. Build state is limited to the test binary and its link dependency.

## Dependencies And Integration Points
Depends on the parent utility library and Automake. It provides a narrow test for process-name lookup support.

## Risks
No `TESTS` variable is declared, so the program may be built but not run by `make check` unless added elsewhere. Missing `getcommandname` support would surface at link time.

## Test Signals
Run `make check` or explicitly build `proctest`, verify linkage against `libutil.la`, and execute it on supported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/tests/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/tests/proctest.cc -->
# sources/distributed-fs/coda/coda-src/util/tests/proctest.cc

## Purpose
Small executable that prints the command name associated with its own process id.

## Important APIs, Types, And Functions
`main()` calls `getpid()`, external `getcommandname(int)`, prints to stdout, and flushes. It also defines `LogFile` and `LogLevel` globals for linked utility code.

## Control Flow
The program obtains its PID, queries the command name, prints one line, and exits.

## State And Persistence
State is transient process state. No files or persistent data are modified.

## Dependencies And Integration Points
Depends on platform implementation of `getcommandname()` from libutil or base utilities, standard I/O, and process APIs.

## Risks
`getcommandname()` is declared manually and may be platform-specific. The program has no assertions, so output must be inspected or wrapped by tests.

## Test Signals
Run the binary and verify the returned name resembles `proctest`, test under long path/process names, and check behavior if `/proc` or equivalent process metadata is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/tests/proctest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/util.c -->
# sources/distributed-fs/coda/coda-src/util/util.c

## Purpose
Implements general Coda utility functions for hashing strings, timestamped logging, fd/stderr printing, hostname lookup/comparison, and simple process detachment.

## Important APIs, Types, And Functions
Globals define debug levels used by logging macros. Functions include `HashString`, `PrintTimeStamp`, `LogMsg`, `fdprint`, `eprint`, `hostname`, `UtilHostEq`, and `UtilDetach`.

## Control Flow
`HashString()` accumulates a reverse string hash modulo table size plus one. `PrintTimeStamp()` tracks date boundaries for up to five FILE pointers and emits date/time prefixes. `LogMsg()` filters by debug level, timestamps, formats, and flushes. `UtilHostEq()` resolves two names and compares their first addresses. `UtilDetach()` forks once and calls `setsid()` in the child.

## State And Persistence
Debug-level globals and static timestamp history are process-local. No durable state is written. `UtilDetach()` changes process/session state.

## Dependencies And Integration Points
Depends on C/POSIX runtime, resolver APIs, `util.h`, and `coda_string`. Many Coda components use `LogMsg` and the debug globals.

## Risks
`HashString()` returns 1..size and divides by `size`, so size zero is invalid and bucket users must expect one-based output. `PrintTimeStamp()` tracks only five files. `eprint()` reuses a variadic argument list by restarting it correctly, but duplicates output to stdout and stderr. `UtilHostEq()` uses legacy `gethostbyname()`.

## Test Signals
Hash empty and numeric strings, log around date boundaries and more than five files, compare host aliases/IPs, call detach in a supervised process, and verify debug-level filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/util.h -->
# sources/distributed-fs/coda/coda-src/util/util.h

## Purpose
Declares general Coda utility functions, logging macros, debug-level globals, and lock convenience macros.

## Important APIs, Types, And Functions
Public functions are `HashString`, `eprint`, `fdprint`, `LogMsg`, `PrintTimeStamp`, `UtilHostEq`, `hostname`, and `UtilDetach`. Macros include `TRUE`, `FALSE`, `VLog`, `SLog`, `DLog`, `ALog`, `CLog`, and `U_*lock` wrappers. Debug globals include server, volume, directory, ACL, and auth levels.

## Control Flow
Callers use package-specific logging macros, host utilities, and lock wrappers around LWP lock-bearing structures.

## State And Persistence
The header exposes process-global debug levels but no durable state.

## Dependencies And Integration Points
Includes `coda_assert`, POSIX/stdio/signal basics, and expects LWP lock functions for `U_*` macros. Used broadly by Coda sources.

## Risks
Macros depend on specific field names (`lock`) and global debug variables. Cygwin compatibility declarations may conflict with modern libc headers.

## Test Signals
Compile C/C++ users, check variadic macro support, lock macro use on structures with `lock`, and cross-platform builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/vice_file.c -->
# sources/distributed-fs/coda/coda-src/util/vice_file.c

## Purpose
Implements path construction for files under the configured Coda server `/vice` tree.

## Important APIs, Types, And Functions
`vice_dir_init()` stores the root directory in static `vicedir`. `vice_config_path()` calls internal `vice_filepath()` to return either the root or a root/name joined path.

## Control Flow
Initialization copies the configured directory into a bounded static buffer. Path lookup alternates between two static `volpath` buffers so calls such as `rename(path1, path2)` can use two returned paths at once.

## State And Persistence
State is process-global static path buffers. No filesystem state is changed by this file.

## Dependencies And Integration Points
Depends on `MAXPATHLEN`, `snprintf`, `CODA_ASSERT`, and `coda_string`. Used by server code such as `updatesrv` to locate `db`, `misc`, and other vice-tree files.

## Risks
Returned pointers refer to shared static buffers and are not thread-safe. Only two generated paths are stable at once. `vice_dir_init()` must be called before path construction.

## Test Signals
Initialize custom roots, request root and nested paths, call twice in one expression use case, exceed `MAXPATHLEN` under assertion builds, and test concurrent callers if any exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/vice_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/vice_file.h -->
# sources/distributed-fs/coda/coda-src/util/vice_file.h

## Purpose
Declares helpers for configuring and constructing paths under the Coda server vice directory.

## Important APIs, Types, And Functions
`vice_dir_init(const char *)` sets the root. `vice_config_path(const char *)` returns the root path or root plus a relative name.

## Control Flow
Programs initialize once from config, then use `vice_config_path()` for all vice-tree file lookups.

## State And Persistence
The API hides static process-global path state and does not modify disk state.

## Dependencies And Integration Points
C/C++ compatible header used by Coda server components.

## Risks
The returned pointer lifetime and static-buffer reuse are not visible from the signature.

## Test Signals
Compile C and C++ callers, verify initialization before use, and validate returned paths for null and non-null names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/vice_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/vmindex.cc -->
# sources/distributed-fs/coda/coda-src/util/vmindex.cc

## Purpose
Implements `vmindex`, a growable array of `unsigned long` indexes, and an iterator returning indexes sequentially.

## Important APIs, Types, And Functions
`vmindex::vmindex`, destructor, and `add()` manage storage. `vmindex_iterator::operator()()` returns the next stored value or -1 at end.

## Control Flow
Construction allocates an initial array if size is positive. `add()` doubles capacity or initializes default capacity when full, copies existing entries, and appends. The iterator holds the current array index and advances until `count`.

## State And Persistence
State is heap-only: `indices`, `size`, and `count`. Values are copied by value; no persistence or ownership beyond the array exists.

## Dependencies And Integration Points
Depends on `vmindex.h` and `util.h` for assertions. It is a small legacy alternative to vectors for index lists.

## Risks
Negative or zero constructor size leaves `size` uninitialized in the `else` branch because it assigns `sz = 0` rather than `size = 0`. Iterator end marker `-1` conflicts with valid `unsigned long` values when cast to signed long. No copy protection is declared.

## Test Signals
Construct with positive, zero, and negative sizes; append past growth boundaries; iterate all values; store values near `ULONG_MAX`; and run under sanitizers for uninitialized `size`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/vmindex.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/vmindex.h -->
# sources/distributed-fs/coda/coda-src/util/vmindex.h

## Purpose
Declares the `vmindex` growable index-array utility and iterator.

## Important APIs, Types, And Functions
`DEFAULTINDEXSIZE` is 32. `vmindex` stores `indices`, `size`, and `count` and exposes constructor, destructor, and `add()`. `vmindex_iterator` returns `long` values via `operator()()`.

## Control Flow
Callers add unsigned long indexes and iterate until `-1` is returned.

## State And Persistence
All state is in-memory and owned by the `vmindex` object.

## Dependencies And Integration Points
Standalone C++ header used by Coda code needing a simple index list.

## Risks
End-of-iteration sentinel can collide with large unsigned values. Public semantics do not mention copy behavior or ownership.

## Test Signals
Compile users and test growth, empty iteration, and sentinel handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/util/vmindex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vcodacon/Inet.cc -->
# sources/distributed-fs/coda/coda-src/vcodacon/Inet.cc

## Purpose
Implements the `Inet` socket wrapper used by `vcodacon` to connect to Coda's mariner/codacon stream over TCP or Unix-domain sockets.

## Important APIs, Types, And Functions
`Inet` methods include constructor/destructor, move-like assignment, `TcpOpen(host,port)`, Unix-socket `TcpOpen(path)`, `TcpServer`, `Accept`, `Close`, `Readline`, `Write(char *)`, `Write(int)`, and `Writeline`. Platform sections handle Winsock startup/cleanup and Unix socket APIs.

## Control Flow
Client open creates a socket, resolves host or fills `sockaddr_un`, connects, and records `remname`. Server open binds/listens. Accept fills a target `Inet` and resolves remote name. `Readline()` reads one byte at a time until newline/CRLF or buffer limit depending on `unixlines`. Writes send strings and append line endings for `Writeline()`.

## State And Persistence
State is per-object descriptor, last error, server flag, remote name/address/length, and newline mode. No persistent storage exists.

## Dependencies And Integration Points
Depends on POSIX sockets or Winsock, config feature macros, and `Inet.h`. `monitor.cc` uses it for GUI event-loop integration through `FileNo()`.

## Risks
`remname` is allocated with `strdup()` but freed with `delete[]`, which mismatches allocation. `Readline()` writes `data[length] = 0` when full, one past the caller's length. The Unix/newline conditional structure means CRLF handling is tied to `unixlines` logic and deserves scrutiny. Name resolution uses legacy `gethostbyname/gethostbyaddr`.

## Test Signals
Connect to TCP and Unix sockets, read LF and CRLF lines at buffer boundaries, write strings/integers/lines, close/reopen, accept clients, run under ASAN for allocation mismatch and buffer limits, and test Winsock lifecycle if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vcodacon/Inet.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vcodacon/Inet.h -->
# sources/distributed-fs/coda/coda-src/vcodacon/Inet.h

## Purpose
Declares a small portable socket wrapper for TCP, optional Unix-domain sockets, and line-oriented I/O.

## Important APIs, Types, And Functions
`Inet` exposes connection/server methods, `Accept`, `Close`, `Readline`, `Write`, `Writeline`, status/error accessors, remote-name/address helpers, and newline mode setters. Macros abstract `close`/`closesocket`, last error, and remote length type.

## Control Flow
GUI or utility code creates an `Inet`, opens a connection, registers the fd, reads lines, writes commands, and closes on errors.

## State And Persistence
The class stores socket descriptor and peer metadata only for object lifetime.

## Dependencies And Integration Points
Includes platform socket headers and optional `sys/un.h`. Used by `vcodacon` monitor code.

## Risks
Assignment is destructive move-like behavior but is exposed as `operator=`, which can surprise users. `RemoteAddr()` assumes an IPv4 sockaddr even if other address families are introduced.

## Test Signals
Compile on Unix, Cygwin/Solaris, and Windows paths; test assignment invalidates source; and validate fd/error accessors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vcodacon/Inet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vcodacon/Makefile.am -->
# sources/distributed-fs/coda/coda-src/vcodacon/Makefile.am

## Purpose
Builds the optional FLTK-based `vcodacon` GUI when both `BUILD_VCODACON` and `BUILD_CLIENT` are enabled.

## Important APIs, Types, And Functions
`bin_PROGRAMS = vcodacon` is conditional. Static sources are `Inet.cc`, `Inet.h`, `monitor.cc`, `monitor.h`, `util.cc`, and `util.h`. Generated sources are `vcodacon.cc` and `vcodacon.h` from `vcodacon.fl` via `$(FLUID)`. `LDADD` links base library and FLTK libraries.

## Control Flow
Automake builds generated FLUID sources first, compiles the GUI/network/monitor utilities, and links the FLTK executable. `CLEANFILES` removes generated sources.

## State And Persistence
No runtime state is defined here. Build state includes generated GUI source files.

## Dependencies And Integration Points
Depends on FLTK flags/libs, `lib-src/base`, and the FLUID interface compiler. Integrates generated UI widgets with handwritten monitor/network code.

## Risks
Missing FLUID or mismatched FLTK flags breaks builds. Generated sources are nodist, so source tarballs must include `vcodacon.fl` and regenerate. Conditional nesting can hide build rot unless enabled regularly.

## Test Signals
Configure with and without `BUILD_VCODACON`/`BUILD_CLIENT`, run FLUID generation, link against FLTK, clean/rebuild, and launch the GUI against a mariner socket.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vcodacon/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vcodacon/monitor.cc -->
# sources/distributed-fs/coda/coda-src/vcodacon/monitor.cc

## Purpose
Implements the `vcodacon` monitor that connects to Coda mariner/codacon output and updates FLTK widgets for connection, activity, cache walks, fetch progress, stores, reintegration, attribute fetches, and conflicts.

## Important APIs, Types, And Functions
Static FLTK callbacks are `GetNextLine`, `ConnExcept`, `TryAgain`, `AgeColor`, `ClearVattr`, and `ClearXfer`. `monitor` methods are `Start`, `NextLine`, `ForceClose`, and `AgeActColor`. Global generated widgets from `vcodacon.h` are updated directly.

## Control Flow
`Start()` initializes the singleton monitor pointer, reads `marinersocket` from `venus.conf`, tries a Unix socket then localhost `CODACONPORT`, registers fd read/exception callbacks, sets connection/activity colors, switches line mode to Unix, and sends `set:fetch`. `NextLine()` reads one line, appends most lines to the browser with bounded history, ages activity color, parses known substrings, and updates progress bars and status widgets. Connection loss or exception closes the fd, marks red, and schedules reconnect. Timeouts clear transient colors/progress bars.

## State And Persistence
State is GUI/runtime only: `TheMon`, `Vattrnum`, progress labels, monitor counters, current activity color, browser size, and socket connection state. No persistent data is written.

## Dependencies And Integration Points
Depends on `Inet`, `codaconf`, FLTK event loop/widgets, generated `vcodacon.h`, and `util.h` for `XferLabel`. It integrates the Coda client mariner event stream with a visual status dashboard.

## Risks
Parsing is substring-based and mutates input strings after locating parentheses/percent signs without validating all pointers, so malformed progress lines can crash. `ForceClose()` calls `Start()` immediately after close, while other paths schedule delayed reconnects. Static singleton design prevents multiple independent monitors. Progress label memory is managed manually.

## Test Signals
Feed representative mariner lines for fetch progress, cache begin/end, shutdown, store/reintegration begin/end, attr fetches, conflicts, malformed progress lines, connection close, and repeated reconnects. Verify FLTK fd/timeout registration, browser trimming, progress-bar reuse, and color aging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vcodacon/monitor.cc -->
