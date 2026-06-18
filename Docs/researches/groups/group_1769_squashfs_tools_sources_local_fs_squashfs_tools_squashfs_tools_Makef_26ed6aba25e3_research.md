# Group Research: group_1769_squashfs_tools_sources_local_fs_squashfs_tools_squashfs_tools_Makef_26ed6aba25e3

Scope verified against `Docs/research_subset_a.md`: `sources/local-fs/squashfs-tools` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/Makefile -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/Makefile

Top-level build recipe for the SquashFS tools in this subtree. It builds `mksquashfs` plus symlink `sqfstar`, and `unsquashfs` plus symlink `sqfscat`.

Main responsibilities:
- Defines configurable compression support: gzip, xz, lzo, lz4, zstd by default; obsolete lzma variants optional.
- Defines xattr support switches: generic xattr support, OS xattr support, and default xattr behavior.
- Defines reader thread defaults and validates thread counts against `MAX_READER_THREADS`.
- Selects compressor wrapper objects, libraries, and `COMPRESSORS` help text based on enabled options.
- Injects build-time `COMP_DEFAULT`, `VERSION`, `DATE`, and `YEAR` into `CFLAGS`.
- Builds object lists for `mksquashfs` and `unsquashfs`, including feature-gated xattr/compressor objects.
- Installs binaries, symlinks, and generated or prebuilt manpages through `generate-manpages/install-manpages.sh`.

Important dependency behavior:
- `CONFIG=1 make` flips many defaults to command-line-overridable `?=` values and uses different reader-thread defaults.
- `COMP_DEFAULT` must be set and must appear in the selected `COMPRESSORS`.
- `LZMA_XZ_SUPPORT` and `LZMA_SUPPORT` are mutually exclusive.
- At least one compressor must be enabled.

Notable quirks:
- `INSTALL_MANPAGES_DIR` default differs between normal and `CONFIG=1` branches: `/usr/local/share/man/man1` vs `/usr/local/man/man1`.
- Installation script arguments are not shell-quoted, so paths containing spaces are not robust.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/action.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/action.c

Implements the `mksquashfs` action language: parsing, expression evaluation, test predicates, action dispatch, xattr rule evaluation, move scheduling, symlink dereference tests, and action-file reading.

Core parser behavior:
- `read_file()` reads action files line-by-line, supports `\` continuations, skips blank lines and `#` comments, and enforces `MAX_LINE` chunks.
- `get_token()` tokenizes punctuation/operators and quoted/escaped strings.
- `parse_expr()` parses left-associative `&&`/`||`, unary `!`, parenthesized subexpressions, and test atoms.
- `parse_action()` parses `action(args)@expr`, validates action name/argument count, calls action-specific argument parsing, then appends the action to the relevant global list.

Action categories maintained as global arrays:
- Fragment placement: `fragment`, plus defaults/tail fragments.
- Exclusion/pruning: `exclude`, `prune`, `empty`.
- Symlink handling: `dereference`.
- Metadata rewrites: `uid`, `gid`, `guid`, `mode`/`chmod`, fragment/compression flags, `align`, `noop`.
- Tree rewrite: `move`.
- Xattr filtering/injection: `xattrs-exclude`, `xattrs-include`, `xattrs-add`.

Evaluation behavior:
- `eval_expr()` short-circuits logical operations.
- Verbose action logging records expression evaluation and prints via `progressbar_info()` only for selected true/false outcomes.
- `file_type_match()` restricts tests/actions to regular files, directories, symlinks, or all supported filesystem object types.
- Public evaluators build `struct action_data` from `dir_ent`, pathname/subpathname, stat buffer, root, and depth.

Move action behavior:
- Move actions are first evaluated into `move_ent` records rather than immediately mutating the tree.
- Multiple compatible move actions may merge rename and destination changes.
- Conflicting renames/destinations and moves into self-subdirectories are reported.
- `do_move_actions()` applies queued moves after scanning and rechecks destination conflicts.

Xattr behavior:
- Include/exclude actions compile POSIX extended regexes.
- Matching actions produce linked lists of regex rules for later xattr filtering.
- `xattrs-add` delegates parsing to `xattr_parse()` and returns matched `struct xattr_add` records.

