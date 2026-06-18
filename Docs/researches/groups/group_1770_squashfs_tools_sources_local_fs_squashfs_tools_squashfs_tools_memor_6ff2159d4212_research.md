# Group Research: group_1770_squashfs_tools_sources_local_fs_squashfs_tools_squashfs_tools_memor_6ff2159d4212

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/squashfs-tools`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/memory.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/memory.c

Implements the memory-limit validation entry point for mksquashfs-style tools.

Key function:
- `check_usable_phys_mem(int total_mem, char *name)` obtains physical memory in MiB through `get_physical_memory()`, rejects unknown physical memory, limits requested cache memory to 75% of physical memory, and additionally rejects requests over 2048 MiB for 32-bit processes.

Dependencies:
- Uses `memory_compat.h` for platform physical-memory probing.
- Uses `error.h` macros for diagnostics.
- Returns local `TRUE`/`FALSE` values from `memory.h`.

Important behavior:
- The function treats `total_mem` as MiB.
- The 75% cap is an operational safety limit to avoid thrashing and denial-of-service behavior.
- The 32-bit check is conservative because a PAE or 64-bit kernel can expose more physical memory than a 32-bit process can address.

Risks and notes:
- `get_physical_memory()` returns `int`; very large systems can be truncated after the MiB conversion if the value exceeds `INT_MAX`.
- This file only validates requested memory. Actual cache sizing and minimum-memory checks happen elsewhere, notably `reader.c`.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/memory.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/memory.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/memory.h

Small public header for memory validation.

Exports:
- `check_usable_phys_mem(int total_mem, char *name)`

Local constants:
- `TRUE` as `1`
- `FALSE` as `0`

Role:
- Lets command-line memory option handling call the shared validator implemented in `memory.c`.

Notes:
- The header does not include dependencies and assumes callers already have any needed declarations for their own use.
- `TRUE`/`FALSE` are repeatedly defined in this codebase, so include order should avoid conflicting semantic definitions.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/memory.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/memory_compat.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/memory_compat.h

Platform compatibility header for querying physical memory.

Exports:
- `static inline int get_physical_memory()`

Linux behavior:
- Includes `<sys/sysinfo.h>`.
- First tries `sysconf(_SC_PHYS_PAGES)` and `sysconf(_SC_PAGESIZE)`.
- Falls back to `sysinfo()` if either `sysconf()` call fails.
- Returns memory in MiB.

Non-Linux behavior:
- Uses `sysconf(_SC_PHYS_PAGES)` and `sysconf(_SC_PAGESIZE)`.
- Returns `0` on failure, otherwise physical memory in MiB.

Important behavior:
- Uses `long long` internally to support 32-bit systems with more than 4 GiB physical memory.
- Linux fallback avoids reliance on `/proc` being mounted when `sysconf(_SC_PHYS_PAGES)` fails.

Risks and notes:
- Return type is `int`, so the final MiB count can overflow on extremely large systems.
- The header depends on callers having included `<unistd.h>` for `sysconf()` in non-Linux builds; `memory.c` does include it before this header.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/memory_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/merge_sort.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/merge_sort.h

Defines a macro-generated bottom-up merge sort for linked lists.

Primary macro:
- `SORT(FUNCTION_NAME, LIST_TYPE, NAME, NEXT)` emits a function that sorts `struct LIST_TYPE` linked through field `NEXT`, comparing string field `NAME` with `strcmp()`.

Algorithm:
- Iterative bottom-up merge sort.
- Starts with stride `1`, merges adjacent sorted sublists, then doubles stride until it reaches the input count.
- Sorts in place by relinking list nodes.
- Requires no auxiliary array or recursion.

Important behavior:
- Uses `strcmp(l1->NAME, l2->NAME) <= 0`, so equal keys keep the left-list item first during merge, preserving stable order across equal names.
- Caller must provide an accurate `count`; the loop termination depends on it.
- Handles `NULL` head and counts below 2 as no-ops.

Risks and notes:
- Macro assumes `strcmp()` is visible in the including translation unit.
- Missized `count` can leave the list partially sorted or make the merge loop operate beyond intended logical bounds.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/merge_sort.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs.h

Central shared header for mksquashfs build state, directory/inode metadata, fragment tracking, and cross-module globals.

Major data structures:
- `struct dir_info`: in-memory directory scan state, including source/output pathnames, directory entry list, depth, exclusion state, and `DIR *`.
- `struct dir_ent`: directory entry node linking name/source name, inode, child directory, owning directory, and reader traversal link.
- `struct inode_info`: cached inode/stat metadata plus pseudo-file state, xattrs, symlink or cloned directory info, Squashfs inode number, flags controlling compression/fragments/tar/read/scanned behavior, and dereference state.
- `struct file_info`: in-memory written-file state including size, bytes, start offset, sparse bytes, block list, fragment linkage, duplicate linkage, checksums, and flags.
- `struct dup_info`, `struct fragment`, `struct id`, `struct append_file`, `struct directory`, `struct exclude_info`, `struct pathname`, `struct pathnames`, and `struct old_root_entry_info`.

Important constants:
- Queue/cache memory ratios: `SQUASHFS_TAKE`, `SQUASHFS_READQ_MEM`, `SQUASHFS_BWRITEQ_MEM`, `SQUASHFS_FWRITEQ_MEM`.
- Fallback memory: `SQUASHFS_UNKNOWN_MEM`.
- Metadata `BLOCK_OFFSET`.
- Hash and directory sizing constants: `ID_ENTRIES`, `INODE_HASH_SIZE`, `DIR_ENTRIES`, `I_COUNT_SIZE`.
- `MAXIMUM_READ_SIZE` for Linux `read()` transfer cap.
- Symlink dereference states: `DEREF_FIRST`, `DEREF_MULTIPLE`, `DEREF_BAD`.

Inline helper:
- `get_pathmax()` chooses `PATH_MAX`, falls back to `pathconf(".", _PC_PATH_MAX)` or `4096`, and caps at 65536.

Cross-module globals:
- Declares caches, queues, compressor pointer, fragment table, inode hash, option flags, root metadata overrides, UID/GID state, pseudo override flag, and tar/global mode state.

Cross-module functions:
- Declares core hooks for reading/writing bytes, adding appended files, ID creation, inode creation, scanning directories, writing files, excluding paths, creating/freeing directory structures, lookup helpers, and parsing date expressions.

Role:
- This is the main coupling point for the mksquashfs pipeline. Reader, sorter, pseudo handling, append-import code, and writer-side code all exchange state through these structs and externs.

Risks and notes:
- Broad extern surface makes module boundaries loose.
- Many fields are single-byte flags; changes need care because behavior is distributed across reader, scanner, writer, pseudo, and append paths.
- `struct inode_info` uses unions whose active member depends on flags and file type.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_error.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_error.h

Defines mksquashfs-specific reporting and exit macros layered on top of `error.h`.

Externs:
- `exit_on_error`
- `prep_exit()`
- `display_info`
- `info_file`

Macros:
- `INFO(s, args...)`: emits informational file-output messages when `display_info` is set, either to `info_file` or through `progressbar_info()`.
- `ERROR_START(s, args...)`: disables the progress bar and starts an error message on stderr.
- `ERROR_EXIT(s, args...)`: if `exit_on_error` is set, prints a newline and exits through `EXIT_MKSQUASHFS()`. Otherwise prints the supplied suffix and re-enables the progress bar.
- `EXIT_MKSQUASHFS()`: calls `prep_exit()` then exits with status `1`.

Role:
- Supports errors that can be warnings by default but fatal under `-exit-on-error`.
- Keeps progress-bar output from corrupting diagnostics.

Risks and notes:
- Depends on `progressbar_info()`, `disable_progress_bar()`, and `enable_progress_bar()` being visible through included headers or prior declarations in consumers.
- Uses GNU variadic macro syntax `args...`, so it is not strictly ISO C.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_error.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_help.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_help.c

Implements help, option-help, section-help, and compressor-help output for `mksquashfs` and `sqfstar`.

Static metadata:
- `mksquashfs_options`, `sqfstar_options`: option names aligned to help text.
- `mksquashfs_args`, `sqfstar_args`: argument placeholders aligned with option arrays.
- `mksquashfs_sections`, `sqfstar_sections`: section names used by `-help-section`.
- `mksquashfs_text`, `sqfstar_text`: complete help content for both programs, including compression, build, time, permissions, pseudo, filters, xattrs, runtime, append/actions/tar/expert/help/misc, pseudo-definition formats, symbolic mode syntax, environment variables, exit status, and documentation links.

Core functions:
- `print_help_all()`: prints syntax, all help text, compressor usage, then exits `0`.
- `print_option()`: compiles a POSIX extended regex, matches it against option names and option argument placeholders, prints matching help text, and exits success or failure.
- `is_header()`: identifies section headers by trailing colon.
- `print_section_names()`: prints section-name mapping.
- `print_section()`: supports exact section name, `list`, or regex-matched section output.
- `handle_invalid_option()`: prints invalid-option guidance plus available help sections.
- `print_help()`: prints summary help and exits `0` or `1` depending on whether an error message was supplied.
- `print_option_help()`: prints a specific parser error and suggests option/section help.

Public wrappers:
- `mksquashfs_help_all()`, `sqfstar_help_all()`
- `mksquashfs_option()`, `sqfstar_option()`
- `mksquashfs_section()`, `sqfstar_section()`
- `mksquashfs_help()`, `sqfstar_help()`
- `mksquashfs_invalid_option()`, `sqfstar_invalid_option()`
- `mksquashfs_option_help()`, `sqfstar_option_help()`
- `display_compressors()`
- `print_compressor_options()`

Dependencies:
- Uses `print_pager.c` APIs for pager launch and wrapping.
- Uses compressor APIs and macros from `compressor.h`.
- Uses allocation wrappers from `alloc.h`.

Important behavior:
- All help entry points exit the process after printing.
- Regex errors are reported with `regerror()`.
- Compressor option help accepts `ALL` and `<all>` aliases by normalizing to `all`.
- Unsupported compressor help prints available compressors and exits `1`.

Risks and notes:
- The option, args, and text arrays are positionally coupled; edits must preserve alignment.
- Section traversal depends on identifying headers by `:` at end of text entries.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_help.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_help.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_help.h

Public help-system header for `mksquashfs` and `sqfstar`.

Compile-time strings:
- Defines `NOXOPT_STR` and `XOPT_STR` based on `XATTR_SUPPORT`, `XATTR_OS_SUPPORT`, and `XATTR_DEFAULT`.
- Defines reader-thread default strings based on `SINGLE_READER_THREAD`, `SMALL_READER_THREADS`, and `BLOCK_READER_THREADS`.

Exports:
- Full help, option help, section help, invalid-option help, and general help functions for both `mksquashfs` and `sqfstar`.
- `display_compressors()`
- `print_compressor_options(char *comp_name, char *prog_name)`

Role:
- Gives command-line parsing code a stable interface to the pager-aware help implementation.
- Encodes build-configuration-dependent annotations in help output.

Risks and notes:
- Relies on compile-time compressor/thread macros from the broader build.
- Defines `TRUE`/`FALSE` locally like several other headers in this tree.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_help.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_xattr.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_xattr.h

Conditional header for reading xattrs from the host filesystem during mksquashfs builds.

Behavior:
- When `XATTR_SUPPORT` and `XATTR_OS_SUPPORT` are both defined, declares:
  - `read_xattrs_from_system(struct dir_ent *dir_ent, char *filename, struct xattr_list **xattrs)`
- When xattr support is compiled but OS xattr support is absent, provides a static inline stub returning `0`.

Role:
- Lets callers compile xattr-aware code paths even on platforms without OS-level xattr read support.

Notes:
- The comment says `unsquashfs_xattr.h`, but the file is `mksquashfs_xattr.h`.
- No declarations are emitted if `XATTR_SUPPORT` is not defined.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/nprocessors_compat.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/nprocessors_compat.c

Platform compatibility implementation for counting available processors.

State:
- Static cached `processors`, initialized to `-1`.

Linux behavior:
- Uses `sched_getaffinity(0, sizeof cpu_set, &cpu_set)` and `CPU_COUNT()` to respect CPU affinity.
- Falls back to `sysconf(_SC_NPROCESSORS_ONLN)` if affinity lookup fails.

Non-Linux behavior:
- Uses `sysctl()` with `CTL_HW` and either `HW_AVAILCPU` or `HW_NCPU`.
- On failure, reports an error and defaults to `1`.

Public function:
- `get_nprocessors(void)`

Important behavior:
- The result is cached after the first call.
- Linux path can return `sysconf()` result directly into `processors`; if `sysconf()` fails, this can cache `-1`.

Risks and notes:
- Non-Linux path is BSD/macOS oriented through `sysctl`.
- Linux fallback does not clamp failure to `1`, unlike the non-Linux path.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/nprocessors_compat.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/nprocessors_compat.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/nprocessors_compat.h

Small public header for processor-count compatibility support.

Exports:
- `get_nprocessors(void)`

Role:
- Allows option/default sizing code to query the effective processor count without caring about the platform-specific implementation.

Notes:
- Implementation caches the result in `nprocessors_compat.c`.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/nprocessors_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/print_pager.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/print_pager.c

Implements pager selection, safe parsing of `PAGER`, terminal width detection, and autowrapped text output.

State:
- `pager_argv`, `pager_command`, `pager_from_env_var`
- Public globals `no_pager` and `user_cols`

Argument parsing:
- `next_arg_count()`, `next_arg_copy()`, and `next_arg()` parse shell-like whitespace, quotes, and backslash handling without invoking a shell.
- Rejects common shell metacharacters `|`, `;`, `<`, `>`, `&` unless quoted/backslashed as literal pager arguments.
- `check_and_set_pager()` splits and validates a user/environment pager string, finds a usable basename, and disables pager if the string is empty.

Pager execution:
- `determine_pager()` forks a child, runs `--version`, and classifies `less`, `more`/`pager`, or unknown.
- `run_cmd()` chooses pager-specific flags: `less --quit-if-one-screen`, `more/pager --exit-on-eof`, or no flags.
- `exec_pager()` builds a pipe to the pager process, falling back through configured pager, `pager`, `less`, `more`, `cat`, then internal `simple_cat()`.
- `launch_pager()` uses a pager only when stdout is a terminal and `no_pager` is false.
- `delete_pager()` closes the stream and waits for the pager child.

Formatting:
- `get_column_width()` returns `user_cols`, terminal width via `TIOCGWINSZ`, or `80`.
- `autowrap_print()` wraps text by terminal width, preserving tabs and avoiding mid-word breaks where possible.
- `autowrap_printf()` formats with `VASPRINTF()` and wraps.

Risks and notes:
- `determine_pager()` has a likely typo: it checks `if(res == 1024)` after `read_bytes()` into `bytes`; intended check may be `bytes == 1024`.
- The parser is deliberately not a shell. Complex shell pipelines in `PAGER` are rejected rather than executed.
- Pager child execution uses fork/exec and avoids `system()`.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/print_pager.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/print_pager.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/print_pager.h

Public interface for pager-backed help output.

Constants:
- `TRUE`, `FALSE`
- Pager classification values: `LESS_PAGER`, `MORE_PAGER`, `UNKNOWN_PAGER`

Exports:
- Public globals `no_pager`, `user_cols`
- `launch_pager(pid_t *process, int *cols)`
- `delete_pager(FILE *pager, pid_t process)`
- `get_column_width()`
- `autowrap_print(FILE *stream, char *text, int maxl)`
- `autowrap_printf(FILE *stream, int maxl, char *fmt, ...)` with printf-format attribute
- `check_and_set_pager(char *pager)`

Role:
- Used by help and compressor-option display code to produce terminal-aware text output.

Notes:
- Includes `<stdio.h>` and `<sys/types.h>` for `FILE` and `pid_t`.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/print_pager.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/process_fragments.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/process_fragments.c

Worker-thread implementation for processing file fragments before main-thread write handling.

Core functions:
- `checksum_sparse(struct file_buffer *file_buffer)`: computes a 16-bit BSD-style checksum over fragment data and detects all-zero sparse fragments.
- `read_filesystem(int fd, long long byte, int bytes, void *buff)`: seeks and reads from the destination filesystem, offset by global `start_offset`.
- `get_fragment(struct fragment *fragment, char *data_buffer, int fd)`: retrieves and decompresses an existing fragment block from caches, writer cache, reserve cache, or disk.
- `get_fragment_cksum(struct file_info *file, char *data_buffer, int fd, unsigned short *checksum)`: reads a fragment block and computes checksums for appended files mapped to that fragment.
- `frag_thrd(void *destination_file)`: main worker loop consuming `to_process_frag`, detecting sparse fragments, doing fragment duplicate checking, and forwarding buffers to `to_main`.

Concurrency and caches:
- Uses `dup_mutex` around duplicate state and fragment-cache lookup/fill coordination.
- Uses `fragment_mutex` when reading fragment-table entries.
- Uses `fragment_buffer`, `reserve_cache`, and `fwriter_buffer`.
- Handles locked cache buffers with `cache_wait_unlock()`.

Pipeline role:
- Receives candidate fragment buffers from readers.
- Marks sparse data when enabled.
- Speculatively loads old/appended fragment blocks for duplicate comparison.
- Replaces duplicate fragment buffers with a lightweight duplicate descriptor when content matches.

Risks and notes:
- `frag_thrd()` is an infinite loop designed for cancellation.
- Duplicate checking opens the destination filesystem for reading and allocates a max-size fragment buffer.
- Correctness depends on `file_mapping`, fragment table, and writer caches being coherent during append mode.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/process_fragments.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/process_fragments.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/process_fragments.h

Public header for fragment processing.

Exports:
- `frag_thrd(void *)`

Role:
- Lets the main mksquashfs thread create fragment-processing worker threads.

Notes:
- The worker expects global queues/caches and destination-file context to have been initialized elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/process_fragments.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/progressbar.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/progressbar.c

Implements progress display, percentage output, and progress-safe info/error printing.

State:
- `display_progress_bar`, `temp_disabled`, `percent`, `need_nl`
- Spinner state `rotate`
- Counters `cur_uncompressed`, `estimated_uncompressed`
- Metadata progress interpolation values `inc`, `base`
- Worker thread `progress_thread`
- Mutexes `progress_mutex` and `size_mutex`

Public controls:
- `progressbar_percentage()`
- `inc_progress_bar()`, `dec_progress_bar(int)`
- `progress_bar_size(int)`
- `progress_bar_metadata(int)`, `inc_meta_progress_bar()`
- `enable_progress_bar()`, `disable_progress_bar()`
- `set_progressbar_state(int)`
- `progressbar_finish()`
- `init_progress_bar()`
- `progressbar_error(char *fmt, ...)`
- `progressbar_info(char *fmt, ...)`

Rendering:
- `progressbar()` renders `[====|    ] current/max percent`, with spinner rotation.
- `display_percentage()` prints integer percentages on separate lines for gauge-style consumers.
- `progress_bar()` switches between full bar and percentage mode.

Threading:
- `progress_thrd()` wakes every 250 ms, rotates the spinner, and redraws when enabled.
- `SIGWINCH` handler updates column width.

Important behavior:
- Non-tty output is rate-limited to every 100 units or final completion to avoid huge logs.
- Error/info printing inserts a newline if progress output is currently occupying the line.

Risks and notes:
- `inc_progress_bar()` and `dec_progress_bar()` modify `cur_uncompressed` without a mutex, while rendering reads under `progress_mutex`.
- The progress thread runs forever and is expected to end with process termination.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/progressbar.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/progressbar.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/progressbar.h

Public header for progress bar management.

Exports:
- Progress counter updates: `inc_progress_bar()`, `dec_progress_bar(int)`, `progress_bar_size(int)`
- State controls: `enable_progress_bar()`, `disable_progress_bar()`, `set_progressbar_state(int)`, `progressbar_finish()`
- Initialization: `init_progress_bar()`
- Mode selection: `progressbar_percentage()`
- Metadata progress: `progress_bar_metadata(int)`, `inc_meta_progress_bar()`

Role:
- Allows reader, writer, metadata, and error paths to coordinate progress output.

Notes:
- Does not expose `progressbar_error()` or `progressbar_info()`, though those are used indirectly through error/info macros in this tree.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/progressbar.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/pseudo.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/pseudo.c

Implements pseudo-file definition parsing and the in-memory pseudo-tree used to inject or modify filesystem entries.

Global state:
- `struct pseudo *pseudo`
- Static mutex around dynamic pseudo-file process execution.
- `pseudo_definitions[]` lists supported syntax variants.

Tree helpers:
- `get_element()` splits a path component and returns the remaining path.
- `pseudo_search()` finds or inserts a sorted `pseudo_entry`.
- `add_pseudo()` recursively inserts a pseudo device/file definition.
- `add_pseudo_definition()` handles root special cases and delegates to `add_pseudo()`.
- `pseudo_subdir()` and `pseudo_readdir()` expose directory-style traversal.
- `pseudo_lookup()` recursively finds an existing pseudo entry.

Dynamic/process pseudo files:
- `pseudo_exec_file()` forks `/bin/sh -c <command>`, pipes child stdout back to the reader, and returns the read fd.

Definition parsing:
- Original lowercase definitions: `b`, `c`, `d`, `f`, `i`, `m`, `s`.
- Extended uppercase definitions: `B`, `C`, `D`, `F`, `I`, `M`, `R`, `S`.
- `read_pseudo_def_original()` parses mode/uid/gid plus type-specific fields.
- `read_pseudo_def_extended()` additionally parses mtime, supports data-backed `R` entries from pseudo files, and sets `force_single_threaded` for embedded data reads.
- `read_pseudo_def_link()` supports hardlinks to real files, with optional symlink following for `h`, and prevents linking to the destination output file.
- `read_pseudo_def_pseudo_link()` supports `L` links to previously defined pseudo files.
- `read_pseudo_def()` parses the filename and dispatches to xattr, link, original, or extended parser.

File-level parsing:
- `read_pseudo_definition()` parses one command-line pseudo definition.
- `read_pseudo_file()` reads a pseudo-definition file, supports comments, whitespace, line continuation with backslash, stdin via `-`, and an embedded data marker `# START OF DATA - DO NOT MODIFY`.
- `read_pseudo_dir()` parses default pseudo-directory definitions for `-pd`.

