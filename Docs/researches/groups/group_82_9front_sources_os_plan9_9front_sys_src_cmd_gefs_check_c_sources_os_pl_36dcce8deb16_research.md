# Group Research: group_82_9front_sources_os_plan9_9front_sys_src_cmd_gefs_check_c_sources_os_pl_36dcce8deb16

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/check.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/check.c

Filesystem consistency checker for gefs.

Key responsibilities:
- Verifies B-tree ordering, key ranges, balance, pointer validity, and child fill counts through `checktree()`.
- Walks arena free AVL ranges for ordering/overlap errors and verifies allocation-log chains.
- Checks snapshot deadlist records and their linked log blocks.
- Opens every snapshot label and checks its root tree.
- Reports errors to a supplied fd and returns overall ok/broken status.

Important behavior:
- `checkfs()` waits for epochs, then holds `fs->mutlk` while checking global metadata.
- `isfree()` detects block pointers that point into currently free arena ranges.
- Pivot buffer messages are validated for known operation codes and valid `Owstat` masks.

Notable risks:
- `checkdata()` currently scans `Klabel` keys in a data tree while interpreting values as block pointers; this means ordinary `Kdat` file data pointers are not actually covered there.
- Error recovery in the snapshot loop uses nested `waserror()` blocks and continues past some failures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/check.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/cons.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/cons.c

Interactive gefs administrative console served through the `.cmd` service.

Key responsibilities:
- Parses console commands and dispatches to sync, halt, snapshot, check, user reload, config, space, and debug handlers.
- Sends administrative work to `fs->admchan` as `Amsg` requests for serialized background execution.
- Provides diagnostic dumps for fids, trees, users, block cache state, free ranges, and recent trace entries.
- Wraps commands that inspect trees in epoch protection.

Important behavior:
- `snap` supports list, delete, mutable fork, and label operations.
- `set`/`clear` can target either global config or a named snapshot.
- `show df` aggregates arena sizes and used/free space.
- `runcons()` tokenizes up to four fields, prints `gefs# ` prompts, and reports command errors through the gefs error stack.

Notable risks:
- `reserve` toggles `usereserve`, but its status print uses `permissive`, so its displayed transition is misleading.
- Command parsing is intentionally small and fixed-size; arguments with spaces are not supported.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/cons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/dat.h

Central gefs data model, constants, on-disk layout notes, and shared structs.

Key contents:
- Defines block size, key/value limits, node layout sizes, message limits, cache sizes, and 9P/server table sizes.
- Defines B-tree key classes for data blocks, directory entries, parent links, snapshot labels, snapshot roots, deadlists, and config keys.
- Defines block types: data, pivot, leaf, log, deadlist, arena header/footer, and superblock.
- Defines mutation operations, wstat bit encodings, allocation-log operations, admin message operations, and deferred-free categories.
- Declares core structs: `Gefs`, `Arena`, `Tree`, `Blk`, `Bptr`, `Kvp`, `Msg`, `Dlist`, `Mount`, `Conn`, `Fid`, `Dent`, `Scan`, `Chan`, `User`, and `Trace`.

Role:
- Documents the disk format and provides the shared ABI between block I/O, B-tree logic, snapshot management, 9P serving, formatting, loading, and checking.
- Encodes gefs as a COW B-tree filesystem with arena allocation logs, snapshot chains, deadlists, block cache/LRU, deferred reclamation, and multiple worker queues.

Notable constraints:
- Block layout constants depend on `Blksz == 1<<14`.
- `Keymax`, `Inlmax`, `Msgmax`, and pivot-buffer sizing must satisfy assertions in `main.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/dump.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/dump.c

Debug formatting and recursive block/tree dump support for gefs.

Key responsibilities:
- Implements custom formatters for block pointers, messages, key/value pairs, keys, qids, and arena ranges.
- Decodes gefs key/value types into readable text for data pointers, dirents, snapshot labels/roots, parent links, deadlists, and config.
- Recursively prints leaf and pivot blocks, including pivot buffers and child pointers.
- Provides `showblk()`, `showbp()`, `showtreeroot()`, and `initshow()` for console/debug use.

Important behavior:
- `%#P` and `%#M` treat values as block pointers with fill counts.
- `showval()` decodes `Owstat`, snapshot relinks, deadlist heads/tails, and serialized `Xdir` fields.
- `rshowblk()` follows child pointers when recursion is enabled.