Supported tests include:
- Name/path matching: `name`, `pathname`, `subpathname`.
- Numeric comparisons and ranges for size, tailsize, inode, blocks, uid/gid, nlink, depth, dircount.
- User/group lookup by name.
- File type, true/false, permission expressions.
- External `file(1)` regex test and shell `exec` test.
- Symlink tests: `exists`, `absolute`, `stat(expr)`, `readlink(expr)`.
- Contextual `eval(path, expr)` over another output-tree entry.

Notable risks/quirks:
- `file_fn()` forks `file -b` and treats command failure as fatal via `BAD_ERROR`.
- `exec_fn()` executes `/bin/sh -c` with file path context in environment variables.
- Many parser allocations are intentionally process-lifetime; failed parse paths free only some intermediate arrays.
- `error.h` fatal macros are used for internal invariants, so some filesystem/action errors terminate the whole process.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/action.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/action.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/action.h

Public interface and data model for `action.c`.

Defines:
- Lexer token IDs and token table record shape.
- Expression tree node types: binary op, atom/test, unary op.
- Syntax-error reporting macros with source-position context.
- Numeric comparison/range parse structures.
- `struct test_entry` for action-language predicate registry.
- Action IDs and file-type applicability constants.
- Action logging constants for true/false/verbose action diagnostics.
- `struct action_entry`, `struct action_data`, and `struct action`.
- Per-action data structs for uid/gid/guid, empty policy, move queue, xattr regexes, alignment, dereference policy, and permission tests.

External API:
- Parses individual actions and action files.
- Evaluates action classes: fragment, exclude, dereference, empty, move, prune, xattr include/exclude/add, and general metadata actions.
- Exposes counters such as `any_actions()`, `move_actions()`, `xattr_add_actions()`.
- Exposes `do_move_actions()` and `dump_actions()`.

Notable coupling:
- Depends on `struct dir_ent`, `struct dir_info`, `struct inode_info`, and `struct xattr_add` from other mksquashfs internals.
- Declares `read_bytes()` despite its implementation living outside this file group.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/action.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/alloc.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/alloc.h

Small allocation wrapper header.

Provides inline wrappers:
- `_calloc`, `_malloc`, `_realloc`
- `_strdup`, `_strndup`
- `_vasprintf`, `_asprintf`

Macros pass `__func__` into each wrapper:
- `CALLOC`, `MALLOC`, `REALLOC`, `STRDUP`, `STRNDUP`, `VASPRINTF`, `ASPRINTF`.

Behavior:
- Any allocation or formatting allocation failure calls `MEM_ERROR(func)`, which logs, performs pre-exit cleanup, and exits.
- Reexports `TRUE` and `FALSE` constants.

Key role: centralizes fail-fast allocation handling across SquashFS tools.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/alloc.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/atomic_swap.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/atomic_swap.h

Provides `atomic_swap()` for `struct read_entry **`.

Two implementations:
- Default: uses GCC/Clang `__atomic_exchange_n(entry, NULL, __ATOMIC_SEQ_CST)`.
- Fallback under `DONT_USE_ATOMIC_EXCHANGE_N`: locks a supplied `pthread_mutex_t`, reads `*entry`, clears it to `NULL`, and unlocks.

Key role: lockless or mutex-backed handoff primitive for reader synchronization.

Notable detail: the fallback uses pthread cleanup handlers so cancellation unlocks the mutex correctly.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/atomic_swap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/caches-queues-lists.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/caches-queues-lists.c

Implements the shared pthread queue/cache infrastructure used by the mksquashfs pipeline.

Main components:
- `struct queue`: bounded circular queue with `empty`/`full` condition variables.
- `struct seq_queue`: hash-backed sequence queue that lets producer threads finish out of order while consumers retrieve in deterministic order.
- `struct read_queue`: per-reader circular queues merged by earliest file/version/block ordering.
- `struct cache`: lookup-capable or shrinking cache of `file_buffer` objects.
- `struct queue_cache`: combined read queue and write-buffer cache for atomically selecting input buffers and allocating output buffers.