Validation:
- Checks major/minor device bounds.
- Checks mode range.
- Resolves numeric or name-based uid/gid through passwd/group databases.
- Checks symlink length.
- Rejects duplicate conflicting pseudo definitions.

Debug support:
- `dump_pseudos()` recursively dumps pseudo entries only under `SQUASHFS_TRACE`; otherwise it is a no-op.

Risks and notes:
- Dynamic pseudo files intentionally execute shell commands.
- `struct pseudo_dev` uses unions; consumers must interpret by `type` and `pseudo_type`.
- Pseudo definitions are order-sensitive for pseudo links: `L` needs the target pseudo definition to already exist.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/pseudo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/pseudo.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/pseudo.h

Public data model and interface for pseudo-file support.

Constants:
- `PSEUDO_FILE_OTHER`
- `PSEUDO_FILE_PROCESS`
- `PSEUDO_FILE_DATA`

Macros:
- `IS_PSEUDO(a)`
- `IS_PSEUDO_PROCESS(a)`
- `IS_PSEUDO_OTHER(a)`
- `IS_PSEUDO_DATA(a)`

Structures:
- `pseudo_stat`: synthetic mode, uid, gid, major/minor, mtime, and pseudo inode.
- `pseudo_file`: backing pseudo data file state.
- `pseudo_data`: offset/length/sparse descriptor for embedded data-backed pseudo files.
- `pseudo_dev`: one pseudo item, holding stat/link metadata and command/symlink/link/data payloads.
- `pseudo_entry`: tree entry with name, pathname, child pseudo tree, device definition, xattrs, and next link.
- `pseudo`: pseudo directory containing sorted entries and read cursor.
- `pseudo_xattr`: list/count wrapper for pseudo xattr additions.

