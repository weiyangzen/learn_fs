<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_rm.c -->
# sources/distributed-fs/orangefs/src/apps/user/ofs_rm.c

## Purpose
Implements a POSIX-like `rm` utility for OrangeFS-capable paths using FTS traversal and regular `unlink`/`rmdir` calls.

## Important APIs, Types, And Functions
`rm_options` stores force, interactive, recursive, verbose, debug, and filename list options. `main` opens an FTS traversal, optionally skips directory contents, prompts interactively, unlinks files/symlinks, removes directories postorder, and accumulates error state. `parse_args` handles short and long options. `usage` describes flags.

## Control Flow
Without `-r`, child directories are skipped and directory inputs report an error. With `-r`, directories are removed postorder. File and symlink cases are removed immediately. `-f` disables interactive prompting. The final exit code reflects whether any removal error was seen.

## State And Persistence
Destructively removes files, links, and directories. Runtime state is the FTS cursor and options-owned filename array; no persistent metadata is written.

## Dependencies And Integration Points
Depends on POSIX FTS, `orange.h`, `unlink`, and `rmdir`. It relies on mounted OrangeFS paths behaving through the VFS/client layer rather than direct PVFS sysint calls.

## Risks And Test Signals
Risks include manual `index` tracking instead of `optind`, `-V` printing version but continuing parse, force handling that appears inverted for `ENOENT` checks (`if ENOENT && !force break`), prompting loops that ignore EOF, and `fts_close(fs)` even if `fts_open` failed. Test signals are file, symlink, empty directory, non-empty directory with/without `-r`, missing file with/without `-f`, interactive yes/no, and mixed-success argument lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_rm.c -->