Queue behavior:
- `queue_put()` and `queue_get()` block on full/empty conditions.
- `queue_get_tid()` integrates thread-idle tracking before waiting.
- Flush/dump helpers reset or report queue state.

Sequence queues:
- `main_queue_put/get()` order by `file_count`, `block`, and `version`, updating state according to `NEXT_BLOCK`, `NEXT_FILE`, or `NEXT_VERSION`.
- `order_queue_put/get()` order by monotonic `sequence`.
- Hash tables reduce ordered lookup cost.

Caches:
- `cache_init()` supports grow/shrink policy and freelist-first vs grow-first behavior.
- `cache_lookup()` increments use counts and removes reused entries from the freelist.
- `cache_get()` allocates or reuses blocks, optionally hashing by index.
- `cache_get_nowait()` creates a locked entry or returns `NULL` if no buffer is available.
- `cache_wait_unlock()` and `cache_unlock()` coordinate consumers waiting for another thread to fill a locked buffer.
- `cache_block_put()` decrements references and either freelists or frees the buffer.

Combined queue/cache:
- `queue_cache_set()` creates per-thread read queues and write-cache pools.
- `queue_cache_get_tid()` chooses the earliest readable buffer from a thread that also has write-buffer capacity, then returns both read and write buffers together.
- `queue_cache_hash()`, lookup, put, flush, and dump mirror the generic cache semantics.

Safety checks:
- Queue and buffer allocation sizes use external `add_overflow()` and `multiply_overflow()` checks.
- Internal impossible states use `BAD_ERROR()`.

Notable quirks:
- Most data structures are never destroyed; they are process-lifetime pipeline infrastructure.
- Correctness relies on callers respecting buffer type and reference-count protocols.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/caches-queues-lists.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/caches-queues-lists.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/caches-queues-lists.h

Header for the mksquashfs queue/cache subsystem.

Defines macro generators:
- `INSERT_LIST` / `REMOVE_LIST` for circular doubly-linked freelists.
- `INSERT_HASH_TABLE` / `REMOVE_HASH_TABLE` for doubly-linked hash buckets.

Core constants:
- `HASH_SIZE` 65536 and `CALCULATE_HASH`.
- Next-state values: `NEXT_BLOCK`, `NEXT_FILE`, `NEXT_VERSION`.
- Buffer source/type values: `QUEUE_CACHE`, `GEN_CACHE`, `WSYNC_CMD`, `RESET_CMD`, `MAP_CMD`.

Defines all queue/cache structs:
- `file_buffer`: central buffer envelope carrying index, sequence/file/block ordering, data size, compressed byte count, checksum, flags, ownership pointers, list/hash links, and inline aligned data.
- `queue`, `seq_queue`, `readq_thrd`, `read_queue`, `cache`, `writeq_thrd`, `queue_cache`.

Exports the queue/cache API implemented in `caches-queues-lists.c`.

Inline helpers:
- `gen_cache_block_put()` dispatches release by buffer type.
- `cache_maxsize()` returns the owning cache capacity.
- `is_sparse()`, `set_sparse()`, and `sparse_count()` encode sparse extents using negative `c_byte`.

Notable risks/quirks:
- `cache_maxsize()` has fatal error paths in an `int` inline function with no return after `BAD_ERROR()`.
- Sparse length is limited to `INT_MAX`.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/caches-queues-lists.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/compressor.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/compressor.c

Compressor registry and help display implementation.

Behavior:
- Creates stub compressor records for algorithms not compiled in, and imports real `*_comp_ops` records for enabled algorithms.
- Maintains ordered global `compressor[]`: gzip, lzo, lz4, xz, zstd, lzma, unknown.
- `lookup_compressor(name)` and `lookup_compressor_id(id)` return matching records or the unknown sentinel.
- `valid_compressor()` checks whether a named compressor is supported in this build.
- `display_compressor_usage()` prints available compressors and compressor-specific option help.
- `print_selected_comp_options()` and `print_comp_options()` print one compressor’s options or all options.

Key role: runtime bridge between CLI parsing/help and compressor wrapper vtables.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/compressor.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/compressor.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/compressor.h