Exports:
- Global `pseudo`.
- Parsing and traversal functions including `read_pseudo_definition()`, `read_pseudo_file()`, `read_pseudo_dir()`, `pseudo_subdir()`, `pseudo_readdir()`, `pseudo_search()`, `get_element()`, `get_pseudo_file()`, `pseudo_exec_file()`, `get_pseudo()`, and `dump_pseudos()`.

Role:
- Shared by scanner, reader, pseudo-xattr code, and directory-building logic.

Notes:
- `get_pseudo_file(int)` is declared here but not implemented in `pseudo.c`; it is presumably provided elsewhere in the source tree.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/pseudo.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/pseudo_xattr.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/pseudo_xattr.c

Adds pseudo extended-attribute definitions into the pseudo tree.

Core helpers:
- `add_xattr(struct pseudo_xattr **xattr, struct xattr_add *entry)`: creates or prepends to a pseudo xattr list and updates count.
- `add_pseudo_xattr(struct pseudo *pseudo, struct xattr_add *xattr, char *target, char *alltarget)`: recursively walks/creates pseudo tree entries and attaches xattr definitions at the leaf.
- `add_pseudo_xattr_definition(struct pseudo *pseudo, struct xattr_add *xattr, char *target, char *alltarget)`: handles root pseudo definition special cases, then delegates.

