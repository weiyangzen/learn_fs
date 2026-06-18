<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/fts.c -->
# sources/distributed-fs/orangefs/src/client/usrint/fts.c

## Purpose
`fts.c` provides a local copy of the BSD file tree traversal implementation for the OrangeFS user-interface library. It backs the `fts_open`, `fts_read`, `fts_children`, `fts_set`, and `fts_close` API declared in `fts.h`, with small usrint adaptations that map libc-internal names such as `__open` and `__readdir` onto the active POSIX wrapper layer. OrangeFS utilities such as `ofs_cp`, `ofs_rm`, and `ofs_setdirhint` use this walker to traverse local/PVFS-visible path trees with `FTS_COMFOLLOW | FTS_PHYSICAL`.

## Important APIs, Types, And Functions
The exported API is the traditional `FTS *fts_open(char * const *argv, int options, compar)`, `FTSENT *fts_read(FTS *)`, `FTSENT *fts_children(FTS *, int)`, `int fts_set(FTS *, FTSENT *, int)`, and `int fts_close(FTS *)`. Internally, `fts_alloc` creates variable-size `FTSENT` nodes and optionally co-locates a `struct stat`; `fts_build` reads a directory into a linked list of children; `fts_stat` classifies nodes as regular files, directories, symlinks, cycles, stat failures, or default entries; `fts_sort` materializes a reusable pointer array for `qsort`; `fts_palloc` expands the traversal path buffer; and `fts_safe_changedir` verifies device/inode before changing cwd.

## Control Flow
`fts_open` validates option bits, allocates the traversal stream, forces `FTS_NOCHDIR` for logical walks, allocates a path buffer, creates a root-parent sentinel, stats each root argument, optionally sorts roots, then installs a dummy `FTS_INIT` current node. `fts_read` drives the preorder/postorder state machine: it handles caller instructions (`FTS_AGAIN`, `FTS_FOLLOW`, `FTS_SKIP`), descends into `FTS_D` nodes by calling `fts_build`, returns linked siblings, then climbs to parents and emits `FTS_DP`. `fts_children` builds child lists for the current preorder directory without advancing the stream. `fts_build` opens the current directory, optionally changes into it, skips dot entries unless requested, creates child nodes, grows the shared path buffer when needed, runs `fts_stat` unless `FTS_NOSTAT` can avoid it, sorts children if requested, and restores cwd for child-only reads or empty directories.

## State And Persistence Behavior
Traversal state is entirely in memory. `FTS` owns the shared path buffer, current node pointer, pending child list, sort array, root directory fd, options, and device id. `FTSENT` nodes link to parents/siblings, store path/name lengths, stat data, cycle back-pointers, symlink fds, caller instructions, and user scratch fields. The implementation may change the process cwd unless `FTS_NOCHDIR` is set, restoring through `fts_rfd`, parent walks, or symlink fds. No durable state is written.

## Dependencies And Integration Points
The file includes `usrint.h`, libc/POSIX headers, and `<fts.h>`. Because `fts.h` maps `__open`, `__opendir`, `__fchdir`, and related symbols, traversal can be compiled inside the usrint interposition layer. It depends on `stat/lstat`, `opendir/readdir/closedir`, `dirfd`, `qsort`, and 64-bit `__fxstat64` in `fts_safe_changedir`.

## Risks
This implementation mutates process cwd, which is fragile in multi-threaded programs or when mixed with code expecting cwd stability. Path lengths are capped below `USHRT_MAX` because `FTSENT.fts_pathlen` is a `u_short`; very deep paths fail with `ENAMETOOLONG`. `fts_padjust` must update every outstanding pointer after reallocating the shared path buffer, making pointer ownership subtle. `fts_safe_changedir` protects against directory replacement races but still relies on fd/cwd semantics. Memory allocation failures set `FTS_STOP` and can leave traversal terminated.

## Test Signals
Useful tests should cover empty roots, zero-length root rejection, preorder/postorder ordering, sorted and unsorted traversal, `FTS_NOSTAT`, `FTS_NOCHDIR`, `FTS_XDEV`, `FTS_SKIP`, `FTS_AGAIN`, symlink follow/no-follow, dangling symlinks, cycle detection, long-path growth, dot entry handling, unreadable directories, and cwd restoration after `fts_close`. Integration tests should exercise OrangeFS tools that call `fts_open` over both local and PVFS-mounted trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/fts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/fts.h -->
# sources/distributed-fs/orangefs/src/client/usrint/fts.h

## Purpose
`fts.h` declares the BSD file tree traversal interface used by OrangeFS usrint code and user tools. It is a bundled compatibility header rather than a thin include of a platform header, allowing the project to build the paired `fts.c` implementation consistently while routing libc-internal helper names through normal POSIX symbols for the PVFS user library.