Notable risks:
- Recursive tree dump calls `getblk()` on child pointers and can be expensive or fail on corrupt structures.
- Some formatting paths abort on malformed sizes rather than returning a printable error.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/error.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/error.c

Shared gefs error-string definitions.

Key contents:
- Defines internal errors for corruption, implementation gaps, protocol botches, I/O, fids, types, search, permissions, auth, snapshots, readonly state, and qid exhaustion.
- Defines Plan 9 wstat-specific errors for illegal qid/mode/name/owner/group/length changes.
- Keeps old/commented error strings as historical references.

Role:
- Provides stable `char[]` error symbols used with `error()`, `broke()`, and 9P `Rerror` responses.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/error.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/fns.h

Shared gefs extern declarations, packing macros, prototypes, and debug/error macros.

Key contents:
- Declares global filesystem state and runtime flags.
- Provides big-endian `PACK*`/`UNPACK*` macros for gefs disk structures.
- Declares block allocation/cache/sync, snapshot, load/ream, B-tree, user, dump, pack/unpack, channel, worker, and fuzz APIs.
- Defines tracing, assertion, fatal, and Plan 9-style error-stack macros.

Role:
- Connects gefs compilation units without exposing implementation-specific headers.
- Establishes the internal API surface for block, tree, snapshot, 9P, admin, and test code.

Notable constraints:
- `waserror()`/`poperror()` depend on per-process `Errctx` setup in `main.c`.
- Many APIs assume callers already hold `fs->mutlk` or are inside an epoch.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/fs.c

Main gefs 9P server, mutation pipeline, snapshot sync, permission logic, and background admin tasks.

Key responsibilities:
- Implements 9P attach, auth, walk, open, create, read, write, stat, wstat, remove, clunk, flush, and version handling.
- Maintains mounts, fids, directory-entry cache, per-connection fid tables, auth fids, and synthetic dump-root behavior.
- Routes requests through separate reader, mutator, admin/sweeper, sync, and periodic-task queues.
- Performs COW B-tree updates for file writes, directory changes, metadata changes, truncation, and removal.
- Coordinates snapshot updates, ordered sync passes, arena header/superblock writes, deadlist flushing, and log compression.
- Handles automatic retained snapshots from `retain` config.

Important behavior:
- Mutations run under `fs->mutlk` and epochs; readers enter epochs without the mutation lock.
- `sync()` performs ordered passes: update snapshots/deadlists/logs, write arena headers, write superblocks, write arena footers, then free old deadlist data.
- Writes allocate new data blocks and then upsert `Kdat` records plus an `Owstat` metadata update.
- Truncation and `ORCLOSE` are deferred as admin messages so block-clearing can run outside the foreground request path.
- Dump attach exposes snapshot labels as a synthetic readonly directory.
- Auth uses factotum `p9any` unless auth is disabled.

Notable risks:
- Many routines depend on precise lock/epoch ordering; `truncwait()` explicitly drops and reacquires mutation state to avoid blocking the sweeper.
- Readonly transition is used as a safety latch after serious sync or mutation failures.
- Some error comments note intentional leaks on exceptional paths to avoid compounding corruption.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/fuzz.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/fuzz.c

Concurrent gefs B-tree fuzzer and shadow-model verifier.

Key responsibilities:
- Generates random directory-entry, data-pointer, insert, delete, clobber, and wstat messages.
- Maintains an AVL shadow map of expected key/value state.
- Runs writer and scanner/checker workers against a mutable `fuzz` snapshot.
- Verifies random lookups and complete scans against the shadow tree.
- Dumps trace data to `/tmp/fuzz.trace` and kills the process group on mismatch.

Important behavior:
- Uses xoshiro-like local PRNG state seeded from `fuzzseed`.
- `fzupsert()` snapshots tree root state, performs `btupsert()`, then applies the same batch to the shadow model.
- `fzscan()` periodically performs both sampled lookups and full in-order scans.
- `fzinit()` creates a mutable `fuzz` snapshot from `empty` and seeds shadow state from existing entries.

Notable risks:
- Shadow selection in `pickrand()` walks the AVL shape heuristically rather than by exact rank.
- The fuzzer intentionally runs forever once enabled.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/fuzz.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/hash.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/hash.c

Hash helpers for gefs block integrity and hash-table indexing.