Parser:
- `read_pseudo_xattr(char *def)` delegates parsing to `xattr_parse(def, "", "pseudo xattr")`.

Behavior:
- Can attach xattrs to existing or newly created pseudo entries.
- Handles `/` specially by wrapping the existing pseudo tree under a root entry when necessary.

Dependencies:
- Uses `pseudo_search()` and `get_element()` from `pseudo.c`.
- Uses `xattr_parse()` and `struct xattr_add` from xattr support.

Risks and notes:
- Like pseudo file entries, xattr insertion mutates the shared pseudo tree and relies on caller ordering.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/pseudo_xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/read_fs.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/read_fs.c

Implements reading an existing Squashfs filesystem for append/import workflows.

Core metadata reader:
- `read_block()` reads a compressed metadata block header, validates compressed size, decompresses when needed, updates next-block offset, and checks expected uncompressed size when supplied.

Inode scanning:
- `scan_inode_table()` reads and decompresses the inode table, locates the root inode block, validates inode boundaries, walks every inode before root, counts file/symlink/device/directory/fifo/socket inodes, accumulates uncompressed file/directory sizes, validates uid/gid indexes, maps appended file data through `add_file()`, and initializes fragment-to-file mapping.
- Handles regular, large regular, symlink, long symlink, directory, long directory, block/char device, fifo, and socket inode variants.
- Performs bounds checks before reading each inode-specific structure and variable-length tail.