## Important APIs, Types, And Constants
The central types are `FTS`, the traversal stream, and `FTSENT`, the node returned to callers. `FTS` contains the current node, pending children, sort array, root fd, path buffer, comparator, and options. `FTSENT` contains tree links, user fields (`fts_number`, `fts_pointer`), access/root paths, errno, symlink fd, path/name lengths, inode/device/link metadata, depth, info code, private flags, caller instruction, stat pointer, and inline name storage. Public option bits include `FTS_COMFOLLOW`, `FTS_LOGICAL`, `FTS_NOCHDIR`, `FTS_NOSTAT`, `FTS_PHYSICAL`, `FTS_SEEDOT`, `FTS_XDEV`, and `FTS_WHITEOUT`; private bits include `FTS_NAMEONLY` and `FTS_STOP`. Public node info codes include `FTS_D`, `FTS_DP`, `FTS_F`, `FTS_SL`, `FTS_SLNONE`, `FTS_DNR`, `FTS_ERR`, `FTS_NS`, and `FTS_DC`. Caller instructions are `FTS_AGAIN`, `FTS_FOLLOW`, `FTS_NOINSTR`, and `FTS_SKIP`.

## Control Flow Contract
Callers create a stream with `fts_open`, repeatedly call `fts_read` to walk entries, optionally call `fts_children` while positioned on a directory, modify traversal with `fts_set`, and release resources with `fts_close`. The header documents enough state for callers to inspect `fts_info`, `fts_level`, `fts_accpath`, `fts_path`, `fts_statp`, and cycle/error fields.

## State And Persistence Behavior
The header defines only in-process traversal state. `FTSENT` user fields allow application-level annotations during traversal, but there is no persistence beyond the stream lifetime. The fields expose enough internals that callers may depend on struct layout, so ABI compatibility matters.

## Dependencies And Integration Points
The header includes `<features.h>` and `<sys/types.h>`, and it expects `struct stat` from surrounding includes or implementation context. The OrangeFS modifications define `internal_function`, map libc-private functions (`__open`, `__close`, `__opendir`, `__readdir`, `__closedir`, `__fchdir`) to normal symbols, and define `__set_errno` when needed. The original large-file-interface exclusion is disabled, allowing usrint builds to use this header in `_FILE_OFFSET_BITS=64` environments.

## Risks
Because this header exposes concrete structs, mismatches between `fts.h` and `fts.c` are ABI-breaking. The `u_short` path/name lengths imply path-size ceilings inherited from the implementation. The disabled LFS incompatibility guard may hide subtle platform differences if external code expects system `fts.h` behavior. Private flags and macros are visible to all includers, so accidental misuse is possible.

## Test Signals
Compile tests should include both 32-bit and 64-bit file-offset configurations, C and C++ declaration contexts via `__BEGIN_DECLS`, and user code that inspects all public `FTSENT` fields. Runtime tests should pair the header with `fts.c` and validate all option/info/instruction constants against expected traversal behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/fts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/glob.c -->
# sources/distributed-fs/orangefs/src/client/usrint/glob.c

## Purpose
`glob.c` is a bundled glibc-derived pathname glob implementation for the OrangeFS usrint library. It expands shell-style patterns into `glob_t.gl_pathv` results while supporting GNU extensions such as brace expansion, tilde expansion, alternate directory callbacks, mark-only-directory behavior, no-sort behavior, and metacharacter detection. The local changes make the file build outside glibc by mapping internal allocation, stat, readdir, and strdup helpers to normal libc/POSIX interfaces.

## Important APIs And Functions
The exported functions are `glob`, `globfree`, `__glob_pattern_type`, and `glob_pattern_p`/`__glob_pattern_p` when enabled. Major helpers include `next_brace_sub`, which finds comma or closing-brace boundaries while honoring nesting and escaping; `glob_in_dir`, which scans one directory for a final path component; `prefix_array`, which prepends directory names to matched base names; `collated_compare`, which sorts with `strcoll`; and `link_exists2_p`, which verifies symlink targets for directory entries that might be symlinks.

## Control Flow
`glob` first validates the pattern, flags, and result pointer. If `GLOB_BRACE` is set, it detects a brace expression, builds each alternative into a temporary pattern, recursively calls `glob` with `GLOB_APPEND`, and either returns matches or falls through according to `GLOB_NOCHECK`/`GLOB_NOMAGIC`. It initializes `gl_pathv` and offsets for non-append calls, splits the pattern into directory and filename portions, handles trailing slash patterns, expands `~` and `~user` using `HOME`, `getlogin_r`, and passwd lookups, then decides whether the directory portion itself contains magic. If the directory portion is magic, it recursively globs directories with `GLOB_ONLYDIR`, then runs `glob_in_dir` inside each directory and prefixes results. Otherwise it unescapes the directory when needed and calls `glob_in_dir` once. After matching, it appends slashes for `GLOB_MARK`, sorts unless `GLOB_NOSORT`, and returns POSIX/GNU status codes.