Defines the compressor vtable contract.

`struct compressor` fields cover:
- SquashFS compressor ID and display name.
- Whether the compressor is compiled/supported.
- Optional init hook.
- Required compress/uncompress hooks.
- Optional command-line option parsing and postprocessing.
- Optional dump/extract/check/display of on-disk compressor options.
- Optional help and option-arity helpers.

Inline wrappers:
- Provide null-safe defaults for optional hooks.
- Treat missing `extract_options` as accepting only zero-sized option blocks.
- Treat missing `check_options` as success.
- Treat missing `option_args` as no extra args.

Key role: common ABI for gzip, lzo, lz4, xz/zstd/lzma wrappers and callers in mksquashfs/unsquashfs.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/compressor.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/crc16.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/crc16.c

Implements a table-driven CRC16 checksum.

Main function:
- `get_checksum(char *buff, int bytes, unsigned short chksum)`

Behavior:
- Uses a 256-entry precomputed table.
- Iterates over input bytes and updates the supplied checksum seed.
- Based on `libcrc` CRC16 code according to the file comment.

Key role: checksum helper for unsquashfs-side data validation paths.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/crc16.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/crc16.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/crc16.h

Header for the CRC16 helper.

Exports:
- `get_checksum(char *buff, int bytes, unsigned short chksum)`

Notable quirk:
- Include guard is named `HASH_H`, not `CRC16_H`, which is harmless only if no unrelated header uses the same guard name.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/crc16.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/date.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/date.c

Implements date-string parsing by delegating to the system `date` command.

Main function:
- `exec_date(char *string, unsigned int *mtime, char **error)`

Behavior:
- Creates a pipe and forks.
- Child redirects stdout/stderr to the pipe and runs `/usr/bin/date -d <string> +%s`.
- Parent reads command output, waits for child, parses seconds since epoch, and validates the result fits unsigned 32-bit SquashFS time.
- Rejects negative times and times on/after `2^32`.

Dependencies:
- Uses external `read_bytes()`.
- Uses `ASPRINTF()` for error strings.

Notable risks/quirks:
- Hard-codes `/usr/bin/date` and GNU-style `-d`.
- Reads into an 11-byte buffer and validates output length before parsing.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/date.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/date.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/date.h

Small header for `date.c`.

Exports:
- External `read_bytes(int, void *, long long)` used by `exec_date()`.

Defines:
- `TRUE` and `FALSE`.

Notable quirk:
- Does not declare `exec_date()` itself, so callers must get that prototype elsewhere or compile without strict prototype checking.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/date.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/endian_compat.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/endian_compat.h

Portability shim for byte-order macros.

Behavior:
- On Linux, includes `<endian.h>`.
- On non-Linux systems, includes `<sys/types.h>` and maps:
  - `__BYTE_ORDER` to `BYTE_ORDER`
  - `__BIG_ENDIAN` to `BIG_ENDIAN`
  - `__LITTLE_ENDIAN` to `LITTLE_ENDIAN`

Key role: lets compressor option headers use Linux-style endian macros across platforms.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/endian_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/error.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/error.h

Shared error/logging macro header.

Declares:
- `progressbar_error()`
- `progressbar_info()`
- `pre_exit_squashfs()`

Defines:
- `TRACE()` under `SQUASHFS_TRACE`, otherwise no-op.
- `ERROR()` as progressbar error logging.
- `MEM_ERROR()` as fatal out-of-memory logging plus `pre_exit_squashfs()` and `exit(1)`.
- `BAD_ERROR()` as fatal internal/error logging plus cleanup and exit.

Notable quirk:
- The include guard ends before `MEM_ERROR` and `BAD_ERROR`, so those macros are outside the guard and can be reprocessed on repeated includes.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/error.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/fnmatch_compat.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/fnmatch_compat.h

Compatibility header for pattern matching.

Behavior:
- Includes `<fnmatch.h>`.
- Defines `FNM_EXTMATCH` to `0` if the platform does not provide it.

Key role: allows action-language pattern matching to request extended match syntax where available while remaining buildable on platforms without that flag.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/fnmatch_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/functions.sh -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/functions.sh