Superblock:
- `read_super()` reads and swaps the superblock, checks magic and Squashfs version, validates compressor support, reads compressor options if present, applies compressor options, and prints summary information unless quiet.

Directory and tables:
- `squashfs_readdir()` reads directory metadata blocks, pushes root directory entries through a callback, validates directory counts and filename sizes, and returns uncompressed directory table bytes.
- `read_id_table()` reads id table indexes and metadata, swaps ids, and registers ids through `create_id()`.
- `read_fragment_table()` reads and swaps fragment table indexes and entries.
- `read_inode_lookup_table()` reads and swaps inode lookup entries.

Top-level API:
- `read_filesystem()` coordinates xattr loading, fragment table, inode lookup table, id table, inode table scan, root directory replay, and construction of compressed/uncompressed inode and directory caches needed for appending.

Dependencies:
- Compressor API, Squashfs swap macros, xattr loader, virtual disk position tracking, mksquashfs globals, and allocation wrappers.

Important behavior:
- Existing filesystem append support is strict about corrupted metadata and table sizes.
- Uses `get_xattrs()` before table scanning.
- Returns `0` on failure, otherwise the original inode table start offset.

Risks and notes:
- Uses stack VLAs for some metadata index arrays and compressed block buffers.
- Many output values are passed through pointer parameters; callers must provide initialized storage and handle partial allocations on failure paths.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/read_fs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/read_fs.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/read_fs.h