`glob_in_dir` handles the final component. If there is no magic and `GLOB_NOCHECK`/`GLOB_NOMAGIC` applies, it can return the literal name. Otherwise it stats a literal name or opens the directory, loops through `readdir`/alternate `gl_readdir`, applies `fnmatch` with `FNM_PERIOD` and `FNM_NOESCAPE` flags, filters `GLOB_ONLYDIR`, verifies symlink targets when needed, accumulates names in stack/heap `globnames` blocks, reallocates `gl_pathv`, appends results, and closes the stream preserving `errno`.

## State And Persistence Behavior
All state is caller-visible through `glob_t`. The implementation allocates `gl_pathv` and each matched path string; callers must release them with `globfree`. `GLOB_APPEND` preserves previous results and adds new entries after `gl_offs + gl_pathc`. No durable state is written, but environment/passwd lookups influence tilde expansion.

## Dependencies And Integration Points
The file includes `usrint.h`, `glob.h`, `fnmatch.h`, dirent/stat/pwd/unistd facilities, and libc compatibility macros. `GLOB_ALTDIRFUNC` allows callers to inject `gl_opendir`, `gl_readdir`, `gl_closedir`, `gl_stat`, and `gl_lstat`, which is the key integration hook for virtualized filesystems. Normal builds use `opendir`, `readdir`, `stat`, `strcoll`, `malloc/realloc/free`, `mempcpy`, and passwd lookup APIs.

## Risks
The implementation has many recursive paths, so brace expansion and globbed directory prefixes can amplify work and memory. The non-glibc portability layer disables glibc's dynamic alloca heuristics by making `__libc_use_alloca(n)` false, pushing more allocations to the heap. Alternate directory callbacks must exactly match expected `glob_t` signatures and return stable dirent/stat data. Several code paths free `pglob` on error, so append users must observe return codes carefully. Tilde expansion depends on environment and passwd state, which may make tests environment-sensitive.

## Test Signals
Tests should cover wildcard matching, bracket expressions, escaped metacharacters, `GLOB_NOESCAPE`, leading-dot behavior with and without `GLOB_PERIOD`, `GLOB_NOCHECK`, `GLOB_NOMAGIC`, `GLOB_DOOFFS`, `GLOB_APPEND`, sorting/locale collation, trailing slash handling, `GLOB_MARK`, `GLOB_ONLYDIR`, brace expansions including malformed braces, tilde expansion success/failure, `GLOB_TILDE_CHECK`, error callback behavior, directory read errors with `GLOB_ERR`, and `GLOB_ALTDIRFUNC` over a fake directory tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/glob.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/glob.h -->
# sources/distributed-fs/orangefs/src/client/usrint/glob.h

## Purpose
`glob.h` is the public compatibility header for the bundled glob implementation. It defines the POSIX and GNU glob flags, result structures, status codes, and function prototypes used by OrangeFS usrint builds, including large-file variants when enabled.

## Important APIs, Types, And Constants
The main type is `glob_t`, containing `gl_pathc`, `gl_pathv`, `gl_offs`, `gl_flags`, and optional alternate directory functions. Under large-file support it also defines `glob64_t` with `struct dirent64`/`struct stat64` callback signatures. User flags include POSIX options (`GLOB_ERR`, `GLOB_MARK`, `GLOB_NOSORT`, `GLOB_DOOFFS`, `GLOB_NOCHECK`, `GLOB_APPEND`, `GLOB_NOESCAPE`, `GLOB_PERIOD`) and GNU/BSD extensions (`GLOB_MAGCHAR`, `GLOB_ALTDIRFUNC`, `GLOB_BRACE`, `GLOB_NOMAGIC`, `GLOB_TILDE`, `GLOB_ONLYDIR`, `GLOB_TILDE_CHECK`). Return codes are `GLOB_NOSPACE`, `GLOB_ABORTED`, `GLOB_NOMATCH`, and `GLOB_NOSYS`, with `GLOB_ABEND` as a GNU compatibility alias.

## Control Flow Contract
Callers pass a pattern, flags, optional error callback, and `glob_t` to `glob`; results are returned in `gl_pathv` with `gl_pathc` entries after any `gl_offs` reserved null slots. `GLOB_APPEND` allows multiple calls to accumulate results, and `globfree` releases allocations. `glob_pattern_p` is a GNU helper for checking whether a pattern contains unquoted metacharacters.

