# sources/distributed-fs/ceph-client/fs/binfmt_script.c

## Purpose
Implements kernel support for scripts beginning with `#!`. It parses the shebang line, rewrites the exec argument vector so the interpreter runs with the script path and optional interpreter argument, and restarts exec with the interpreter file.

## Important APIs, Types, And Functions
The binary-format entry point is `load_script(struct linux_binprm *bprm)`, registered through `script_format` at `core_initcall()`. Small helpers `spacetab()`, `next_non_spacetab()`, and `next_terminator()` parse spaces, tabs, NULs, and the bounded `bprm->buf` shebang region.

## Control Flow
`load_script()` first rejects files whose first two bytes are not `#!`. It searches the initial exec buffer for a newline; when none exists, it allows truncated optional arguments but rejects a potentially truncated interpreter path by requiring a later space, tab, or NUL after the path. It trims trailing spaces/tabs, skips leading spaces/tabs after `#!`, identifies the interpreter path, and optionally identifies one interpreter argument.

If the original script path will be inaccessible after exec, it returns `-ENOENT` before opening the interpreter. It removes the script's original argv0, pushes the script path, optional interpreter argument, and interpreter name in reverse stack order, updates `bprm->interp` through `bprm_change_interp()`, opens the interpreter with `open_exec()`, and stores it in `bprm->interpreter` so the exec loop restarts on that file.

## State And Persistence
The function mutates only the in-flight `linux_binprm`: argument count, copied argument strings, interpreter path, and interpreter file. It deliberately writes temporary NUL bytes into `bprm->buf` to delimit parsed strings. No persistent filesystem state is changed.

## Dependencies And Integration Points
It depends on the generic exec argument stack helpers (`remove_arg_zero()`, `copy_string_kernel()`, `bprm_change_interp()`), VFS executable opening, and the exec loop's convention that setting `bprm->interpreter` restarts format probing. It also cooperates with `binfmt_misc`, which may update `bprm->interp` before the script handler sees an interpreter.

## Risks
The main risk is accepting a truncated interpreter path from a too-long shebang line. The code intentionally rejects that case while allowing truncated interpreter arguments. Another risk is path-inaccessible scripts, where interpreters would fail or behave differently after fd close-on-exec; the explicit `BINPRM_FLAGS_PATH_INACCESSIBLE` check prevents that. Argument order is subtle because exec argument strings are stored backward.

## Test Signals
Tests should cover normal shebangs, leading whitespace after `#!`, optional interpreter arguments, trailing spaces, no newline within `BINPRM_BUF_SIZE`, truncated interpreter path rejection, long optional argument truncation acceptance, inaccessible `/dev/fd` style script paths, and interpreter open failures.