Key responsibilities:
- Provides MetroHash64 implementation with fixed gefs seed.
- Hashes arbitrary buffers and whole gefs blocks.
- Provides `ihash()` integer finalizer for distributing ids across hash tables.

Important behavior:
- `bufhash()` and `blkhash()` use seed `0x6765`.
- MetroHash reads native unaligned integer widths through casts.

Notable risks:
- The native-width reads assume the target architecture tolerates the access pattern used here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/load.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/load.c

gefs mount-time loader for superblocks, arenas, allocation logs, and users.

Key responsibilities:
- Loads arena header/footer pairs, accepting either valid copy as fallback.
- Initializes arena free-range AVL trees, log buffers, and cache-plucked static blocks.
- Loads primary superblock, falling back to the backup superblock at device end.
- Reconstructs arena free state by replaying allocation logs.
- Opens the `adm` snapshot and loads `/users`.

Important behavior:
- `loadfs()` creates a synthetic `dump` mount rooted at `fs->snap`.
- Arena reserve is derived from arena size and clamped between 512 KiB and 8 MiB.
- Prints loaded filesystem geometry and generation/qid state.

Notable risks:
- The fallback message for backup superblock says “primary” twice.
- If both arena header copies fail, loading aborts with `Efs`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/load.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/main.c

gefs process entry point, runtime initialization, error stack, tracing, and worker startup.

Key responsibilities:
- Parses command-line modes for ream, grow, check-only, readonly, stdio, auth-disable, debug, cache size, trace size, fuzzing, service name, and network announces.
- Allocates global `Gefs`, block cache, deferred-free pool, deadlist cache, trace ring, and per-process error context.
- Installs formatters and starts console, mutator, sweeper, task, reader, sync, network, srv, stdio, and fuzz workers.
- Implements Plan 9-style `waserror()`/`error()`/`broke()`/`nexterror()` over per-process `jmp_buf` stacks.
- Posts `/srv/gefs` and `/srv/gefs.cmd` pipe endpoints.

Important behavior:
- Default cache size is 25% of detected memory from `/dev/swap`.
- Worker processes are `rfork(RFPROC|RFMEM|RFNOWAIT)` children sharing memory.
- `broke()` marks the filesystem readonly before raising the error.
- `writetrace()` and `_babort()` dump trace-ring entries for debugging.

Notable risks:
- `Maxprocs`, epoch slot count, and worker ids must remain coordinated.
- The process exits immediately after launching server workers; service lifetime is in children.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/pack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/pack.c

gefs serialization and deserialization for keys, values, stats, trees, arenas, and superblocks.

Key responsibilities:
- Packs/unpacks nul-terminated counted strings used in directory keys.
- Converts `Xdir` records to/from B-tree kvps and Plan 9 stat buffers.
- Packs data keys, parent links, labels, snapshot keys, deadlists, block pointers, tree records, arena records, and superblocks.
- Validates superblock magic/version and hash.

Important behavior:
- Directory stat conversion resolves uid/gid/muid through the loaded user table.
- Superblock stores snap root, snap deadlist, arena pointers, flags, next qid/gen, and qgen, followed by a MetroHash checksum.
- `unpacksb()` allocates `fs->arenabp` and restores `fs->qgen`.

Notable risks:
- Many routines assert buffer sizes rather than returning recoverable errors.
- `kv2qid()` reads qid version as 64 bits, although Plan 9 `Qid.vers` is narrower elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/pack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/ream.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/ream.c

gefs formatter and grower for block devices.

Key responsibilities:
- Creates initial arena headers, allocation logs, root tree, `adm` tree, users file, snapshot tree, and superblock copies.
- Initializes labels `empty`, `adm`, and mutable `main`.
- Writes default `/adm/users` content using the requested ream user.
- Splits a device into 8 to 32 arenas for initial formatting.
- Adds four new arenas when growing a filesystem.

Important behavior:
- Requires at least `128 MiB + Blksz` for ream.
- Leaves two blocks at each arena start for arena header/footer.
- Writes both primary superblock at block 0 and backup superblock near device end.
- `growfs()` rewrites the backup superblock at the new end after extending arena metadata.

Notable risks:
- `reamfs()` has duplicated `dropblk()` calls for several blocks after they were already dropped, which is suspicious unless reference counts were intentionally held.
- Grow requires at least 64 MiB of new arena space.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/ream.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/snap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/snap.c