## State And Persistence Behavior
The header describes caller-owned result state but no persistent storage. The callback fields become active only when `GLOB_ALTDIRFUNC` is set; otherwise the implementation ignores them. The structure layout is ABI-sensitive because callers allocate `glob_t`.

## Dependencies And Integration Points
The header includes `<sys/cdefs.h>` and defines `__size_t`/`size_t` compatibly with feature macros. GNU feature macros control visibility of `struct stat`-typed callbacks and the `glob_pattern_p` extension. `_FILE_OFFSET_BITS=64` builds redirect `glob` and `globfree` to `glob64`/`globfree64`, while `__USE_LARGEFILE64` exposes explicit 64-bit APIs.

## Risks
Feature-macro-dependent typedefs and callback signatures can differ between compilation units if they include the header under different macro sets. Alternate directory callbacks must conform to the visible signature, especially with GNU vs non-GNU dirent/stat types. Redirected large-file prototypes need to match the compiled implementation, or callers may link against missing `glob64` symbols.

## Test Signals
Compile tests should cover POSIX-only, GNU, BSD, and large-file macro configurations. ABI tests should confirm `glob_t` layout and callback field offsets are stable for the usrint build. Runtime tests should pair this header with `glob.c` and exercise every flag exposed in `__GLOB_FLAGS`, including `GLOB_ALTDIRFUNC` and large-file redirects when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/glob.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/iocommon.c -->
# sources/distributed-fs/orangefs/src/client/usrint/iocommon.c

## Purpose
`iocommon.c` is the central OrangeFS/PVFS user-interface bridge that implements low-level operations behind the POSIX interposition layer. It converts libc-like operations into `PVFS_sys_*` and `PVFS_isys_*` calls, manages credentials, resolves paths across PVFS and non-PVFS namespaces, allocates `pvfs_descriptor` objects, maps PVFS attributes into POSIX structs, performs data I/O with optional user cache support, and implements metadata, directory, xattr, statfs, and sendfile helpers.

## Important APIs And Functions
Credential and initialization support is handled by `iocommon_cred`, which caches and refreshes a static `PVFS_credential`. Lookup/open functions include `iocommon_lookup_absolute`, `iocommon_lookup_relative`, `iocommon_lookup`, `iocommon_expand_path`, `iocommon_parse_serverlist`, `iocommon_create_file`, and `iocommon_open`. File mutation and positioning APIs include `iocommon_fsync`, `iocommon_truncate`, `iocommon_lseek`, `iocommon_remove`, `iocommon_unlink`, `iocommon_rmdir`, and `iocommon_rename`. I/O paths are `iocommon_readorwrite`, `iocommon_vreadorwrite`, `iocommon_readorwrite_nocache`, and `iocommon_ireadorwrite`. Metadata APIs include `iocommon_getattr`, `iocommon_setattr`, `iocommon_stat`, `iocommon_stat64`, `iocommon_chown`, `iocommon_getmod`, `iocommon_chmod`, `iocommon_make_directory`, `iocommon_readlink`, `iocommon_symlink`, `iocommon_getdents`, `iocommon_getdents64`, `iocommon_access`, `iocommon_statfs`, `iocommon_statfs64`, `iocommon_sendfile`, and extended-attribute helpers.

## Control Flow
Most functions start by validating descriptors or paths, ensuring PVFS initialization through `PVFS_INIT`, obtaining credentials with `iocommon_cred`, calling one or more PVFS system-interface operations, and normalizing PVFS errors through `IOCOMMON_CHECK_ERR`. Absolute lookup qualifies and expands paths, resolves mount points, handles already-expanded `PVFS_path_t` state, and calls `PVFS_sys_lookup`. Relative lookup breaks long paths into `PVFS_NAME_MAX` chunks and iterates `PVFS_sys_ref_lookup`. `iocommon_open` first tries direct lookup, falls back to `PVFS_expand_path` when a symlink exits PVFS, handles `O_CREAT` by looking up/creating the parent, respects `O_EXCL`, allocates a descriptor through `pvfs_alloc_descriptor`, fetches attributes to set mode/type/path state, then applies `O_TRUNC` or `O_APPEND`.