Public header for reading existing Squashfs filesystems.

Exports:
- `read_super(int, struct squashfs_super_block *, char *)`
- `read_filesystem(...)` with a large parameter list returning existing filesystem metadata, counts, table caches, fragment table, inode lookup table, and root directory entries via callback.

Role:
- Used by append-mode code to validate and import an existing Squashfs filesystem.

Notes:
- The `read_filesystem()` signature is highly coupled to mksquashfs append internals.
- Types such as `struct compressor`, `struct squashfs_super_block`, `struct squashfs_fragment_entry`, and `squashfs_inode` must be visible to including code.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/read_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/read_xattrs.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/read_xattrs.c

Common xattr read code shared by mksquashfs and unsquashfs.

State:
- Hash table mapping compressed xattr metadata block disk starts to uncompressed in-memory offsets.
- `xattr_table_length`
- `xattr_ids`
- `xattrs`
- `xattr_table_start`

Prefix table:
- Maps Squashfs xattr prefix IDs to strings: `user.`, `trusted.`, `security.`.

Helpers:
- `save_xattr_block()` stores compressed-block-start to memory-offset mapping.
- `get_xattr_block()` resolves that mapping.
- `read_xattr_entry()` constructs `struct xattr_list` names from prefix plus on-disk name.

Main reader:
- `read_xattrs_from_disk(int fd, struct squashfs_super_block *sBlk, int sanity_only, long long *table_start)` reads the xattr table descriptor, validates id/index sizes, optionally returns only sanity/table-start info, reads and decompresses xattr id table blocks, reads and decompresses xattr metadata blocks, records block mappings, swaps xattr IDs, and returns the xattr id count.