Shared shell helpers for manpage generation scripts.

Provides:
- `print()` and `error()` wrappers using an external `echo` binary.
- `check_sed()` to verify a sed executable supports GNU-compatible `-i` behavior and `\U` replacement uppercasing.
- `set_sed()` to use a supplied `SED`, otherwise discover `sed` or `gsed`.

Startup behavior:
- Requires non-builtin `echo` to exist in `PATH`.
- Stores `ECHO=$(which echo)` for later use.

Key role: centralizes GNU sed detection because generated manpage scripts rely on GNU sed extensions.

Notable risks/quirks:
- Uses unquoted shell variables in several command invocations, so paths with whitespace are fragile.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/functions.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/install-manpages.sh -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/install-manpages.sh

Installer helper for SquashFS tool manpages.

Arguments:
- Source/git root path.
- Manpage install directory.
- Whether to force prebuilt manpages (`y`/`n`).

Behavior:
- Validates source root by checking for `squashfs-tools/generate-manpages/functions.sh`.
- Sources shared functions.
- Skips cleanly if install path is empty.
- Requires `gzip`.
- Uses prebuilt manpages when requested, when GNU sed is unavailable, when `help2man` is unavailable, or when custom generation fails.
- Attempts to generate custom manpages for `mksquashfs`, `unsquashfs`, `sqfstar`, and `sqfscat`.
- Installs and gzip-compresses each `.1` page with `gzip -n -f9`.

Notable risks/quirks:
- Many variables and paths are unquoted.
- Fallback warning text contains nested unescaped `"y"` inside a double-quoted string, which is shell-fragile as written.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/install-manpages.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/mksquashfs-manpage.sh -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/mksquashfs-manpage.sh

Generates a `mksquashfs(1)` manpage from live `mksquashfs -help-all` and `-version` output using `help2man`.

Workflow:
- Must be run from `generate-manpages`.
- Requires GNU sed, `expand`, and `help2man`.
- Validates the supplied directory contains executable `mksquashfs`.
- Captures help and version output into a temp directory.
- Creates a temporary wrapper executable that serves modified help/version text to `help2man`.
- Normalizes version/copyright/author output.
- Rewrites help text into `help2man`-friendly sections and option layouts.
- Uses `mksquashfs.h2m` include file.
- Removes the temp directory after successful generation.

Transformations include:
- Converts `SYNTAX:` to `Usage:`.
- Inserts `*OPTIONS*`.
- Indents options for `help2man`.
- Expands shortened operands and uppercases manpage operands.
- Concatenates compressor lists and LZO algorithm lists.
- Turns compressor names and pseudo file format text into manpage sections.
- Adds See Also references to `unsquashfs(1)`, `sqfstar(1)`, and `sqfscat(1)`.
- Sectionizes Environment, Exit status, See also, and Symbolic mode specification.

Notable quirks:
- Temp cleanup is skipped on earlier failure exits.
- Heavily depends on exact `mksquashfs -help-all` formatting.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/mksquashfs-manpage.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/sqfscat-manpage.sh -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/sqfscat-manpage.sh

Generates a `sqfscat(1)` manpage from live `sqfscat -help-all` and `-version` output using `help2man`.

Workflow:
- Requires running from `generate-manpages`.
- Requires GNU sed and `help2man`.
- Validates executable `sqfscat` under the supplied path.
- Captures help/version output, wraps it with a temporary script, edits it, then calls `help2man -Ni sqfscat.h2m`.
- Removes the temp directory after success.

Transformations:
- Converts `SYNTAX:` to `Usage:`.
- Inserts `*OPTIONS*`.
- Splits bracketed short/long option forms into explicit alternatives.
- Uppercases and removes angle brackets from operands.
- Concatenates decompressor list and multi-line option descriptions.
- Concatenates exit status, `PAGER`, and `SQFS_CMDLINE` text.
- Sectionizes Decompressors available, Exit status, See also, and Environment.
- Adds See Also references to `mksquashfs(1)`, `unsquashfs(1)`, and `sqfstar(1)`.