Blocking vector I/O computes aggregate byte counts, converts iovecs into PVFS request objects, calls `PVFS_sys_io`, returns `io_resp.total_completed`, and frees requests. If `PVFS_UCACHE_ENABLE` and `ucache_enabled` are active with a file cache entry, `iocommon_readorwrite` maps requested offsets to cache blocks, records hits/misses, reads partial or missing blocks into cache, handles write-through cache size updates and dirty-block copies, and falls back to uncached I/O when cache limits or insertions fail. Nonblocking I/O builds a contiguous memory request, calls `PVFS_isys_io`, advances the descriptor file pointer by request size, and returns the op id plus response/request handles to the caller.

## State And Persistence Behavior
Global state includes `pvfs_errno`, set when a PVFS-specific non-errno error is mapped to `errno = EIO`, and the static credential buffer in `iocommon_cred`. Descriptor state lives in `pvfs_descriptor_status`: `pvfs_ref`, flags, mode, deferred mode bits, `file_pointer`, directory `token`, directory path, and optional `fent` cache entry. Directory iteration persists through `pd->s->token` and `pd->s->file_pointer`. The user cache persists dirty in-memory blocks until flush/removal; `iocommon_fsync` flushes cache entries before `PVFS_sys_flush`. Server-side durable changes occur through create, remove, rename, truncate, setattr, mkdir, symlink, xattr, and write operations.

## Dependencies And Integration Points
The file includes `usrint.h`, `posix-ops.h`, `openfile-util.h`, `iocommon.h`, `pvfs-path.h`, optional `ucache.h`, and `pint-cached-config.h`. It is called heavily from `posix-pvfs.c` wrappers for open/read/write/stat/chmod/chown/xattr/statfs/sendfile and by async helpers. It uses PVFS system-interface calls, cached configuration helpers, path qualification/expansion APIs, descriptor-table helpers, mutexes, user-cache locks, and real libc operations through `glibc_ops` when expansion resolves outside PVFS.

## Risks
`iocommon_cred` uses static mutable credential state without visible locking. `iocommon_lseek` returns from `errorout` without unlocking `pd->s->lock` on some error paths, which is a deadlock risk. Several allocation paths lack immediate null checks or cleanup symmetry, including mmap-like descriptor/path concatenations and xattr key-array allocation. `iocommon_parse_serverlist` leaks `server_array` if too few tokens are supplied after `slist->servers` allocation. The user-cache path uses variable-length arrays sized by request block/copy counts, which can stress stack memory on large requests. Some errors are returned through mixed conventions (`errno`, `pvfs_errno`, PVFS-negative values), so wrapper callers must be disciplined. `sendfile` reads full 8 MiB chunks until EOF without capping the final read to `count`, so byte accounting deserves close testing.

## Test Signals
High-value tests include absolute and relative lookup, mountpoint lookup, long path segmentation, symlink-to-non-PVFS fallback, `openat` with PVFS directory descriptors, `O_CREAT`/`O_EXCL` races, deferred mode bits, `O_TRUNC`, `O_APPEND`, stat/stat64 field mapping, directory `getdents` token progression, lseek on files and directories, unlink/rmdir type checks, rename same-object no-op, mkdir/symlink/readlink, permission checks with `AT_EACCESS` and `AT_SYMLINK_NOFOLLOW`, statfs/statfs64 conversion, xattr get/set/list/delete/atomic translation, fsync with and without user cache, uncached and cached vector I/O including partial EOF blocks, and nonblocking I/O request lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/iocommon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/iocommon.h -->
# sources/distributed-fs/orangefs/src/client/usrint/iocommon.h

## Purpose
`iocommon.h` declares the shared low-level PVFS/OrangeFS user-interface routines implemented in `iocommon.c`. It is the contract between POSIX-facing wrappers, async/cache code, descriptor utilities, and the PVFS system-interface layer.

## Important APIs, Types, And Macros
The cache helper structs `ucache_req_s` and `ucache_copy_s` describe cache block tags, shared-memory block pointers/indexes, and cache-to-user-buffer copy operations. The global `pvfs_errno` reports PVFS-specific errors when `errno` is set to `EIO`. The prototypes cover initialization, credentials, path expansion and lookup, server-list parsing, file creation/open/truncate/lseek/remove/rename, blocking and nonblocking I/O, attribute/stat/statfs operations, extended attributes, ownership/mode changes, directory creation, readlink/symlink, directory reads, access checks, and sendfile.

The `IOCOMMON_RETURN_ERR` macro jumps to `errorout` when a conventional `-1` return is seen. `IOCOMMON_CHECK_ERR` is the key PVFS error adapter: it restores `errno` to `orig_errno`, maps PVFS non-errno errors into `pvfs_errno` plus `EIO`, maps ordinary PVFS errors through `PINT_errno_mapping`, converts the return to `-1`, and jumps to `errorout`.