Public cleanup:
- `free_xattr(struct xattr_list *xattr_list, int count)`

Lookup:
- `get_xattr(int i, unsigned int *count, int *failed)` builds a list of xattr name/value pairs for an xattr id, supports out-of-line values, and flags unknown prefixes through `failed`.

Important behavior:
- Unknown xattr prefixes are not always fatal at lookup time. The caller can distinguish partial success with `failed`.
- Extensive bounds checks prevent reading beyond the decompressed xattr metadata area.
- `sanity_only` allows append sanity checks without extracting all xattrs.

Risks and notes:
- Static global storage makes this a process-wide xattr cache.
- Out-of-line value lookup assumes `get_xattr_block(start)` succeeds; corrupted metadata checks cover offset bounds after mapping.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/read_xattrs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/reader.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/reader.c

Implements source-file reading and reader-thread scheduling for mksquashfs.

Configuration/state:
- Reader arrays, reader threads, reader buffers, readahead table for stdin-backed pseudo data, and counters for file/block/fragment entries.
- Reader modes differ by build:
  - With `SINGLE_READER_THREAD`, defaults to one reader unless both small and block reader options are specified.
  - Otherwise defaults to configured `SMALL_READER_THREADS` and `BLOCK_READER_THREADS`.

Reader classification:
- `is_fragment()` decides whether file tail data should become a fragment, considering fragment options, compression flags, alignment, file size, and always-use-fragments.
- `is_large()` checks file size against block size.
- `add_entry()` routes regular/pseudo-data/process/large entries into block or fragment arrays.

Buffer flow:
- `get_buffer()` initializes a `file_buffer` from a reader cache.
- `put_file_buffer()` sends buffers to `to_main`, `to_process_frag`, or `to_deflate` based on sparse/error/empty/fragment/compressible state.

File readers:
- `reader_read_process()` executes dynamic pseudo-file commands, reads stdout into blocks, updates progress size as blocks arrive, waits for child exit, and marks final fragment state.
- `reader_read_file()` opens regular files, reads blocks, handles sparse files using `SEEK_DATA`, detects file-size changes by reading past expected EOF and restatting, versions changed reads up to 1023 retries, and emits buffers with `NEXT_BLOCK`, `NEXT_FILE`, or `NEXT_VERSION`.
- `reader_read_data()` reads embedded pseudo-file data by offset and length, using readahead buffering when the pseudo data source is stdin.

Pseudo-data readahead:
- `get_readahead()`, `do_readahead()`, and `read_data()` support out-of-order reads from stdin-backed pseudo data by buffering skipped ranges in 8192-byte chunks.

Threading:
- `reader_scan()` recursively collects files from the directory tree.
- `create_resources()` sizes queue/cache resources and initializes readers.
- `block_reader()` and `fragment_reader()` atomically claim entries from arrays.
- `multi_thread()` builds entry arrays, clamps thread counts to work counts, creates fragment and block reader threads.
- `single_reader_scan()` and `single_thread()` perform sequential traversal/read.
- `initial_reader()` consumes the root directory from `to_reader`, sets up throttling if requested, handles tar input specially, and chooses threaded or single-threaded reading.

Public controls:
- `readers_sane()`
- `get_readers()`, `get_reader_threads()`
- `set_read_frag_threads()`, `set_read_block_threads()`, `set_single_threaded()`
- `get_reader_num()`
- `set_sleep_time()`
- `check_min_memory()`

Memory validation:
- `check_min_memory()` calculates reader/writer block availability from MiB budgets and block size, reports actionable option changes, and calls `BAD_ERROR()` if insufficient.

Risks and notes:
- Reader pipeline correctness depends on global queues and cache sizing established elsewhere.
- File mutation while reading is handled by retry/version logic, but repeated mutation eventually becomes an error.
- Stdin pseudo-data out-of-order reads can grow the readahead table.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/reader.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/reader.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/reader.h

Public interface and structs for source reader threads.

Constants:
- Readahead: `READAHEAD_SIZE`, `READAHEAD_ALLOC`, `READAHEAD_INDEX()`, `READAHEAD_OFFSET()`
- Reader types: `COMBINED_READER`, `FRAGMENT_READER`, `BLOCK_READER`
- Minimum per-reader blocks: `BLOCKS_MIN`

Conditional behavior:
- Under `SINGLE_READER_THREAD`, declares runtime `readers_sane()`.
- Otherwise provides inline `readers_sane()` returning `TRUE`.

Structures:
- `readahead`: buffered pseudo-data range with source pointer and flexible data payload.
- `read_entry`: directory entry plus file-order counter.
- `reader`: reader id, type label, reusable pathname buffer, and cache pointer.

Exports:
- Reader/thread accessors, thread-count setters, single-thread mode setter, reader count getter, throttle sleep setter, and minimum-memory checker.

Role:
- Shared by main setup, restore handling, and reader implementation.