Snapshot, deadlist, and block-reclamation logic for gefs.

Key responsibilities:
- Caches, loads, creates, flushes, merges, and frees deadlists.
- Records killed blocks into deadlists based on snapshot generations.
- Opens, closes, labels, forks, updates, and deletes snapshot trees.
- Maintains predecessor/successor links and snapshot label/reference counts.
- Reclaims blocks when snapshots are deleted or merged.

Important behavior:
- Mutable snapshots get a new tree generation and `memgen`; immutable labels increment label counts.
- `updatesnap()` creates a new generation for dirty mounted snapshots, relinks history, and can delete the old tree if it becomes unreferenced.
- `killblk()` avoids double-freeing blocks allocated before a fork by comparing block generation with tree base.
- `dlsync()` flushes all cached deadlists into the snapshot tree before sync.

Notable risks:
- Correctness depends on subtle `gen`, `memgen`, `base`, `pred`, and `succ` relationships.
- Deadlist cache eviction flushes metadata and can allocate/write while snapshot metadata is being mutated.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/snap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/tree.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/tree.c

Core gefs copy-on-write B-tree implementation.

Key responsibilities:
- Encodes/decodes leaf values and pivot-buffer messages.
- Performs sorted batched upserts using pivot-buffer messages and flush-down compaction.
- Applies insert, delete, clear, clobber, wstat, and snapshot relink operations.
- Splits, rotates, merges, and balances leaf and pivot blocks.
- Frees replaced data pointers and old tree blocks through deferred reclamation.
- Provides lookup and prefix/in-order scan APIs.

Important behavior:
- Pivot blocks have two regions: child pointers and buffered mutation messages.
- `btupsert()` sorts message batches, tries fast pivot-buffer insertion, otherwise finds a victim path and flushes messages toward leaves.
- Tree updates are COW: new blocks are allocated, old blocks are freed after root replacement.
- `btlookup()` walks to a leaf, then applies pending messages from ancestors from bottom to top.
- `btnext()` merges leaf values with pending pivot-buffer inserts/deletes to produce current scan state.
- Root height can grow or shrink during flush.

Notable risks:
- Very dense pointer arithmetic and fixed-size packed records make corruption bugs hard to localize.
- Correctness depends on preserving room for at least one message during pivot operations.
- `btupsert()` asserts `fs->mutlk` is already held.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/user.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/user.c

gefs `/adm/users` loader and parser.

Key responsibilities:
- Reads the users file from a snapshot tree through `Kdat` block pointers.
- Parses user records of the form `id:name:leader:members`.
- Builds `User` entries with ids, names, group leaders, and member id lists.
- Swaps the loaded user table under `fs->userlk`.
- Resolves users by id or name.

Important behavior:
- Parsing is two-pass: first ids/names, then leader and membership references.
- `loadusers()` falls back to a minimal default table only when no prior table exists and permissive mode is enabled.
- Updates global `noneid`, `admid`, and `nogroupid` after load.

Notable risks:
- `slurp()` does not drop blocks after `getblk()`, which appears to leak block references.
- User file size is capped at 1 MiB.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/getmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/getmap.c

Plan 9 colormap loader/applicator for 8-bit draw displays.

Key responsibilities:
- Reads colormaps from explicit files, `/lib/cmap/`, display colormap files, or generated gamma maps.
- Supports `gamma`, `gammaN`, `rgamma`, and `rgammaN` generated grayscale maps.
- Validates 256-line colormap files with index plus RGB fields.
- Writes the selected colormap to `/dev/draw/<id>/colormap`.

Important behavior:
- Opens `/dev/draw/new`, extracts the display id, and only proceeds for `m8` CMAP8 displays.
- `rep()` replicates an n-bit value across a 32-bit word but is not used by `main()`.

Notable risks:
- Allocated read buffers are not freed, but the command is short-lived.
- The fallback comparison for `screen`/`display`/`vga` checks the composed `name`, not the original argument after directory probing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/getmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/add -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/add

rc script for staging files in 9front git.

Key responsibilities:
- Initializes git environment through `common.rc` and `gitup`.
- Parses `-r` to stage removals instead of additions.
- Cleans input paths relative to the repo root.
- Walks files while excluding `.git`, then appends staging rows to `.git/INDEX9`.

Important behavior:
- Addition rows use `A NOQID 0 path`; removal rows use `R NOQID 0 path`.
- Requires at least one path argument.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/add -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/branch -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/branch