## Control Flow Contract
Functions using this header generally follow a common pattern: define `int rc`, `int orig_errno = errno`, perform PVFS work, use the macros after PVFS calls, and have an `errorout:` cleanup label returning `rc` or an API-specific value. Callers are expected to pass valid `pvfs_descriptor` objects for descriptor-based operations and `PVFS_object_ref` values for direct object operations.

## State And Persistence Behavior
The header exposes the stateful nature of the subsystem through descriptors, credentials, cache block descriptions, directory tokens hidden inside descriptors, and `pvfs_errno`. Persistent server-side changes are mediated by the declared mutation APIs, while local cache state is coordinated through cache helper structs and `ucache` functions.

## Dependencies And Integration Points
The header includes PVFS public types (`pvfs2.h`, `pvfs2-types.h`, `pvfs2-request.h`, `pvfs2-debug.h`) and `pvfs-path.h`. It assumes POSIX types such as `mode_t`, `off64_t`, `struct iovec`, `struct stat`, `struct statfs`, `struct dirent`, and descriptor types from usrint headers are visible through include order. `posix-pvfs.c`, `aiocommon.c`, `ucache.c`, and path utilities consume this interface.

## Risks
The macros require local variables named `orig_errno`, `rc`, and an `errorout` label; using them outside that pattern is unsafe. `IOCOMMON_CHECK_ERR` mutates `errno` even on errors from PVFS calls, so callers must not rely on syscall-side errno after PVFS returns. Cache helper structs are compiled only meaningfully with `PVFS_UCACHE_ENABLE`, but their declarations are always present. The declared `iocommon_ensure_init` is not implemented in the inspected `iocommon.c`, so link coverage should confirm whether another file provides it or whether it is stale.

## Test Signals
Compile tests should include all consumers of `iocommon.h` and verify prototypes match implementations. Unit or integration tests should intentionally trigger PVFS errors that map to ordinary errno and non-errno PVFS errors, verifying `pvfs_errno` behavior. API tests should cover each descriptor/object operation through the POSIX wrapper layer to ensure the declared contract remains synchronized with implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/iocommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/locks.h -->
# sources/distributed-fs/orangefs/src/client/usrint/locks.h

## Purpose
`locks.h` provides a local replacement for glibc/libio stream lock definitions that are not reliably exported by modern system headers. It lets OrangeFS stdio interposition code store and operate on `_lock` fields in `FILE`-like streams without depending on private libc `_IO_lock_t` definitions.

## Important APIs, Types, And Macros
The key type is `_PVFS_lock_t`, with simple fields `lock`, `cnt`, and `owner`. `_PVFS_lock_initializer` and `_PVFS_lock_finalizer` provide static initializer values. `_PVFS_lock_init` and `_PVFS_lock_fini` write initial/final marker values into `stream->_lock`. `_PVFS_lock_lock`, `_PVFS_lock_trylock`, and `_PVFS_lock_unlock` delegate to `stdio_ops.flockfile`, `stdio_ops.ftrylockfile`, and `stdio_ops.funlockfile`.

## Control Flow
The stdio layer allocates or embeds `_PVFS_lock_t`, assigns it to a stream's `_lock`, initializes it with `_PVFS_lock_init`, then uses the lock/unlock macros around stream operations. Finalization marks the fields as `-1`/`NULL` before deallocation or teardown. Actual synchronization is performed by the underlying stdio operation table rather than by direct atomic operations on the fields.

## State And Persistence Behavior
Lock state is process-local and attached to stream objects. The fields are not persisted and are meaningful only while the stream and its `_lock` pointer remain valid. The `owner` pointer is opaque and initialized to `NULL`.

## Dependencies And Integration Points
This header is consumed by `stdio.c`, which defines static locks for standard streams and allocates locks for PVFS stream wrappers. It requires `stdio_ops` to be in scope with `flockfile`, `ftrylockfile`, and `funlockfile` members. It also assumes stream objects expose a `_lock` member compatible with casting to `_PVFS_lock_t *`.

## Risks
The include guard defines only `LOCKS_H` without setting it to a value, which still works for `#ifndef` but is nonstandard style. The lock fields are not themselves authoritative if `stdio_ops` maintains separate locking state, so code must not inspect them as synchronization truth. The macros directly cast `stream->_lock`; invalid or uninitialized `_lock` pointers will corrupt memory. The trailing backslashes on lock operation macros are harmless in macro definitions but make formatting brittle.

## Test Signals
Tests should cover initialization/finalization for standard and dynamically allocated streams, recursive or nested `flockfile` behavior as mediated by `stdio_ops`, trylock failure paths, and teardown after close. Build tests should compile against current glibc headers where private `_IO_lock_t` is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/locks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/mmap.c -->
# sources/distributed-fs/orangefs/src/client/usrint/mmap.c