Notable quirk:
- Duplicate comment line for “Make Decompressors available header”.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/sqfscat-manpage.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/sqfstar-manpage.sh -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/sqfstar-manpage.sh

Generates a `sqfstar(1)` manpage from live `sqfstar -help-all` and `-version` output.

Workflow:
- Must run from `generate-manpages`.
- Requires GNU sed, `expand`, and `help2man`.
- Validates executable `sqfstar`.
- Captures expanded help and version output.
- Creates a temp wrapper script for `help2man`.
- Uses `sqfstar.h2m` to supply replacement front matter.
- Removes temp directory after successful generation.

Transformations:
- Joins wrapped first syntax line, inserts `*OPTIONS*`, then deletes original first line because `sqfstar.h2m` supplies that content.
- Indents options and compressor options.
- Adds spacing for long option descriptions.
- Uppercases operands, then restores quoted pseudo-definition forms where case matters.
- Concatenates compressor and LZO algorithm lists.
- Converts pseudo file definitions into option-like lines.
- Sectionizes compressor options, pseudo definition format, exit status, see also, environment, and symbolic mode specification.
- Adds See Also references to `mksquashfs(1)`, `unsquashfs(1)`, and `sqfscat(1)`.

Notable quirks:
- Performs both global angle-bracket removal and a later targeted removal expression, making the second mostly redundant.
- Depends closely on current help text shape.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/sqfstar-manpage.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/unsquashfs-manpage.sh -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/unsquashfs-manpage.sh

Generates an `unsquashfs(1)` manpage from live `unsquashfs -help-all` and `-version` output using `help2man`.

Workflow:
- Must run from `generate-manpages`.
- Requires GNU sed and `help2man`.
- Validates executable `unsquashfs`.
- Captures help/version output to a temp directory.
- Creates a wrapper executable for `help2man`.
- Normalizes version/copyright/author.
- Edits help output into manpage-friendly formatting.
- Runs `help2man -Ni unsquashfs.h2m`.

Transformations:
- Converts `SYNTAX:` to `Usage:`.
- Inserts `*OPTIONS*`.
- Splits bracketed short/long option forms.
- Converts tabs to option/description spacing.
- Uppercases and removes operand angle brackets.
- Concatenates decompressor list, option text, exit-status text, `PAGER`, and `SQFS_CMDLINE`.
- Sectionizes Decompressors available, Exit status, See also, and Environment.
- Adds See Also references to `mksquashfs(1)`, `sqfstar(1)`, and `sqfscat(1)`.

Notable quirks:
- Temp cleanup is only on success.
- Formatting edits are tightly coupled to generated help text.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/unsquashfs-manpage.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/gzip_wrapper.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/gzip_wrapper.c

Implements gzip/zlib compressor support for the SquashFS compressor interface.

Supported options:
- `-Xcompression-level <1..9>`
- `-Xwindow-size <8..15>`
- `-Xstrategy <comma-separated strategies>`

Strategies:
- default
- filtered
- huffman_only
- run_length_encoded
- fixed

Behavior:
- Maintains process-global compressor option state.
- Suppresses stored compressor options when all gzip defaults are used, preserving legacy compatibility.
- Serializes non-default options into `struct gzip_comp_opts`.
- Extracts stored options for append mode, resetting to defaults when option size is zero.
- Displays stored compressor options.
- Initializes a zlib stream and, for data blocks with multiple strategies, tries each selected strategy and keeps the smallest result.
- Uses zlib `uncompress()` for decompression.

Key compressor vtable:
- `gzip_comp_ops` supports init, compress, uncompress, options, post-options, dump/extract/display options, usage, and option-arity detection.

Notable quirks:
- Error messages say ranges such as `1 >= n <= 9`, which is mathematically reversed wording but intended as `1 <= n <= 9`.
- Multiple strategy mode allocates extra temporary buffers for all but the first strategy.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/gzip_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/gzip_wrapper.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/gzip_wrapper.h

Data definitions for gzip compressor options and zlib strategy state.