Notes:
- Requires `pthread_t`, `struct dir_ent`, and `struct cache` to be visible in including translation units.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/reader.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/restore.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/restore.c

Implements interrupt-triggered recovery for append/update workflows.

State:
- Static `interrupted` flag.
- Static `restore_thread`.

Worker:
- `restore_thrd(void *arg)` blocks `SIGINT`, `SIGTERM`, and `SIGUSR1`, waits for signals, and on the first SIGINT/SIGTERM warns that interrupting will restore the original filesystem and asks for a second interrupt.
- On a restoring signal path, disables progress/info output, cancels and joins pipeline threads in order, flushes queues between stages, then calls external `restorefs()`.

Pipeline cancellation order:
- Initial reader
- Worker readers
- Deflators
- Fragment processors
- Main thread
- Fragment deflators
- Orderer
- Writer

Public init:
- `init_restore_thread()` creates the restore thread and returns its address.

Dependencies:
- Reader thread access through `get_reader_threads()`.
- Queue flush APIs from caches/queues/lists.
- Global worker thread arrays and `processors`.

Risks and notes:
- Thread cancellation assumes each pipeline stage reaches cancellation points and cleanup handlers unlock resources.
- Restore behavior depends on external `restorefs()` implementation.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/restore.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/restore.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/restore.h

Public header for recovery thread initialization.

Exports:
- `init_restore_thread()`

Role:
- Allows main setup code to start the signal-waiting restore thread for recovery-capable operations.

Notes:
- Return type is `pthread_t *`, so including code needs pthread declarations visible.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/restore.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/signals.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/signals.h

Portable signal-wait helper.

Exports:
- `static inline int wait_for_signal(sigset_t *sigmask, int *waiting)`

Platform behavior:
- On macOS and OpenBSD, uses `sigwait()` and clears `*waiting`.
- On other platforms, loops with:
  - `sigtimedwait()` using a 1-second timeout while `*waiting` is true.
  - `sigwaitinfo()` when no timed wait is needed.

Important behavior:
- `EAGAIN` from timed wait clears `*waiting`.
- `EINTR` is ignored and the wait continues.
- Other errors call `BAD_ERROR()` with `strerror(errno)`.
- Returns the received signal number.

Role:
- Gives signal-handling threads a portable way to switch from timed waiting to blocking waiting.

Risks and notes:
- Header assumes `errno`, `EAGAIN`, `EINTR`, `strerror()`, `sigset_t`, `struct timespec`, and `BAD_ERROR()` are available from including context.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/signals.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/sort.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/sort.c

Implements sort-file parsing and priority-ordered file writing.

State:
- Static `mkisofs_style` auto-detection flag.
- Static `sort_info_list[65536]` hashed by inode.
- Public `priority_list[65536]`, where priority is offset by `+32768`.

Helpers:
- `add_priority_list(struct dir_ent *dir, int priority)` prepends a file entry into its priority bucket.
- `get_priority(char *filename, struct stat *buf, int priority)` looks up a stat identity in `sort_info_list`, falling back to inherited priority.
- `add_sort_list(char *path, int priority, int source, char *source_path[])` resolves sort-list paths against absolute/current/mkisofs/source-relative semantics, stats the matching file, and stores device/inode priority mappings.

Priority generation:
- `generate_file_priorities(struct dir_info *dir, int priority, struct stat *buf)` recursively walks directories, inherits directory priority, and adds regular files to `priority_list`.

Sort-file parser:
- `read_sort_file(char *filename, int source, char *source_path[])`
- Supports max line length 16384.
- Skips leading whitespace and comments.
- Parses filenames with backslash escaping for spaces.
- Requires decimal priority in range `-32768` to `32767`.
- Rejects trailing junk.
- Treats missing stat entries as ignored warnings by default, with `-exit-on-error` behavior controlled through error macros.

Writing:
- `sort_files_and_write(struct dir_info *dir)` walks priorities from high to low, writes unread files with `write_file()`, marks inodes read, and reports duplicate/link information through `INFO()`.

Important behavior:
- Sort entries are mapped by `(st_dev, st_ino)`, so hardlinks share priority.
- Ambiguous relative entries mapping to multiple source paths are rejected.
- Legacy mkisofs-style relative sortlists are detected and warned about.

Risks and notes:
- Priority buckets use prepend insertion, so equal-priority write order is reverse of insertion order within each bucket.
- `sort_files_and_write()` ignores its `dir` parameter.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/sort.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/sort.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/sort.h

Public header for sort-list support.

Structures:
- `priority_entry`: links a `dir_ent` into a priority bucket.
- `sort_info`: maps `(st_dev, st_ino)` to a priority with hash chaining.

Exports:
- `read_sort_file(char *, int, char *[])`
- `sort_files_and_write(struct dir_info *)`
- `generate_file_priorities(struct dir_info *, int priority, struct stat *)`
- Global `priority_list[65536]`

Role:
- Used by command-line parsing and reader/writer ordering code to honor user-specified file priorities.

Notes:
- Priority range `-32768..32767` is stored by offsetting into the 65536-entry array.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/sort.h -->