## Purpose
`mmap.c` implements minimal mmap-family behavior for PVFS descriptors. It does not provide kernel-backed shared file mappings; instead it maps anonymous memory, reads file contents into that memory, records mapping metadata, and writes shared mappings back on `munmap` or `msync`. Anonymous mappings bypass PVFS and are delegated directly to `glibc_ops.mmap`.

## Important APIs And Functions
The exported functions are `pvfs_mmap`, `pvfs_munmap`, and `pvfs_msync`, registered in `pvfs_ops` by `posix-pvfs.c`. The file maintains a static `maplist` of `struct pvfs_mmap_s` records, whose fields are defined in `posix-ops.h`: mapping start, length, protection, flags, fd, offset, and quicklist link.

## Control Flow
`pvfs_mmap` checks `MAP_ANONYMOUS` first and delegates to glibc for non-file mappings. For PVFS file mappings, it finds the descriptor with `pvfs_find_descriptor`, creates an anonymous mapping through `glibc_ops.mmap`, reads the requested region with `pvfs_pread`, allocates a mapping-list entry, records metadata, and appends it to `maplist`. `pvfs_munmap` validates page alignment, searches for an exact `(start, length)` mapping, removes it, writes the full mapping back with `pvfs_pwrite` when `MAP_SHARED` was set, delegates unmap to glibc, then frees the metadata. `pvfs_msync` validates alignment, finds an existing mapping that fully covers the requested subrange, and writes that subrange back for shared mappings.

## State And Persistence Behavior
The only local state is the process-global `maplist`; there is no per-descriptor registration. File persistence occurs only through explicit `pvfs_pwrite` on shared mappings during `pvfs_munmap` or `pvfs_msync`. Private mappings never write back. The implementation does not track dirty pages, partial unmaps, protection changes, fork inheritance, or invalidation.

## Dependencies And Integration Points
The file includes `usrint.h`, `posix-ops.h`, `posix-pvfs.h`, `openfile-util.h`, and `<quicklist.h>`. It depends on `glibc_ops.mmap/munmap`, descriptor lookup, and PVFS pread/pwrite wrappers. `PVFS2_SIZEOF_VOIDP` controls pointer-width-specific alignment checks.

## Risks
There appears to be a correctness bug: `pvfs_mmap` stores `mlist->mst = start` rather than the returned mapped address `maddr`, so `munmap`/`msync` lookups can fail whenever the kernel does not map exactly at the requested `start` address, including typical `start == NULL` calls. The call to `glibc_ops.mmap` uses `flags & MAP_ANONYMOUS`, which strips most original mapping flags and may not set `MAP_PRIVATE`/`MAP_SHARED` as required by the platform. `pvfs_munmap` declares `mapl` uninitialized and checks `if (!mapl)` after the loop, which is unsafe if the list is empty or no match is found. The global list is not locked, so concurrent mmap/munmap/msync calls can race. Allocation failure for `mlist` is not checked. Writeback errors from `pvfs_pwrite` in `munmap` are ignored.

## Test Signals
Tests should map with `start == NULL`, verify `munmap` succeeds by returned address, exercise exact and subrange `msync`, check `MAP_SHARED` writeback and `MAP_PRIVATE` non-writeback, validate page-alignment errors, map/unmap multiple regions, run concurrent mapping operations, inject `malloc`/`pread`/`pwrite` failures, and compare behavior against POSIX expectations for anonymous mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/module.mk.in -->
# sources/distributed-fs/orangefs/src/client/usrint/module.mk.in

## Purpose
`module.mk.in` contributes the OrangeFS usrint source lists and per-file compiler flags to the repository build system. It decides which files are built into the old library (`OLIBSRC`), the usrint library (`ULIBSRC`), and the common library source set (`LIBSRC`) based on `build_olib` and `build_usrint`.

## Important Build Variables
`DIR` is set to `src/client/usrint`. When `build_olib` is `yes`, `OSRC` contains core PVFS-backed helpers such as `pvfs-path.c`, `mmap.c`, `openfile-util.c`, `iocommon.c`, `request.c`, `ucache.c`, `posix-pvfs.c`, and `env-vars.c`, and the list is appended to `OLIBSRC`. When `build_usrint` is `yes`, the same `OSRC` list is appended to `OLIBSRC`, while `USRC` adds interposition/front-end sources such as `posix.c`, `stdio.c`, `selinux.c`, `overunder.c`, `fts.c`, `glob.c`, `error.c`, and `recursive-remove.c`, and appends them to `ULIBSRC`. `SRC` contains `pvfs-qualify-path.c` and is appended to `LIBSRC`.