Defines:
- Big-endian swap macro `SQUASHFS_INSWAP_COMP_OPTS`.
- Defaults: `GZIP_DEFAULT_COMPRESSION_LEVEL` and `GZIP_DEFAULT_WINDOW_SIZE`.
- `struct gzip_comp_opts` stored in SquashFS compressor options.
- `struct strategy` for option parsing.
- `struct gzip_strategy` for per-strategy compression attempts.
- `struct gzip_stream` containing a `z_stream` and flexible strategy array.

Key role: shared layout for gzip wrapper implementation and on-disk option serialization.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/gzip_wrapper.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/info.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/info.c

Implements signal-driven runtime diagnostics for `mksquashfs`.

Public functions:
- `disable_info()`
- `update_info(struct dir_ent *)`
- `init_info()`

Behavior:
- Tracks the current directory entry in a static `ent`.
- `print_filename()` prints the current file path via `progressbar_info()`.
- `dump_state()` disables the progress bar and prints queue/cache/thread status across the whole compression pipeline.
- `info_thrd()` waits for `SIGQUIT` and `SIGHUP`.
  - First `SIGQUIT` prints current filename and opens a short waiting window.
  - A second signal during that window, or SIGHUP, dumps full queue/cache/thread state.
- `init_info()` starts the info thread.

Dependencies:
- Uses global pipeline objects from other modules: queues, caches, reader state, and thread dump helpers.

Key role: operational introspection while long `mksquashfs` runs are active.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/info.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/info.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/info.h

Header for signal-driven mksquashfs diagnostics.

Exports:
- `disable_info()`
- `update_info(struct dir_ent *)`
- `init_info()`

Key role: lets scanning/build code update the currently processed entry and initialize diagnostic signal handling.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/info.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/limit.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/limit.c

Implements open-file limit detection.

Main function:
- `file_limit()`

Behavior:
- Caches the computed limit in static `max_files`.
- Calls `getrlimit(RLIMIT_NOFILE)`.
- If lookup fails, logs an error and returns 1.
- If finite, subtracts `OPEN_FILE_MARGIN` unless that would leave no usable files.
- If infinite, returns `-1`.

Key role: provides a conservative maximum number of files the tools should keep open concurrently.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/limit.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/limit.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/limit.h

Header for file-descriptor limit handling.

Defines:
- `OPEN_FILE_MARGIN 10`

Exports:
- `file_limit()`

Key role: centralizes the safety margin kept below `RLIMIT_NOFILE`.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/limit.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/lseek.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/lseek.h

Compatibility header for sparse-file seek support.

Behavior:
- Includes `<unistd.h>`.
- Defines `SEEK_DATA` as `3` if the platform C library does not define it.

Key role: allows code using `lseek(..., SEEK_DATA)` to compile against older libc headers.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/lseek.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/lz4_wrapper.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/lz4_wrapper.c

Implements LZ4 compressor support.

Supported options:
- `-Xhc`
- `-Xacceleration <1..65537>`
- `-Xcompression-level <1..12>` for high-compression mode

Behavior:
- Tracks global option state: high-compression flag, acceleration, compression level, and whether options were explicitly supplied.
- Rejects incompatible options in postprocessing: acceleration with high-compression, or compression-level without high-compression.
- Dumps versioned LZ4 option structures. LZ4 always writes an option structure to identify the legacy stream format.
- Supports v1 options for legacy/high-compression flag and v2 options for non-default acceleration/compression data.
- Extracts options for append mode and checks options for unsquashfs compatibility.
- Compresses with either normal LZ4 or LZ4 HC wrappers selected by library version macros.
- Decompresses with `LZ4_decompress_safe()`.

Compatibility:
- `OLD_LIBRARY_OPTION` and `OLD_LIBRARY_EXTRACT` reject non-default acceleration when linked against older LZ4 APIs.

Notable quirks:
- Extraction paths do not explicitly clear all previous global option flags in every branch, so correctness assumes append/extract state is not contaminated by earlier option parsing.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/lz4_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/lz4_wrapper.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/lz4_wrapper.h

Data definitions and compatibility macros for LZ4 compressor support.