rc script for listing, switching, creating, removing, and merging branches.

Key responsibilities:
- Lists local/remote branch refs or all branches from git/fs control state.
- Resolves target branch/base refs, including auto-creating local heads from origin refs.
- Prevents clobbering uncommitted changes unless merge/remove options allow it.
- Updates working tree files from the target branch tree and records index updates.
- Runs `merge1` for dirty paths requiring three-way merge.
- Updates `.git/HEAD` and target ref.

Important behavior:
- Ref names are normalized under `refs/heads/`.
- `-r` refuses to remove the current branch.
- `-s` updates branch ref without switching HEAD.

Notable risks:
- File/directory type transitions are handled by `rm -rf`, so path normalization must be correct.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/branch -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/clone -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/clone

rc script for cloning remote repositories with 9front git.

Key responsibilities:
- Creates `.git` layout, writes origin remote config, fetches remote refs through `git/get`, and sets local HEAD.
- Selects default branch from remote HEAD/symref or requested `-b` branch.
- Checks out the selected branch through `git/fs` and tar-copy from the mounted tree.
- Seeds `.git/INDEX9` with tracked tree entries.
- Cleans partially cloned destination on interrupt or failure.

Important behavior:
- Local directory defaults to the remote basename without `.git`.
- Empty existing destination is allowed; non-empty destination is rejected.
- Remote heads are stored under `.git/refs/remotes/origin`.

Notable risks:
- The checkout path relies on `.git/fs/HEAD/tree` after starting `git/fs`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/clone -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/commit -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/commit

rc script for creating, revising, and partially selecting commits.

Key responsibilities:
- Finds the active branch/ref and handles initial commits.
- Builds parent lists for normal, revised, and merge commits.
- Creates or edits commit messages and strips comments/extra blank lines.
- Collects changed files from explicit paths, merge state, or git walk.
- Supports partial commit hunk selection by building and applying a temporary patch in ramfs.
- Calls `git/save` and updates branch/HEAD plus `.git/INDEX9`.

Important behavior:
- Defaults editor from `git/conf core.editor`, then `$editor`, then `hold`.
- `-m` supplies a message, `-e` edits, `-r` revises, and `-p` commits selected hunks.
- Removes `.git/merge-parents` after successful update.

Notable risks:
- Partial hunk path uses bind mounts and patch application; failure handling is intentionally conservative.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/commit -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/compat -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/compat

Compatibility wrapper that emulates selected mainstream `git` commands using 9front git commands.

Key responsibilities:
- Implements dispatch functions for init, clone, pull/fetch, checkout, submodule, rev-parse, show-ref, remote add, log/show, ls-remote, version, and status.
- Handles common flags used by tools such as Go.
- Can bind itself as `git` in a temporary namespace when invoked as `compat`.
- Locates repo root for commands that need it.

Important behavior:
- Reports version as `git version 2.2.0`.
- Submodules are explicitly unsupported if `.gitmodules` exists.
- Debug mode logs commands to `/tmp/gitlog`.

Notable risks:
- Contains two `cmd_rev-parse` definitions; the later one overrides the earlier in rc function namespace.
- `cmd_checkout` calls `git/branch $b`, but `b` is not set in that function.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/compat -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/conf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/conf.c

Git config query command.

Key responsibilities:
- Locates repository root or prints it with `-r`.
- Reads config values from explicit `-f` files or default repo/user/system config files.
- Supports section-qualified keys using `section.key`.
- Optionally prints all matches with `-a`.

Important behavior:
- Section headers are matched as literal bracketed strings like `[remote "origin"]`.
- Key matching strips whitespace around key/value and `=`.
- Default config search order is `.git/config`, `$home/lib/git/config`, then `/sys/lib/git/config`.

Notable risks:
- Section detection compares against the unstripped line for headers, while other comparisons use stripped text.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/delta.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/delta.c

Content-defined delta generator for git pack writing.

Key responsibilities:
- Splits a base object into rolling gear-hash chunks.
- Builds an open-addressed hash table from base chunks.
- Splits the target object the same way, looks up matching chunks, and emits copy or insert delta spans.
- Extends copy spans forward while bytes continue matching.
- Manages delta table object references and memory.

Important behavior:
- Chunk sizes range from 128 to 8192 bytes with split mask `(1<<8)-1`.
- Uses `murmurhash2()` for table lookup keys.
- Copy lengths are capped below Git’s 24-bit delta length limit.

