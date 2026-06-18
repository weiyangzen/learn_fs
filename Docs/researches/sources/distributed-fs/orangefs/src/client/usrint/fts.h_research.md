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