## Control Flow
The make fragment is declarative. Build configuration chooses the `build_olib` and `build_usrint` branches. Each branch assigns source lists and appends them to aggregate variables consumed elsewhere by the top-level make logic. The final lines add warning suppressions for `posix.c` and `stdio.c`.

## State And Persistence Behavior
There is no runtime state. The file shapes build outputs by selecting which objects are compiled into which library. Changes here persist only as build metadata.

## Dependencies And Integration Points
The fragment depends on the surrounding OrangeFS make system to define `build_olib`, `build_usrint`, `OLIBSRC`, `ULIBSRC`, `LIBSRC`, and `MODCFLAGS_*` conventions. The inclusion of `fts.c` and `glob.c` in `USRC` explains why those bundled compatibility implementations are part of the usrint build. `mmap.c` and `iocommon.c` are included in both old-library and usrint core lists.

## Risks
`OSRC` is assigned separately inside each branch, so future edits must keep duplicate lists synchronized. The same `OSRC` is appended to `OLIBSRC` in both branches when both build flags are enabled, which may be intentional or may risk duplicate source entries depending on upstream aggregation behavior. Commented-out sources (`acl.c`, `socket.c`) indicate stale or deferred build decisions. Warning suppression is narrow, currently only disabling `-Wnonnull-compare` for `posix.c` and `stdio.c`; similar warnings in other usrint files would fail under stricter builds.

## Test Signals
Build tests should run configurations with only `build_olib`, only `build_usrint`, both enabled, and both disabled if supported. Source-list tests should detect duplicate object entries. Compiler tests should verify that `fts.c`, `glob.c`, `mmap.c`, and `iocommon.c` are included in the expected libraries and that `MODCFLAGS` are applied only to intended files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/old_libio.h -->
# sources/distributed-fs/orangefs/src/client/usrint/old_libio.h

## Purpose
`old_libio.h` supplies legacy glibc/libio flag and marker definitions needed by the OrangeFS stdio/over-under interposition code. It avoids relying on private system `libio` headers while preserving constants expected by code that manipulates `_IO_FILE`-style fields.

## Important APIs, Types, And Constants
The file defines old stream mode bits such as `_IOS_INPUT`, `_IOS_OUTPUT`, `_IOS_ATEND`, `_IOS_APPEND`, `_IOS_TRUNC`, `_IOS_NOCREATE`, `_IOS_NOREPLACE`, and `_IOS_BIN`. It defines `_IO_MAGIC`, `_OLD_STDIO_MAGIC`, `_IO_MAGIC_MASK`, and many `_IO_*` flag bits for buffer ownership, read/write permission, EOF/error state, linked streams, backup state, line buffering, append/current-put mode, filebuf identity, delete/close behavior, and user locking. It also defines `_IO_FLAGS2_*` bits and formatting flags such as `_IO_SKIPWS`, `_IO_LEFT`, `_IO_DEC`, `_IO_HEX`, `_IO_SHOWBASE`, `_IO_FIXED`, `_IO_STDIO`, and `_IO_BOOLALPHA`. The only type is `struct _IO_marker`, which links markers to an `_IO_FILE` buffer and stores a relative position.

## Control Flow
This header has no functions and no control flow. It is included by usrint stdio-related code so that stream setup and compatibility logic can read or set flag bits using the historical names expected by glibc-derived code.

## State And Persistence Behavior
The constants describe in-memory stream state stored in `_IO_FILE`-like objects. The header itself owns no storage and writes no persistent state. Stream flags influence runtime buffering, read/write permissions, EOF/error reporting, append behavior, and cleanup decisions wherever included code applies them.

## Dependencies And Integration Points
`stdio.c` and `overunder.c` include this header. It forward-references `struct _IO_FILE` inside `struct _IO_marker`, relying on libc headers or local declarations to define the full stream type elsewhere. Several constants are guarded by `#ifndef` so they do not conflict if a platform header already provided `_IO_EOF_SEEN` or `_IO_ERR_SEEN`.

## Risks
These are private glibc compatibility constants, so they are sensitive to libc version and platform differences. Code that assumes `_IO_FILE` layout or flag semantics may break on non-glibc or newer glibc implementations. The header intentionally does not include full libio declarations, so includers must arrange compatible declarations. Typos or stale values in these constants could produce subtle stdio behavior rather than compile errors.

## Test Signals
Build tests should compile `stdio.c` and `overunder.c` against current target libc headers. Runtime stdio tests should verify EOF/error propagation, append/write/read mode restrictions, buffering behavior, standard-stream setup, close/delete behavior, and compatibility with `flockfile`/`funlockfile` paths that also use `locks.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/old_libio.h -->