Defines:
- Big-endian swap macros for v1 and v2 option structs.
- Stream format `LZ4_LEGACY`.
- Flags `LZ4_HC`, `LZ4_NON_DEFAULT`, `LZ4_FLAGS_MASK`.
- Default acceleration `LZ4_ACC_DEFAULT`.
- `struct lz4_comp_opts_v1` and `struct lz4_comp_opts_v2`.

Library-version compatibility:
- For `LZ4_VERSION_NUMBER >= 10700`, uses `LZ4_compress_fast()` and `LZ4_compress_HC()`, default HC level 12.
- For older libraries, uses older limited-output APIs, default HC level 9, and defines runtime guards for unsupported acceleration.

Notable typo:
- Comment says “omly legacy stream format”.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/lz4_wrapper.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/lzma_wrapper.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/lzma_wrapper.c

Implements obsolete LZMA1 compressor support using the LZMA SDK.

Behavior:
- Compresses with `LzmaCompress()` into an LZMA-alone style header plus payload.
- Writes an 8-byte little-endian uncompressed-size field after the LZMA properties.
- Treats `SZ_ERROR_OUTPUT_EOF` as output-buffer overflow and returns 0.
- Decompresses by reading the size from the LZMA header, validating it fits the requested output size, then calling `LzmaUncompress()`.
- Exposes no compressor options.
- Usage text marks it deprecated and notes no kernel support.

Key role: optional legacy compressor wrapper retained for compatibility.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/lzma_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/lzma_xz_wrapper.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/lzma_xz_wrapper.c

Alternative obsolete LZMA1 wrapper implemented with XZ Utils liblzma.

Behavior:
- Uses `lzma_alone_encoder()` with preset 5 and dictionary size equal to SquashFS block size.
- Rewrites the 8-byte uncompressed-size field in the LZMA-alone header.
- Uses `lzma_alone_decoder()` with a 32 MiB memory limit.
- During decompression, copies the input header, reads the expected uncompressed size, replaces the size field with unknown-size bytes, then decodes.
- Accepts stream-end success, and also accepts a case where `LZMA_OK` produced enough output and consumed input.
- Exposes no compressor options.
- Usage text marks it deprecated and notes no kernel support.

Key role: optional legacy LZMA1 support without requiring the standalone LZMA SDK.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/lzma_xz_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/lzo_wrapper.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/lzo_wrapper.c

Implements LZO compressor support.

Supported options:
- `-Xalgorithm <algorithm>`
- `-Xcompression-level <1..9>` for `lzo1x_999`

Algorithms:
- `lzo1x_1`
- `lzo1x_1_11`
- `lzo1x_1_12`
- `lzo1x_1_15`
- `lzo1x_999`

Behavior:
- Default algorithm is `lzo1x_999`; default compression level is 8.
- Postprocessing ensures compression level is used only with `lzo1x_999`.
- Suppresses stored compressor options when defaults match legacy behavior.
- Serializes non-default algorithm/level into `struct lzo_comp_opts`.
- Extracts stored options for append mode and validates algorithm/level combinations.
- Allocates LZO workspace and an expansion-sized temporary buffer in `squashfs_lzo_init()`.
- Compresses into the temporary buffer because LZO’s API does not take an output-size limit, checks against block size, optimizes, then copies to destination.
- Decompresses with `lzo1x_decompress_safe()`.

Key compressor vtable:
- `lzo_comp_ops` supports init, compress, uncompress, options, post-options, dump/extract/display options, usage, and option-arity detection.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/lzo_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/lzo_wrapper.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/lzo_wrapper.h

Data definitions for LZO compressor support.

Defines:
- Big-endian swap macro for LZO compressor options.
- Algorithm IDs matching the `lzo[]` table order.
- Default compression level for `SQUASHFS_LZO1X_999`.
- `struct lzo_comp_opts` on-disk option layout.
- `struct lzo_algorithm` lookup entries.
- `struct lzo_stream` workspace/temp-buffer holder.
- `LZO_MAX_EXPANSION(size)` for safe temporary compression output sizing.
- Prototype for `lzo1x_999_wrapper()`.

Key role: connects LZO library APIs, option serialization, and SquashFS compressor vtable implementation.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/lzo_wrapper.h -->