Notable risks:
- The algorithm emits one delta op per chunk/span and does not coalesce adjacent compatible ops.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/delta.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/diff -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/diff

rc script for showing git working-tree diffs.

Key responsibilities:
- Parses commit base, summarize, and uncommitted options.
- Uses `git/walk` to list changed paths or summarize changes.
- Mounts scratch namespaces and binds commit tree as `a` and working tree as `b`.
- Runs `diff -u` for each changed file, using `/dev/null` for additions/deletions.

Important behavior:
- Default base commit is `HEAD`.
- `-u` includes uncommitted state in the walk filter.
- Path arguments are cleaned relative to the git root.

Notable risks:
- Output header says `diff <commit> uncommitted` once per run.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/diff -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/export -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/export

rc script for exporting commits as patch emails/files.

Key responsibilities:
- Resolves a query to commits.
- Builds patch mail headers from commit author, commit message, and timestamp.
- Diffs each commit against its parent using scratch binds.
- Writes patches to stdout or `-o` patch directory.
- Generates numbered patch filenames from sanitized first-line subjects.

Important behavior:
- Uses `[PATCH]` or `[PATCH n/m]` subjects.
- Includes a 9front signature marker after diff content.
- Tolerates failure to create `/mnt/scratch` for web UI usage.

Notable risks:
- Uses `diff -ur` over bound trees rather than git-specific rename or mode metadata handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/export -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/fs.c

9P filesystem view of a git repository.

Key responsibilities:
- Exposes root entries `HEAD`, `branch`, `object`, and `ctl`.
- Maps branches, commits, trees, blobs, tags, and object hashes into synthetic 9P directories/files.
- Provides commit metadata files: `tree`, `parent`, `msg`, `hash`, `author`, and `committer`.
- Generates stable synthetic qids with a small qid cache.
- Resolves refs, reads objects, follows symlinks within tree walks, and lists object directories.
- Implements lib9p attach, walk, clone, open, read, stat, and fid cleanup.

Important behavior:
- `ctl` reports current branch and repo root.
- Blob/tag reads return raw object data; tree/commit reads are directory listings.
- Branch refs are read from `.git/refs`; `HEAD` ref indirection is followed.
- `.git` path entries are hidden when walking object trees.

Notable risks:
- Symlink resolution avoids cycles by checking existing crumbs, but it is limited to in-tree object traversal.
- qid generation uses an in-memory cache and monotonically increasing qid ids; it is stable only within the running server.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/get.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/get.c

Git fetch/upload-pack client.

Key responsibilities:
- Connects to a remote upload service and reads advertised refs/capabilities.
- Filters refs by branch, heads, tags, and HEAD; validates ref names.
- Resolves local remote-tracking refs to determine already-held objects.
- Negotiates wants and haves, including optional extra local heads.
- Receives sideband or raw pack data, verifies pack SHA-1 trailer, indexes the pack, and renames pack/index files by hash.
- Prints remote/local ref mapping output for callers like clone.

Important behavior:
- `-l` lists refs without fetching.
- Supports `multi_ack`, `side-band`, and `side-band-64k`.
- Sends up to 256 have lines from local refs and queued ancestors.
- Temporary pack files live under `.git/objects/pack/fetch.<pid>.*`.

Notable risks:
- `fail()` formats variadic messages with `snprint` instead of `vsnprint`, so detailed error formatting may be wrong.
- Smart HTTP and multi-round negotiation are intentionally simplified.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/get.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/git.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/git.h

Shared 9front git declarations, object model, protocol model, and utility prototypes.

Key contents:
- Defines git object type constants, object cache flags, connection types, sizes, and endian helpers.
- Defines `Hash`, `Object`, commit/tree info, pack/index/object-list state, object sets, priority queues, delta tables, and delta ops.
- Declares object I/O, ref resolution, pack writing/indexing, object-set, object-list, utility, delta, protocol, and queue APIs.
- Declares custom formatters for hashes, types, objects, and qids.

Role:
- Central contract for git command C files including `fs.c`, `get.c`, `delta.c`, config, pack, proto, ref, save, and utility modules.

Notable constraints:
- SHA-1 hash size is fixed at 20 bytes.
- Path buffers are mostly fixed-size Plan 9-style arrays.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/git.h -->