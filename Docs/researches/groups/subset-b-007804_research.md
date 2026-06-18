# subset-b-007804 Research

Grouped research report for OpenAFS test files. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-stat.c -->
# sources/distributed-fs/openafs/src/tests/create-stat.c

## Purpose
Validates that creating a sibling file does not perturb an existing AFS file's inode identity and that the POSIX inode matches the VenusFid-derived AFS file id.

## Important APIs, Types, and Functions
functions: usage, main; AFS calls/macros: fs_lib, fs_getfid

## Control Flow
Requires one filename, opens the original, creates `<file>.new` with O_EXCL, compares stat/lstat inode values before and after creation, calls `fs_getfid`, computes the expected AFS inode from Volume/Vnode, then unlinks both files.

## State and Persistence Behavior
Creates and removes the supplied file and a `.new` sibling; errors attempt cleanup before failing.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting; AFS interfaces fs_lib, fs_getfid

## Risks and Test Signals
Strongly AFS-specific because it depends on `pioctl(VIOCGETFID)` semantics and the inode derivation formula; failures signal vnode identity regression or stale stat metadata.

## Source Notes
Read as C program; 145 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-stat.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-symlinks.c -->
# sources/distributed-fs/openafs/src/tests/create-symlinks.c

## Purpose
Stress-creates many numeric symlinks and verifies all link targets remain stable.

## Important APIs, Types, and Functions
functions: creat_symlinks, verify_contents, usage, main

## Control Flow
Parses count and optional verbose flag, creates symlinks named `0..count-1` to the constant target `kaka`, then reads every symlink back with `readlink` and compares the content.

## State and Persistence Behavior
Persists count-sized directory entries in the current directory and leaves cleanup to the surrounding harness.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
Exercises directory mutation, symlink creation, link target storage, and MAXPATHLEN-sized read buffers.

## Source Notes
Read as C program; 138 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-symlinks.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dd -->
# sources/distributed-fs/openafs/src/tests/dd

## Purpose
Runs a focused shell-level filesystem test built around `dd, rm, echo`.

## Important APIs, Types, and Functions
commands: dd, rm, echo

## Control Flow
Sequential shell commands run in the harness work directory: `dd, rm, echo`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `dd, rm, echo`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, dd, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 8 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dd -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/deep-tree -->
# sources/distributed-fs/openafs/src/tests/deep-tree

## Purpose
Runs a focused shell-level filesystem test built around `then, mkdir, , $SHELL`.

## Important APIs, Types, and Functions
commands: then, mkdir, , $SHELL, ${objdir}/rm-rf

## Control Flow
Sequential shell commands run in the harness work directory: `then, mkdir, , $SHELL, ${objdir}/rm-rf`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 6 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/deep-tree -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/deep-tree2 -->
# sources/distributed-fs/openafs/src/tests/deep-tree2

## Purpose
Runs a focused shell-level filesystem test built around `mkdir, rm`.

## Important APIs, Types, and Functions
commands: mkdir, rm

## Control Flow
Sequential shell commands run in the harness work directory: `mkdir, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, rm

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 12 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/deep-tree2 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dir-size-mismatch -->
# sources/distributed-fs/openafs/src/tests/dir-size-mismatch

## Purpose
Runs a focused shell-level filesystem test built around `then, i, ++i, ln`.

## Important APIs, Types, and Functions
commands: then, i, ++i, ln, find, xargs, rm

## Control Flow
Sequential shell commands run in the harness work directory: `then, i, ++i, ln, find, xargs, rm`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, i, ++i, ln, find, xargs`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, ln, find, xargs, awk, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 10 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dir-size-mismatch -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dir-tree -->
# sources/distributed-fs/openafs/src/tests/dir-tree

## Purpose
Runs a focused shell-level filesystem test built around `shift, expr, mkdir, cd`.

## Important APIs, Types, and Functions
commands: shift, expr, mkdir, cd, \, $SHELL

## Control Flow
Sequential shell commands run in the harness work directory: `shift, expr, mkdir, cd, \, $SHELL`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, expr

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 22 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dir-tree -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dup2-and-unlog.c -->
# sources/distributed-fs/openafs/src/tests/dup2-and-unlog.c

## Purpose
Runs a focused C filesystem test with entry points `main`.

## Important APIs, Types, and Functions
functions: main; AFS calls/macros: ktc_ForgetAllTokens

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, write, dup2`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting; AFS interfaces ktc_ForgetAllTokens

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 34 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dup2-and-unlog.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/echo-n.c -->
# sources/distributed-fs/openafs/src/tests/echo-n.c

## Purpose
Runs a focused C filesystem test with entry points `main`.

## Important APIs, Types, and Functions
functions: main

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls ``; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 17 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/echo-n.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/err.c -->
# sources/distributed-fs/openafs/src/tests/err.c

## Purpose
Implements or declares BSD-style `err(3)`/`warn(3)` compatibility helpers for the test programs.

## Important APIs, Types, and Functions
functions: err

## Control Flow
`main` drives the test through helper functions `err` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls ``; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 46 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/err.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/err.h -->
# sources/distributed-fs/openafs/src/tests/err.h

## Purpose
Implements or declares BSD-style `err(3)`/`warn(3)` compatibility helpers for the test programs.

## Important APIs, Types, and Functions
No callable API; the file is fixture/template content.

## Control Flow
The file is consumed by the surrounding build/test harness as a static fixture or substituted script template.

## State and Persistence Behavior
Uses POSIX filesystem calls ``; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C header; 72 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/err.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/errx.c -->
# sources/distributed-fs/openafs/src/tests/errx.c

## Purpose
Implements or declares BSD-style `err(3)`/`warn(3)` compatibility helpers for the test programs.

## Important APIs, Types, and Functions
functions: errx

## Control Flow
`main` drives the test through helper functions `errx` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls ``; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 46 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/errx.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/exec -->
# sources/distributed-fs/openafs/src/tests/exec

## Purpose
Runs a focused shell-level filesystem test built around `echo, test, chmod`.

## Important APIs, Types, and Functions
commands: echo, test, chmod

## Control Flow
Sequential shell commands run in the harness work directory: `echo, test, chmod`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `chmod`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands chmod, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 9 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/exec -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/exit-wo-close.c -->
# sources/distributed-fs/openafs/src/tests/exit-wo-close.c

## Purpose
Runs a focused C filesystem test with entry points `child, parent, doit, main`.

## Important APIs, Types, and Functions
functions: child, parent, doit, main

## Control Flow
`main` drives the test through helper functions `child, parent, doit` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, read, write, stat, fstat, fork, waitpid`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 122 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/exit-wo-close.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/extcopyin -->
# sources/distributed-fs/openafs/src/tests/extcopyin

## Purpose
Runs a focused shell-level filesystem test built around `${FS}, ${objdir}/write-rand, ${objdir}/afscp, diff`.

## Important APIs, Types, and Functions
commands: ${FS}, ${objdir}/write-rand, ${objdir}/afscp, diff

## Control Flow
Sequential shell commands run in the harness work directory: `${FS}, ${objdir}/write-rand, ${objdir}/afscp, diff`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `${FS}, ${objdir}/write-rand, ${objdir}/afscp, diff`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands diff

## Risks and Test Signals
uses `/tmp` scratch files; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 11 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/extcopyin -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/extcopyout -->
# sources/distributed-fs/openafs/src/tests/extcopyout

## Purpose
Runs a focused shell-level filesystem test built around `${FS}, ${objdir}/write-rand, ${objdir}/afscp, diff`.

## Important APIs, Types, and Functions
commands: ${FS}, ${objdir}/write-rand, ${objdir}/afscp, diff

## Control Flow
Sequential shell commands run in the harness work directory: `${FS}, ${objdir}/write-rand, ${objdir}/afscp, diff`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `${FS}, ${objdir}/write-rand, ${objdir}/afscp, diff`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands diff

## Risks and Test Signals
uses `/tmp` scratch files; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 11 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/extcopyout -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fcachesize-dir -->
# sources/distributed-fs/openafs/src/tests/fcachesize-dir

## Purpose
Checks OpenAFS cache accounting before and after a file or directory operation.

## Important APIs, Types, and Functions
commands: awk, mkdir, test, rmdir

## Control Flow
Sequential shell commands run in the harness work directory: `awk, mkdir, test, rmdir`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir, rmdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, rmdir, awk, expr, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 13 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fcachesize-dir -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fcachesize-file-small -->
# sources/distributed-fs/openafs/src/tests/fcachesize-file-small

## Purpose
Checks OpenAFS cache accounting before and after a file or directory operation.

## Important APIs, Types, and Functions
commands: awk, echo, test, rm

## Control Flow
Sequential shell commands run in the harness work directory: `awk, echo, test, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `awk, echo, test, rm`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, awk, expr, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 13 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fcachesize-file-small -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fcachesize-read-file -->
# sources/distributed-fs/openafs/src/tests/fcachesize-read-file

## Purpose
Checks OpenAFS cache accounting before and after a file or directory operation.

## Important APIs, Types, and Functions
commands: awk, dd, rm, echo

## Control Flow
Sequential shell commands run in the harness work directory: `awk, dd, rm, echo`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `awk, dd, rm, echo`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, dd, awk, expr, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 14 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fcachesize-read-file -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fcachesize-write-file -->
# sources/distributed-fs/openafs/src/tests/fcachesize-write-file

## Purpose
Checks OpenAFS cache accounting before and after a file or directory operation.

## Important APIs, Types, and Functions
commands: awk, dd, echo

## Control Flow
Sequential shell commands run in the harness work directory: `awk, dd, echo`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `awk, dd, echo`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands dd, awk, expr, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 13 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fcachesize-write-file -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fchmod.c -->
# sources/distributed-fs/openafs/src/tests/fchmod.c

## Purpose
Runs a focused C filesystem test with entry points `main`.

## Important APIs, Types, and Functions
functions: main

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, write, stat, fstat, fchmod, unlink`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 70 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fchmod.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/find-and-cat-netbsd -->
# sources/distributed-fs/openafs/src/tests/find-and-cat-netbsd

## Purpose
Runs a focused shell-level filesystem test built around `then, find, >`.

## Important APIs, Types, and Functions
commands: then, find, >

## Control Flow
Sequential shell commands run in the harness work directory: `then, find, >`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, find, >`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands find, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 5 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/find-and-cat-netbsd -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/find-linux -->
# sources/distributed-fs/openafs/src/tests/find-linux

## Purpose
Runs a focused shell-level filesystem test built around `then, cd, find`.

## Important APIs, Types, and Functions
commands: then, cd, find

## Control Flow
Sequential shell commands run in the harness work directory: `then, cd, find`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, cd, find`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands find, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 5 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/find-linux -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fs-flush -->
# sources/distributed-fs/openafs/src/tests/fs-flush

## Purpose
Runs a focused shell-level filesystem test built around `>, ${FS}, test`.

## Important APIs, Types, and Functions
commands: >, ${FS}, test

## Control Flow
Sequential shell commands run in the harness work directory: `>, ${FS}, test`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `>, ${FS}, test`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 6 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fs-flush -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fs-sa-la -->
# sources/distributed-fs/openafs/src/tests/fs-sa-la

## Purpose
Runs a focused shell-level filesystem test built around `${FS}`.

## Important APIs, Types, and Functions
commands: ${FS}

## Control Flow
Sequential shell commands run in the harness work directory: `${FS}`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `${FS}`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 6 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fs-sa-la -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fs_lib.c -->
# sources/distributed-fs/openafs/src/tests/fs_lib.c

## Purpose
Provides reusable test helpers around AFS cache-manager `pioctl` operations.

## Important APIs, Types, and Functions
functions: fs_getfid, fs_nop, fs_getfilecellname, fs_setcrypt, fs_getcrypt, fs_connect, fs_setfprio, fs_getfprio, fs_setmaxfprio, fs_getmaxfprio, fs_getfilecachestats, fs_getaviatorstats, fs_gcpags, fs_calculate_cache, fs_invalidate, debug; AFS calls/macros: fs_lib, fs_getfid, pioctl, VIOCGETFID, fs_nop, VIOCNOP, fs_getfilecellname, VIOC_FILE_CELL_NAME, VIOC_SETRXKCRYPT, fs_setcrypt, VIOC_GETRXKCRYPT, fs_getcrypt, VIOCCONNECTMODE, fs_connect, VIOC_FPRIOSTATUS, fs_setfprio

## Control Flow
Each public wrapper initializes `struct ViceIoctl`, fills input/output buffers for one Venus command, calls `pioctl`, and returns errno-style status; mount-point helpers split paths before issuing mount-point stat/delete ioctls.

## State and Persistence Behavior
Mostly stateless, but functions can change cache-manager state: crypt level, connect mode, fetch priority, sysname, cache size, debug flags, mount points, cache flushing, callback invalidation, and PAG garbage collection.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting; AFS interfaces fs_lib, fs_getfid, pioctl, VIOCGETFID, fs_nop, VIOCNOP, fs_getfilecellname, VIOC_FILE_CELL_NAME, VIOC_SETRXKCRYPT, fs_setcrypt

## Risks and Test Signals
Many functions are conditional on OpenAFS/Arla ioctl defines and some use legacy compatibility probes; wrong buffer sizing or renumbered ioctl assumptions can produce false test failures across client versions.

## Source Notes
Read as C program; 843 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fs_lib.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fs_lib.h -->
# sources/distributed-fs/openafs/src/tests/fs_lib.h

## Purpose
Runs a focused C filesystem test with entry points ``.

## Important APIs, Types, and Functions
AFS calls/macros: fs_lib, fs_getfid, fs_rmmount

## Control Flow
The file is consumed by the surrounding build/test harness as a static fixture or substituted script template.

## State and Persistence Behavior
Uses POSIX filesystem calls `fs_getfid, fs_rmmount`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; AFS interfaces fs_lib, fs_getfid, fs_rmmount

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C header; 17 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fs_lib.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fsx.c -->
# sources/distributed-fs/openafs/src/tests/fsx.c

## Purpose
Runs the classic randomized file-system exerciser against an AFS-hosted file, mixing reads, writes, mmap reads/writes, truncates, and close/reopen cycles while checking an in-memory oracle.

## Important APIs, Types, and Functions
functions: prt, prterr, log4, logdump, save_buffer, report_failure, check_buffers, check_size, check_trunc_hack, doread, domapread, gendata, dowrite, domapwrite, dotruncate, writefileimage; AFS calls/macros: AFS_FALLTHROUGH

## Control Flow
Parses many tuning flags, seeds pseudo-random operations, logs the last 1000 operations, mutates `good_buf` as the expected file image, executes matching system calls on the target file, compares reads/mmap reads against the oracle, and dumps the operation log plus `.fsxgood` data on failure.

## State and Persistence Behavior
Creates and mutates one target file plus optional `.fsxlog` and `.fsxgood` evidence; global state tracks file size, biggest truncate, operation count, random seed, mapping/read/write enablement, and failure offsets.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting; AFS interfaces AFS_FALLTHROUGH

## Risks and Test Signals
High-value stress test for cache coherency, mmap/writeback, holes, truncate extension, short I/O, and close/open callback behavior; randomness means seed and options are required for reproducible failures.

## Source Notes
Read as C program; 1063 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fsx.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ga-test.c -->
# sources/distributed-fs/openafs/src/tests/ga-test.c

## Purpose
Unit-tests the AFS command parser/list-building helpers by feeding simple string, repeated string, integer, and flag options.

## Important APIs, Types, and Functions
functions: test_simple_string, test_simple_strings, test_simple_integer, test_simple_flag, main

## Control Flow
Defines test callbacks, builds `cmd_syndesc` command descriptions, invokes the command parser for each synthetic scenario, and checks that parsed values match expected strings, counts, integers, and flags.

## State and Persistence Behavior
No persistent filesystem state; all validation is in-process parser state and callback-observed command fields.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
Protects command-line compatibility for OpenAFS-style tools; failures indicate regression in parameter parsing or list handling rather than filesystem behavior.

## Source Notes
Read as C program; 308 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ga-test.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/generic-build -->
# sources/distributed-fs/openafs/src/tests/generic-build

## Purpose
Runs a focused shell-level filesystem test built around `echo, gzip, tar, cd`.

## Important APIs, Types, and Functions
commands: echo, gzip, tar, cd, ./configure, make

## Control Flow
Sequential shell commands run in the harness work directory: `echo, gzip, tar, cd, ./configure, make`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `echo, gzip, tar, cd, ./configure, make`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands tar, gzip, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 18 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/generic-build -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/getdents-and-unlink1 -->
# sources/distributed-fs/openafs/src/tests/getdents-and-unlink1

## Purpose
Runs a focused shell-level filesystem test built around `then, gzip, tar, cd`.

## Important APIs, Types, and Functions
commands: then, gzip, tar, cd, $objdir/kill-softer, test

## Control Flow
Sequential shell commands run in the harness work directory: `then, gzip, tar, cd, $objdir/kill-softer, test`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, gzip, tar, cd, $objdir/kill-softer, test`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands tar, gzip, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 9 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/getdents-and-unlink1 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/getdents-and-unlink2 -->
# sources/distributed-fs/openafs/src/tests/getdents-and-unlink2

## Purpose
Runs a focused shell-level filesystem test built around `then, gzip, tar, cd`.

## Important APIs, Types, and Functions
commands: then, gzip, tar, cd, $objdir/rm-rf, test

## Control Flow
Sequential shell commands run in the harness work directory: `then, gzip, tar, cd, $objdir/rm-rf, test`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, gzip, tar, cd, $objdir/rm-rf, test`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands tar, gzip, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 9 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/getdents-and-unlink2 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/getdents-and-unlink3 -->
# sources/distributed-fs/openafs/src/tests/getdents-and-unlink3

## Purpose
Runs a focused shell-level filesystem test built around `then, gzip, tar, cd`.

## Important APIs, Types, and Functions
commands: then, gzip, tar, cd, $objdir/kill-softly, test

## Control Flow
Sequential shell commands run in the harness work directory: `then, gzip, tar, cd, $objdir/kill-softly, test`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, gzip, tar, cd, $objdir/kill-softly, test`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands tar, gzip, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 9 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/getdents-and-unlink3 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/grind-arla-with-cvs -->
# sources/distributed-fs/openafs/src/tests/grind-arla-with-cvs

## Purpose
Runs a focused shell-level filesystem test built around `echo, sleep, test, mkdir`.

## Important APIs, Types, and Functions
commands: echo, sleep, test, mkdir, cd, cvs, grep, sh, ../arla/configure, mv

## Control Flow
Sequential shell commands run in the harness work directory: `echo, sleep, test, mkdir, cd, cvs, grep, sh`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, cvs, sleep, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 52 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/grind-arla-with-cvs -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hardlink1.c -->
# sources/distributed-fs/openafs/src/tests/hardlink1.c

## Purpose
Exercises hard-link creation, link-count semantics, and cross-volume or high-count hard-link constraints.

## Important APIs, Types, and Functions
functions: main

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, write, stat, lstat, fstat, unlink, link`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
detects link-count and cross-volume hard-link policy regressions; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 143 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hardlink1.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hardlink2.c -->
# sources/distributed-fs/openafs/src/tests/hardlink2.c

## Purpose
Exercises hard-link creation, link-count semantics, and cross-volume or high-count hard-link constraints.

## Important APIs, Types, and Functions
functions: main

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `mkdir, rmdir, link`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
detects link-count and cross-volume hard-link policy regressions; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 63 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hardlink2.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hardlink3 -->
# sources/distributed-fs/openafs/src/tests/hardlink3

## Purpose
Exercises hard-link creation, link-count semantics, and cross-volume or high-count hard-link constraints.

## Important APIs, Types, and Functions
commands: then, touch, i, ++i, ln, ls, ${FS}, rm

## Control Flow
Sequential shell commands run in the harness work directory: `then, touch, i, ++i, ln, ls, ${FS}, rm`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `stat`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, ln, touch, awk, test

## Risks and Test Signals
may be skipped in FAST mode; detects link-count and cross-volume hard-link policy regressions; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 28 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hardlink3 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hardlink4.c -->
# sources/distributed-fs/openafs/src/tests/hardlink4.c

## Purpose
Exercises hard-link creation, link-count semantics, and cross-volume or high-count hard-link constraints.

## Important APIs, Types, and Functions
functions: main

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, stat, fstat, mkdir, rmdir, unlink, link`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
detects link-count and cross-volume hard-link policy regressions; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 94 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hardlink4.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hardlink5 -->
# sources/distributed-fs/openafs/src/tests/hardlink5

## Purpose
Exercises hard-link creation, link-count semantics, and cross-volume or high-count hard-link constraints.

## Important APIs, Types, and Functions
commands: then, touch, ln, echo, rm

## Control Flow
Sequential shell commands run in the harness work directory: `then, touch, ln, echo, rm`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, touch, ln, echo, rm`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, ln, touch, test

## Risks and Test Signals
may be skipped in FAST mode; detects link-count and cross-volume hard-link policy regressions; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 14 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hardlink5 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hello-world.in -->
# sources/distributed-fs/openafs/src/tests/hello-world.in

## Purpose
Runs a focused shell-level filesystem test built around `cat, int, }, FOO`.

## Important APIs, Types, and Functions
commands: cat, int, }, FOO, %CC%, ./foo, rm

## Control Flow
Sequential shell commands run in the harness work directory: `cat, int, }, FOO, %CC%, ./foo, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `cat, int, }, FOO, %CC%, ./foo`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 8 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hello-world.in -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/intr-read.c -->
# sources/distributed-fs/openafs/src/tests/intr-read.c

## Purpose
Runs a focused C filesystem test with entry points `sigalrm, try_read, find, main`.

## Important APIs, Types, and Functions
functions: sigalrm, try_read, find, main

## Control Flow
`main` drives the test through helper functions `sigalrm, try_read, find` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, stat, lstat, opendir, readdir`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 125 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/intr-read.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/intr-read1 -->
# sources/distributed-fs/openafs/src/tests/intr-read1

## Purpose
Runs a focused shell-level filesystem test built around `$objdir/intr-read`.

## Important APIs, Types, and Functions
commands: $objdir/intr-read

## Control Flow
Sequential shell commands run in the harness work directory: `$objdir/intr-read`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `$objdir/intr-read`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 4 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/intr-read1 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/invalidate-file.c -->
# sources/distributed-fs/openafs/src/tests/invalidate-file.c

## Purpose
Runs a focused C filesystem test with entry points `create_write_file, read_file, mmap_read_file, mmap_write_file, main`.

## Important APIs, Types, and Functions
functions: create_write_file, read_file, mmap_read_file, mmap_write_file, main; AFS calls/macros: fs_invalidate

## Control Flow
`main` drives the test through helper functions `create_write_file, read_file, mmap_read_file, mmap_write_file` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, read, write, mmap, munmap, fs_invalidate`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting; AFS interfaces fs_invalidate

## Risks and Test Signals
targets mmap/cache coherency and writeback edge cases; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 200 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/invalidate-file.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/kill-softer.c -->
# sources/distributed-fs/openafs/src/tests/kill-softer.c

## Purpose
Runs a focused C filesystem test with entry points `kill_one, do_dir, kill_dir, main`.

## Important APIs, Types, and Functions
functions: kill_one, do_dir, kill_dir, main

## Control Flow
`main` drives the test through helper functions `kill_one, do_dir, kill_dir` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `stat, lstat, rmdir, opendir, readdir, unlink, chdir`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 184 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/kill-softer.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/kill-softly.c -->
# sources/distributed-fs/openafs/src/tests/kill-softly.c

## Purpose
Runs a focused C filesystem test with entry points `kill_one, do_dir, kill_dir, main`.

## Important APIs, Types, and Functions
functions: kill_one, do_dir, kill_dir, main

## Control Flow
`main` drives the test through helper functions `kill_one, do_dir, kill_dir` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `stat, lstat, rmdir, opendir, readdir, unlink, chdir`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 155 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/kill-softly.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/kotest -->
# sources/distributed-fs/openafs/src/tests/kotest

## Purpose
Runs a focused shell-level filesystem test built around `exec`.

## Important APIs, Types, and Functions
commands: exec

## Control Flow
Sequential shell commands run in the harness work directory: `exec`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `exec`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 4 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/kotest -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-dir-16384 -->
# sources/distributed-fs/openafs/src/tests/large-dir-16384

## Purpose
Stresses large directory creation, lookup, and removal behavior.

## Important APIs, Types, and Functions
commands: then, $objdir/large-dir

## Control Flow
Sequential shell commands run in the harness work directory: `then, $objdir/large-dir`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, $objdir/large-dir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 4 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-dir-16384 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-dir-extra -->
# sources/distributed-fs/openafs/src/tests/large-dir-extra

## Purpose
Stresses large directory creation, lookup, and removal behavior.

## Important APIs, Types, and Functions
commands: then, $objdir/large-dir2, $objdir/large-dir3

## Control Flow
Sequential shell commands run in the harness work directory: `then, $objdir/large-dir2, $objdir/large-dir3`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, $objdir/large-dir2, $objdir/large-dir3`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 7 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-dir-extra -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-dir.c -->
# sources/distributed-fs/openafs/src/tests/large-dir.c

## Purpose
Stresses large directory creation, lookup, and removal behavior.

## Important APIs, Types, and Functions
functions: creat_files, usage, main

## Control Flow
`main` drives the test through helper functions `creat_files, usage` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, stat, mkdir, opendir, readdir, unlink, chdir`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 148 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-dir.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-dir2.c -->
# sources/distributed-fs/openafs/src/tests/large-dir2.c

## Purpose
Stresses large directory creation, lookup, and removal behavior.

## Important APIs, Types, and Functions
functions: creat_files, usage, main

## Control Flow
`main` drives the test through helper functions `creat_files, usage` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, stat, mkdir, rmdir, opendir, readdir, unlink, chdir`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 127 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-dir2.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-dir3.c -->
# sources/distributed-fs/openafs/src/tests/large-dir3.c

## Purpose
Stresses large directory creation, lookup, and removal behavior.

## Important APIs, Types, and Functions
functions: creat_files, usage, main

## Control Flow
`main` drives the test through helper functions `creat_files, usage` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, stat, mkdir, rmdir, opendir, readdir, unlink, chdir`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 118 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-dir3.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-filename -->
# sources/distributed-fs/openafs/src/tests/large-filename

## Purpose
Runs a focused shell-level filesystem test built around `touch, rm`.

## Important APIs, Types, and Functions
commands: touch, rm

## Control Flow
Sequential shell commands run in the harness work directory: `touch, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `touch, rm`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, touch

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 6 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-filename -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ls-afs -->
# sources/distributed-fs/openafs/src/tests/ls-afs

## Purpose
Runs a focused shell-level filesystem test built around `then, ls, true`.

## Important APIs, Types, and Functions
commands: then, ls, true

## Control Flow
Sequential shell commands run in the harness work directory: `then, ls, true`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, ls, true`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 5 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ls-afs -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/make-page.c -->
# sources/distributed-fs/openafs/src/tests/make-page.c

## Purpose
Runs a focused C filesystem test with entry points `main`.

## Important APIs, Types, and Functions
functions: main

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, mmap, munmap`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
targets mmap/cache coherency and writeback edge cases; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 97 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/make-page.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-dirs -->
# sources/distributed-fs/openafs/src/tests/many-dirs

## Purpose
Stresses repeated file, directory, fetch, store, or symlink operations.

## Important APIs, Types, and Functions
commands: mkdir, cd, $objdir/create-dirs, $objdir/rm-rf

## Control Flow
Sequential shell commands run in the harness work directory: `mkdir, cd, $objdir/create-dirs, $objdir/rm-rf`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 6 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-dirs -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-fetchs -->
# sources/distributed-fs/openafs/src/tests/many-fetchs

## Purpose
Stresses repeated file, directory, fetch, store, or symlink operations.

## Important APIs, Types, and Functions
commands: touch, echo, i, ++i, ${FS}, cat, rm

## Control Flow
Sequential shell commands run in the harness work directory: `touch, echo, i, ++i, ${FS}, cat, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `touch, echo, i, ++i, ${FS}, cat`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, touch, awk

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 15 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-fetchs -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-files -->
# sources/distributed-fs/openafs/src/tests/many-files

## Purpose
Stresses repeated file, directory, fetch, store, or symlink operations.

## Important APIs, Types, and Functions
commands: $objdir/create-files

## Control Flow
Sequential shell commands run in the harness work directory: `$objdir/create-files`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `$objdir/create-files`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 4 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-files -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-files-with-content -->
# sources/distributed-fs/openafs/src/tests/many-files-with-content

## Purpose
Stresses repeated file, directory, fetch, store, or symlink operations.

## Important APIs, Types, and Functions
commands: $objdir/create-files

## Control Flow
Sequential shell commands run in the harness work directory: `$objdir/create-files`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `$objdir/create-files`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 4 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-files-with-content -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-stores -->
# sources/distributed-fs/openafs/src/tests/many-stores

## Purpose
Stresses repeated file, directory, fetch, store, or symlink operations.

## Important APIs, Types, and Functions
commands: touch, i, ++i, echo, rm

## Control Flow
Sequential shell commands run in the harness work directory: `touch, i, ++i, echo, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `touch, i, ++i, echo, rm`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, touch, awk

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 10 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-stores -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-symlinks -->
# sources/distributed-fs/openafs/src/tests/many-symlinks

## Purpose
Stresses repeated file, directory, fetch, store, or symlink operations.

## Important APIs, Types, and Functions
commands: $objdir/create-symlinks

## Control Flow
Sequential shell commands run in the harness work directory: `$objdir/create-symlinks`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `$objdir/create-symlinks`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 4 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-symlinks -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkdir -->
# sources/distributed-fs/openafs/src/tests/mkdir

## Purpose
Exercises directory creation/removal semantics and directory visibility through `.` and `..` entries.

## Important APIs, Types, and Functions
commands: mkdir, echo, rmdir, test, rm

## Control Flow
Sequential shell commands run in the harness work directory: `mkdir, echo, rmdir, test, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir, rmdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, rmdir, rm, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 10 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkdir -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkdir-lnk -->
# sources/distributed-fs/openafs/src/tests/mkdir-lnk

## Purpose
Exercises directory creation/removal semantics and directory visibility through `.` and `..` entries.

## Important APIs, Types, and Functions
commands: mkdir, ls, awk, rmdir

## Control Flow
Sequential shell commands run in the harness work directory: `mkdir, ls, awk, rmdir`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir, rmdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, rmdir, awk

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 12 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkdir-lnk -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkdir1 -->
# sources/distributed-fs/openafs/src/tests/mkdir1

## Purpose
Exercises directory creation/removal semantics and directory visibility through `.` and `..` entries.

## Important APIs, Types, and Functions
commands: mkdir, test, rmdir

## Control Flow
Sequential shell commands run in the harness work directory: `mkdir, test, rmdir`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir, rmdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, rmdir, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 7 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkdir1 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkdir2.c -->
# sources/distributed-fs/openafs/src/tests/mkdir2.c

## Purpose
Exercises directory creation/removal semantics and directory visibility through `.` and `..` entries.

## Important APIs, Types, and Functions
functions: main

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `stat, lstat, mkdir, rmdir`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 77 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkdir2.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkdir3.c -->
# sources/distributed-fs/openafs/src/tests/mkdir3.c

## Purpose
Exercises directory creation/removal semantics and directory visibility through `.` and `..` entries.

## Important APIs, Types, and Functions
functions: main

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, stat, lstat, mkdir, rmdir, unlink`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 95 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkdir3.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkm-rmm -->
# sources/distributed-fs/openafs/src/tests/mkm-rmm

## Purpose
Runs a focused shell-level filesystem test built around `${FS}, test`.

## Important APIs, Types, and Functions
commands: ${FS}, test

## Control Flow
Sequential shell commands run in the harness work directory: `${FS}, test`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `${FS}, test`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands test

## Risks and Test Signals
may require privileged execution; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 13 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkm-rmm -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mmap-and-read.c -->
# sources/distributed-fs/openafs/src/tests/mmap-and-read.c

## Purpose
Compares mmap-backed access with ordinary file I/O to catch cache coherency or writeback regressions.

## Important APIs, Types, and Functions
functions: generate_random_file, read_file, test, main

## Control Flow
`main` drives the test through helper functions `generate_random_file, read_file, test` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, read, write, ftruncate, mmap, munmap`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
targets mmap/cache coherency and writeback edge cases; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 153 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mmap-and-read.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mmap-cat.c -->
# sources/distributed-fs/openafs/src/tests/mmap-cat.c

## Purpose
Compares mmap-backed access with ordinary file I/O to catch cache coherency or writeback regressions.

## Important APIs, Types, and Functions
functions: doit_mmap, doit_read, doit, usage, main

## Control Flow
`main` drives the test through helper functions `doit_mmap, doit_read, doit, usage` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, read, write, stat, fstat, mmap, munmap`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
targets mmap/cache coherency and writeback edge cases; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 137 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mmap-cat.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mmap-shared-write.c -->
# sources/distributed-fs/openafs/src/tests/mmap-shared-write.c

## Purpose
Compares mmap-backed access with ordinary file I/O to catch cache coherency or writeback regressions.

## Important APIs, Types, and Functions
functions: doit, usage, main

## Control Flow
`main` drives the test through helper functions `doit, usage` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, ftruncate, mmap, msync`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
targets mmap/cache coherency and writeback edge cases; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 96 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mmap-shared-write.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mmap-vs-read.c -->
# sources/distributed-fs/openafs/src/tests/mmap-vs-read.c

## Purpose
Compares mmap-backed access with ordinary file I/O to catch cache coherency or writeback regressions.

## Important APIs, Types, and Functions
functions: generate_file, read_file, mmap_file, do_test, main

## Control Flow
`main` drives the test through helper functions `generate_file, read_file, mmap_file, do_test` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, read, write, mmap, unlink`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
targets mmap/cache coherency and writeback edge cases; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 167 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mmap-vs-read.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mmap-vs-read2.c -->
# sources/distributed-fs/openafs/src/tests/mmap-vs-read2.c

## Purpose
Compares mmap-backed access with ordinary file I/O to catch cache coherency or writeback regressions.

## Important APIs, Types, and Functions
functions: generate_file, read_file, mmap_file, do_test, main

## Control Flow
`main` drives the test through helper functions `generate_file, read_file, mmap_file, do_test` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, read, write, mmap, unlink`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
targets mmap/cache coherency and writeback edge cases; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 167 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mmap-vs-read2.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mountpoint.in -->
# sources/distributed-fs/openafs/src/tests/mountpoint.in

## Purpose
Runs a focused shell-level filesystem test built around `${FS}, touch`.

## Important APIs, Types, and Functions
commands: ${FS}, touch

## Control Flow
Sequential shell commands run in the harness work directory: `${FS}, touch`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `${FS}, touch`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands touch

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 9 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mountpoint.in -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/null-search.c -->
# sources/distributed-fs/openafs/src/tests/null-search.c

## Purpose
Runs a focused C filesystem test with entry points `usage, parse_options, my_error_cb, my_file_cb, main`.

## Important APIs, Types, and Functions
functions: usage, parse_options, my_error_cb, my_file_cb, main

## Control Flow
`main` drives the test through helper functions `usage, parse_options, my_error_cb, my_file_cb` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls ``; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 178 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/null-search.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/parallel1 -->
# sources/distributed-fs/openafs/src/tests/parallel1

## Purpose
Runs a focused shell-level filesystem test built around `then, $objdir/test-parallel1`.

## Important APIs, Types, and Functions
commands: then, $objdir/test-parallel1

## Control Flow
Sequential shell commands run in the harness work directory: `then, $objdir/test-parallel1`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, $objdir/test-parallel1`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 5 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/parallel1 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/pine.c -->
# sources/distributed-fs/openafs/src/tests/pine.c

## Purpose
Runs a focused C filesystem test with entry points `main`.

## Important APIs, Types, and Functions
functions: main

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, stat, chmod, unlink, link`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 99 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/pine.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsadduser.pl -->
# sources/distributed-fs/openafs/src/tests/ptsadduser.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_add` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_add; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_add

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_add`, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_add; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 17 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsadduser.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptschown.pl -->
# sources/distributed-fs/openafs/src/tests/ptschown.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_chown` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_chown; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_chown

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_chown`, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_chown; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 17 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptschown.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptscreategroup.pl -->
# sources/distributed-fs/openafs/src/tests/ptscreategroup.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_creategroup` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_creategroup; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_creategroup

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_creategroup`, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_creategroup; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 17 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptscreategroup.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptscreateuser.pl -->
# sources/distributed-fs/openafs/src/tests/ptscreateuser.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_createuser` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_createuser; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_createuser

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_createuser`, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_createuser; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 17 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptscreateuser.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsdeletegroup.pl -->
# sources/distributed-fs/openafs/src/tests/ptsdeletegroup.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_delete` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_delete; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_delete

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_delete`, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_delete; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 17 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsdeletegroup.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsdeleteuser.pl -->
# sources/distributed-fs/openafs/src/tests/ptsdeleteuser.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_delete` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_delete; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_delete

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_delete`, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_delete; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 17 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsdeleteuser.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsexaminegroup.pl -->
# sources/distributed-fs/openafs/src/tests/ptsexaminegroup.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_examine` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_examine; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_examine

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_examine` and checks returned fields, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_examine; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 27 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsexaminegroup.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsexamineuser.pl -->
# sources/distributed-fs/openafs/src/tests/ptsexamineuser.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_examine` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_examine; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_examine

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_examine` and checks returned fields, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_examine; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 24 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsexamineuser.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptslistmax.pl -->
# sources/distributed-fs/openafs/src/tests/ptslistmax.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_listmax` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_listmax; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_listmax

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_listmax` and checks returned fields, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_listmax; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 24 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptslistmax.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptslistown.pl -->
# sources/distributed-fs/openafs/src/tests/ptslistown.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_listown` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_listown; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_listown

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_listown` and checks returned fields, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_listown; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 23 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptslistown.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsmembersgroup.pl -->
# sources/distributed-fs/openafs/src/tests/ptsmembersgroup.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_members` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_members, AFS_pts_add, AFS_pts_remove; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_members, AFS_pts_add, AFS_pts_remove

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_remove` and checks returned fields, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_members, AFS_pts_add, AFS_pts_remove; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 35 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsmembersgroup.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsmembersuser.pl -->
# sources/distributed-fs/openafs/src/tests/ptsmembersuser.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_members` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_members, AFS_pts_add, AFS_pts_remove; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_members, AFS_pts_add, AFS_pts_remove

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_remove` and checks returned fields, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_members, AFS_pts_add, AFS_pts_remove; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 35 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsmembersuser.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsremove.pl -->
# sources/distributed-fs/openafs/src/tests/ptsremove.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_remove` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_remove; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_remove

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_remove`, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_remove; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 17 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsremove.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptssetf.pl -->
# sources/distributed-fs/openafs/src/tests/ptssetf.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_setf` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_setf, AFS_pts_examine; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_setf, AFS_pts_examine

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_examine` and checks returned fields, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_setf, AFS_pts_examine; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 28 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptssetf.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptssetmax.pl -->
# sources/distributed-fs/openafs/src/tests/ptssetmax.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_setmax` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_setmax; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_setmax

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_setmax`, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_setmax; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 17 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptssetmax.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/read-vs-mmap.c -->
# sources/distributed-fs/openafs/src/tests/read-vs-mmap.c

## Purpose
Compares mmap-backed access with ordinary file I/O to catch cache coherency or writeback regressions.

## Important APIs, Types, and Functions
functions: generate_file, read_file, mmap_file, do_test, main

## Control Flow
`main` drives the test through helper functions `generate_file, read_file, mmap_file, do_test` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, read, write, mmap, unlink`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
targets mmap/cache coherency and writeback edge cases; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 166 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/read-vs-mmap.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/read-vs-mmap2.c -->
# sources/distributed-fs/openafs/src/tests/read-vs-mmap2.c

## Purpose
Compares mmap-backed access with ordinary file I/O to catch cache coherency or writeback regressions.

## Important APIs, Types, and Functions
functions: generate_random_file, read_file, mmap_file, main

## Control Flow
`main` drives the test through helper functions `generate_random_file, read_file, mmap_file` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, read, write, mmap, unlink`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
targets mmap/cache coherency and writeback edge cases; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 129 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/read-vs-mmap2.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/read-write.c -->
# sources/distributed-fs/openafs/src/tests/read-write.c

## Purpose
Runs a focused C filesystem test with entry points `write_random_file, write_null_file, read_file, main`.

## Important APIs, Types, and Functions
functions: write_random_file, write_null_file, read_file, main

## Control Flow
`main` drives the test through helper functions `write_random_file, write_null_file, read_file` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, read, write, lseek, unlink`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 141 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/read-write.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/readdir-vs-lstat.c -->
# sources/distributed-fs/openafs/src/tests/readdir-vs-lstat.c

## Purpose
Runs a focused C filesystem test with entry points `verify_inodes, usage, main`.

## Important APIs, Types, and Functions
functions: verify_inodes, usage, main

## Control Flow
`main` drives the test through helper functions `verify_inodes, usage` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `stat, lstat, opendir, readdir, chdir`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 97 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/readdir-vs-lstat.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/readfile-wo-create -->
# sources/distributed-fs/openafs/src/tests/readfile-wo-create

## Purpose
Runs a focused shell-level filesystem test built around `test`.

## Important APIs, Types, and Functions
commands: test

## Control Flow
Sequential shell commands run in the harness work directory: `test`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `test`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 3 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/readfile-wo-create -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/reauth.pl -->
# sources/distributed-fs/openafs/src/tests/reauth.pl

## Purpose
Runs a Perl integration test around ``.

## Important APIs, Types, and Functions
No callable API; the file is fixture/template content.

## Control Flow
Loads OpenAFS Perl utility modules, runs ``, and uses explicit `exit(1)` checks where returned data is inspected.

## State and Persistence Behavior
Persists state only through the OpenAFS command wrappers it invokes; most scripts are single-operation integration checks.

## Dependencies and Integration Points
OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 34 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/reauth.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename-under-feet.c -->
# sources/distributed-fs/openafs/src/tests/rename-under-feet.c

## Purpose
Exercises rename semantics, including replacement, rollback, directory moves, or active-directory edge cases.

## Important APIs, Types, and Functions
functions: emkdir, child_sigterm, child_chdir, kill_child, main

## Control Flow
`main` drives the test through helper functions `emkdir, child_sigterm, child_chdir, kill_child` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `close, read, write, stat, lstat, mkdir, rmdir, rename, fork, waitpid`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
detects stale directory entries, wrong inode preservation, or bad rollback; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 161 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename-under-feet.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename1 -->
# sources/distributed-fs/openafs/src/tests/rename1

## Purpose
Exercises rename semantics, including replacement, rollback, directory moves, or active-directory edge cases.

## Important APIs, Types, and Functions
commands: touch, mv, test, rm

## Control Flow
Sequential shell commands run in the harness work directory: `touch, mv, test, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `touch, mv, test, rm`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, touch, test

## Risks and Test Signals
detects stale directory entries, wrong inode preservation, or bad rollback; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 7 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename1 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename2 -->
# sources/distributed-fs/openafs/src/tests/rename2

## Purpose
Exercises rename semantics, including replacement, rollback, directory moves, or active-directory edge cases.

## Important APIs, Types, and Functions
commands: touch, mv, test, rm

## Control Flow
Sequential shell commands run in the harness work directory: `touch, mv, test, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `touch, mv, test, rm`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, touch, test

## Risks and Test Signals
detects stale directory entries, wrong inode preservation, or bad rollback; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 7 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename2 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename3 -->
# sources/distributed-fs/openafs/src/tests/rename3

## Purpose
Exercises rename semantics, including replacement, rollback, directory moves, or active-directory edge cases.

## Important APIs, Types, and Functions
commands: echo, sed, rm, test, mv

## Control Flow
Sequential shell commands run in the harness work directory: `echo, sed, rm, test, mv`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `echo, sed, rm, test, mv`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, test

## Risks and Test Signals
detects stale directory entries, wrong inode preservation, or bad rollback; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 9 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename3 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename4 -->
# sources/distributed-fs/openafs/src/tests/rename4

## Purpose
Exercises rename semantics, including replacement, rollback, directory moves, or active-directory edge cases.

## Important APIs, Types, and Functions
commands: mkdir, mv, test, rmdir

## Control Flow
Sequential shell commands run in the harness work directory: `mkdir, mv, test, rmdir`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir, rmdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, rmdir, test

## Risks and Test Signals
detects stale directory entries, wrong inode preservation, or bad rollback; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 9 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename4 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename5.c -->
# sources/distributed-fs/openafs/src/tests/rename5.c

## Purpose
Exercises rename semantics, including replacement, rollback, directory moves, or active-directory edge cases.

## Important APIs, Types, and Functions
functions: emkdir, elstat, check_inum, main

## Control Flow
`main` drives the test through helper functions `emkdir, elstat, check_inum` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `stat, lstat, mkdir, rename`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
detects stale directory entries, wrong inode preservation, or bad rollback; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 104 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename5.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename6.c -->
# sources/distributed-fs/openafs/src/tests/rename6.c

## Purpose
Exercises rename semantics, including replacement, rollback, directory moves, or active-directory edge cases.

## Important APIs, Types, and Functions
functions: main

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, unlink, rename`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
detects stale directory entries, wrong inode preservation, or bad rollback; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 71 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename6.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rewrite-emacs -->
# sources/distributed-fs/openafs/src/tests/rewrite-emacs

## Purpose
Runs a focused shell-level filesystem test built around `then, gzip, tar, find`.

## Important APIs, Types, and Functions
commands: then, gzip, tar, find, xargs, $objdir/truncate-files

## Control Flow
Sequential shell commands run in the harness work directory: `then, gzip, tar, find, xargs, $objdir/truncate-files`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `chmod`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, find, xargs, tar, gzip, chmod, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 10 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rewrite-emacs -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rm-rf.c -->
# sources/distributed-fs/openafs/src/tests/rm-rf.c

## Purpose
Runs a focused C filesystem test with entry points `kill_one, do_dir, kill_dir, main`.

## Important APIs, Types, and Functions
functions: kill_one, do_dir, kill_dir, main; AFS calls/macros: fs_lib, fs_rmmount

## Control Flow
`main` drives the test through helper functions `kill_one, do_dir, kill_dir` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `rmdir, opendir, readdir, unlink, chdir, fs_rmmount`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting; AFS interfaces fs_lib, fs_rmmount

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 125 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rm-rf.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/run-fsx -->
# sources/distributed-fs/openafs/src/tests/run-fsx

## Purpose
Runs a focused shell-level filesystem test built around `then, ${objdir}/fsx`.

## Important APIs, Types, and Functions
commands: then, ${objdir}/fsx

## Control Flow
Sequential shell commands run in the harness work directory: `then, ${objdir}/fsx`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, ${objdir}/fsx`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 7 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/run-fsx -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/run-rcs -->
# sources/distributed-fs/openafs/src/tests/run-rcs

## Purpose
Runs a focused shell-level filesystem test built around `echo, ci, co, wc`.

## Important APIs, Types, and Functions
commands: echo, ci, co, wc, grep

## Control Flow
Sequential shell commands run in the harness work directory: `echo, ci, co, wc, grep`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `echo, ci, co, wc, grep`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands ci

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 11 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/run-rcs -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/run-suite.pl -->
# sources/distributed-fs/openafs/src/tests/run-suite.pl

## Purpose
Bootstraps an end-to-end local OpenAFS test cell, starts server/client services, creates volumes and mount points, then runs the front-end test harness.

## Important APIs, Types, and Functions
Perl calls/subs: mkvol, uudecode

## Control Flow
Requires root, rejects already-running AFS mounts, stops/starts services, writes ThisCell/CellServDB, seeds the protection database, creates bos/vl/pt/ka/fileserver instances, creates root/user/service/replicated volumes, authenticates, runs `pagsh -c './test-front.sh ...'`, and unwinds registered cleanup commands.

## State and Persistence Behavior
Mutates system-wide AFS configuration, databases, volumes, `/afs`, `/usr/vice/cache`, test dumps, and service state; cleanup is managed through an unwind stack and END block.

## Dependencies and Integration Points
OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
Destructive and environment-sensitive; requires root, a valid KeyFile, available partitions, service paths from Dirpath, and careful cleanup to avoid leaving partial cells or running services.

## Source Notes
Read as Perl OpenAFS command test; 302 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/run-suite.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/run-tests.in -->
# sources/distributed-fs/openafs/src/tests/run-tests.in

## Purpose
Main shell harness that selects OpenAFS test categories, establishes the work directory and authentication, executes each test in an isolated per-test directory, and reports failures.

## Important APIs, Types, and Functions
AFS calls/macros: AFS_TESTS, setpag; commands: ., echo, mkdir1, mkdir2, symlink, hardlink1, hardlink4, hardlink2, hardlink5, touch1

## Control Flow
Loads build-time Dirpath.sh and run-tests.conf, defines category lists, parses flags such as `-basic`, `-mmap`, `-pts`, `-vos`, `-fast`, `-large`, `-j`, and `-user`, resolves each test as source script or built binary, optionally runs through `asu`, and removes successful temp directories.

## State and Persistence Behavior
Creates per-test directories under `$AFSROOT/$CELLNAME/$TESTDIR`, exports srcdir/objdir/FAST/LARGE/verbosity state, can authenticate with `kinit`/`aklog`, and leaves failed directories for inspection.

## Dependencies and Integration Points
AFS interfaces AFS_TESTS, setpag; harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, hostname, test, fs, vos, pts, bos, kinit

## Risks and Test Signals
Harness correctness depends on build substitutions, configuration files, AFS credentials, and the `savedres` typo in one assignment is suspicious though the final failure path forces exitval to 1.

## Source Notes
Read as POSIX shell test; 462 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/run-tests.in -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/setgroups -->
# sources/distributed-fs/openafs/src/tests/setgroups

## Purpose
Runs a focused shell-level filesystem test built around `$objdir/test-setgroups`.

## Important APIs, Types, and Functions
commands: $objdir/test-setgroups

## Control Flow
Sequential shell commands run in the harness work directory: `$objdir/test-setgroups`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `$objdir/test-setgroups`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 4 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/setgroups -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/setpag -->
# sources/distributed-fs/openafs/src/tests/setpag

## Purpose
Runs a focused shell-level filesystem test built around `$objdir/test-setpag`.

## Important APIs, Types, and Functions
AFS calls/macros: setpag; commands: $objdir/test-setpag

## Control Flow
Sequential shell commands run in the harness work directory: `$objdir/test-setpag`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `$objdir/test-setpag`.

## Dependencies and Integration Points
AFS interfaces setpag; harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 4 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/setpag -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/shallow-tree -->
# sources/distributed-fs/openafs/src/tests/shallow-tree

## Purpose
Runs a focused shell-level filesystem test built around `mkdir, , $SHELL, ${objdir}/rm-rf`.

## Important APIs, Types, and Functions
commands: mkdir, , $SHELL, ${objdir}/rm-rf

## Control Flow
Sequential shell commands run in the harness work directory: `mkdir, , $SHELL, ${objdir}/rm-rf`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 5 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/shallow-tree -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/still-there-p.c -->
# sources/distributed-fs/openafs/src/tests/still-there-p.c

## Purpose
Runs a focused C filesystem test with entry points `main`.

## Important APIs, Types, and Functions
functions: main

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, read, write, lseek, stat, fstat`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 88 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/still-there-p.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/strange-characters -->
# sources/distributed-fs/openafs/src/tests/strange-characters

## Purpose
Runs a focused shell-level filesystem test built around `touch, test, rm`.

## Important APIs, Types, and Functions
commands: touch, test, rm

## Control Flow
Sequential shell commands run in the harness work directory: `touch, test, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `touch, test, rm`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, touch, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 7 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/strange-characters -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/strange-characters-c.c -->
# sources/distributed-fs/openafs/src/tests/strange-characters-c.c

## Purpose
Runs a focused C filesystem test with entry points `creat_file, look_at_file, usage, main`.

## Important APIs, Types, and Functions
functions: creat_file, look_at_file, usage, main

## Control Flow
`main` drives the test through helper functions `creat_file, look_at_file, usage` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 88 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/strange-characters-c.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/strange-other-characters -->
# sources/distributed-fs/openafs/src/tests/strange-other-characters

## Purpose
Runs a focused shell-level filesystem test built around `test`.

## Important APIs, Types, and Functions
commands: test

## Control Flow
Sequential shell commands run in the harness work directory: `test`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `test`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 5 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/strange-other-characters -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/symlink.c -->
# sources/distributed-fs/openafs/src/tests/symlink.c

## Purpose
Runs a focused C filesystem test with entry points `main`.

## Important APIs, Types, and Functions
functions: main

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `stat, lstat, unlink, symlink`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 67 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/symlink.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-front.sh -->
# sources/distributed-fs/openafs/src/tests/test-front.sh

## Purpose
Runs a focused shell-level filesystem test built around `./reauth.pl, ./run-tests`.

## Important APIs, Types, and Functions
commands: ./reauth.pl, ./run-tests

## Control Flow
Sequential shell commands run in the harness work directory: `./reauth.pl, ./run-tests`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `./reauth.pl, ./run-tests`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 10 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-front.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-gunzip-gnu-mirror -->
# sources/distributed-fs/openafs/src/tests/test-gunzip-gnu-mirror

## Purpose
Runs a focused shell-level filesystem test built around `then, cd, find, echo`.

## Important APIs, Types, and Functions
commands: then, cd, find, echo, *not*in*gzip*format*, *OK*, *

## Control Flow
Sequential shell commands run in the harness work directory: `then, cd, find, echo, *not*in*gzip*format*, *OK*, *`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `read`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands find, gzip, gunzip, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 14 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-gunzip-gnu-mirror -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-parallel1.c -->
# sources/distributed-fs/openafs/src/tests/test-parallel1.c

## Purpose
Runs a focused C filesystem test with entry points `worker, main`.

## Important APIs, Types, and Functions
functions: worker, main

## Control Flow
`main` drives the test through helper functions `worker` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, fchmod, unlink, fork`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 96 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-parallel1.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-parallel2.c -->
# sources/distributed-fs/openafs/src/tests/test-parallel2.c

## Purpose
Runs a focused C filesystem test with entry points `getcwd_worker, mkdir_worker, mkdir_rmdir_worker, rename_worker, stat_worker`.

## Important APIs, Types, and Functions
functions: getcwd_worker, mkdir_worker, mkdir_rmdir_worker, rename_worker, stat_worker, main

## Control Flow
`main` drives the test through helper functions `getcwd_worker, mkdir_worker, mkdir_rmdir_worker, rename_worker, stat_worker` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, stat, mkdir, rmdir, rename, fork, chdir`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 181 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-parallel2.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-setgroups.c -->
# sources/distributed-fs/openafs/src/tests/test-setgroups.c

## Purpose
Runs a focused C filesystem test with entry points `print_groups, main`.

## Important APIs, Types, and Functions
functions: print_groups, main; AFS calls/macros: setpag

## Control Flow
`main` drives the test through helper functions `print_groups` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `getgroups, setpag`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting; AFS interfaces setpag

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 123 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-setgroups.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-setpag.c -->
# sources/distributed-fs/openafs/src/tests/test-setpag.c

## Purpose
Runs a focused C filesystem test with entry points `print_groups, main`.

## Important APIs, Types, and Functions
functions: print_groups, main; AFS calls/macros: setpag

## Control Flow
`main` drives the test through helper functions `print_groups` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `fork, waitpid, getgroups, setpag`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting; AFS interfaces setpag

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 113 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-setpag.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/too-many-files -->
# sources/distributed-fs/openafs/src/tests/too-many-files

## Purpose
Runs a focused shell-level filesystem test built around `then, $objdir/create-files`.

## Important APIs, Types, and Functions
commands: then, $objdir/create-files

## Control Flow
Sequential shell commands run in the harness work directory: `then, $objdir/create-files`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, $objdir/create-files`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 5 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/too-many-files -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/touch1 -->
# sources/distributed-fs/openafs/src/tests/touch1

## Purpose
Runs a focused shell-level filesystem test built around `touch, test, rm`.

## Important APIs, Types, and Functions
commands: touch, test, rm

## Control Flow
Sequential shell commands run in the harness work directory: `touch, test, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `touch, test, rm`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, touch, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 4 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/touch1 -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/truncate-files.c -->
# sources/distributed-fs/openafs/src/tests/truncate-files.c

## Purpose
Runs a focused C filesystem test with entry points `do_dir, read_and_truncate, repeat_dir, main`.

## Important APIs, Types, and Functions
functions: do_dir, read_and_truncate, repeat_dir, main

## Control Flow
`main` drives the test through helper functions `do_dir, read_and_truncate, repeat_dir` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, read, write, stat, lstat, opendir, readdir, chdir`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 141 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/truncate-files.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/truncate.c -->
# sources/distributed-fs/openafs/src/tests/truncate.c

## Purpose
Runs a focused C filesystem test with entry points `create_and_write, check_size, main`.

## Important APIs, Types, and Functions
functions: create_and_write, check_size, main

## Control Flow
`main` drives the test through helper functions `create_and_write, check_size` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, write, stat, truncate, unlink`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 107 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/truncate.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/untar-emacs -->
# sources/distributed-fs/openafs/src/tests/untar-emacs

## Purpose
Runs a focused shell-level filesystem test built around `then, $objdir/echo-n, gzip, tar`.

## Important APIs, Types, and Functions
commands: then, $objdir/echo-n, gzip, tar, rm, echo

## Control Flow
Sequential shell commands run in the harness work directory: `then, $objdir/echo-n, gzip, tar, rm, echo`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, $objdir/echo-n, gzip, tar, rm, echo`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, tar, gzip, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 9 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/untar-emacs -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/untar-openafs -->
# sources/distributed-fs/openafs/src/tests/untar-openafs

## Purpose
Runs a focused shell-level filesystem test built around `then, wget, $objdir/echo-n, gzip`.

## Important APIs, Types, and Functions
commands: then, wget, $objdir/echo-n, gzip, tar, rm, echo

## Control Flow
Sequential shell commands run in the harness work directory: `then, wget, $objdir/echo-n, gzip, tar, rm, echo`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, wget, $objdir/echo-n, gzip, tar, rm`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, tar, gzip, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 10 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/untar-openafs -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/utime-dir.c -->
# sources/distributed-fs/openafs/src/tests/utime-dir.c

## Purpose
Runs a focused C filesystem test with entry points `doit, main`.

## Important APIs, Types, and Functions
functions: doit, main

## Control Flow
`main` drives the test through helper functions `doit` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `mkdir`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 76 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/utime-dir.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/utime-file.c -->
# sources/distributed-fs/openafs/src/tests/utime-file.c

## Purpose
Runs a focused C filesystem test with entry points `main`.

## Important APIs, Types, and Functions
functions: main

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, write, lseek, stat, fstat, utime, ftruncate`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 97 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/utime-file.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/verr.c -->
# sources/distributed-fs/openafs/src/tests/verr.c

## Purpose
Implements or declares BSD-style `err(3)`/`warn(3)` compatibility helpers for the test programs.

## Important APIs, Types, and Functions
functions: verr

## Control Flow
`main` drives the test through helper functions `verr` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls ``; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 44 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/verr.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/verrx.c -->
# sources/distributed-fs/openafs/src/tests/verrx.c

## Purpose
Implements or declares BSD-style `err(3)`/`warn(3)` compatibility helpers for the test programs.

## Important APIs, Types, and Functions
functions: verrx

## Control Flow
`main` drives the test through helper functions `verrx` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls ``; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 44 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/verrx.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/visit-volumes -->
# sources/distributed-fs/openafs/src/tests/visit-volumes

## Purpose
Runs a focused shell-level filesystem test built around `ls`.

## Important APIs, Types, and Functions
commands: ls

## Control Flow
Sequential shell commands run in the harness work directory: `ls`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `ls`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 6 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/visit-volumes -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosaddsite.pl -->
# sources/distributed-fs/openafs/src/tests/vosaddsite.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_addsite` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_addsite; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_addsite

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_addsite`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_addsite; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosaddsite.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosbackup.pl -->
# sources/distributed-fs/openafs/src/tests/vosbackup.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_backup` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_backup; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_backup

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_backup`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_backup; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosbackup.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/voscreate.pl -->
# sources/distributed-fs/openafs/src/tests/voscreate.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_create` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_create; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_create

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_create`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_create; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 20 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/voscreate.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosdelentry.pl -->
# sources/distributed-fs/openafs/src/tests/vosdelentry.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_delentry` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_delentry; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_delentry

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_delentry`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_delentry; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosdelentry.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosdump.pl -->
# sources/distributed-fs/openafs/src/tests/vosdump.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_dump` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_dump; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_dump

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_dump`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_dump; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
uses `/tmp` scratch files; requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosdump.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosexamine.pl -->
# sources/distributed-fs/openafs/src/tests/vosexamine.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_examine` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_examine; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_examine

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_examine` and validates returned volume/partition fields, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_examine; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 32 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosexamine.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/voslistpart.pl -->
# sources/distributed-fs/openafs/src/tests/voslistpart.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_listpart` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_listpart; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_listpart

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_listpart` and validates returned volume/partition fields, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_listpart; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 26 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/voslistpart.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/voslistvldb.pl -->
# sources/distributed-fs/openafs/src/tests/voslistvldb.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_listvldb` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_listvldb; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_listvldb

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_listvldb` and validates returned volume/partition fields, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_listvldb; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 24 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/voslistvldb.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/voslistvol.pl -->
# sources/distributed-fs/openafs/src/tests/voslistvol.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_listvol` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_listvol; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_listvol

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_listvol` and validates returned volume/partition fields, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_listvol; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 24 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/voslistvol.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/voslock.pl -->
# sources/distributed-fs/openafs/src/tests/voslock.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_lock` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_lock; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_lock

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_lock`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_lock; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/voslock.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosmove.pl -->
# sources/distributed-fs/openafs/src/tests/vosmove.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_move` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_move; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_move

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_move`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_move; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosmove.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vospartinfo.pl -->
# sources/distributed-fs/openafs/src/tests/vospartinfo.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_partinfo` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_partinfo; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_partinfo

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_partinfo`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_partinfo; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vospartinfo.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosrelease.pl -->
# sources/distributed-fs/openafs/src/tests/vosrelease.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_release` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_release; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_release

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_release`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_release; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosrelease.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosremove.pl -->
# sources/distributed-fs/openafs/src/tests/vosremove.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_remove` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_remove; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_remove

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_remove`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_remove; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosremove.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosremsite.pl -->
# sources/distributed-fs/openafs/src/tests/vosremsite.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_remsite` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_remsite; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_remsite

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_remsite`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_remsite; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosremsite.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosrename.pl -->
# sources/distributed-fs/openafs/src/tests/vosrename.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_rename` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_rename; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_rename

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_rename`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_rename; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; detects stale directory entries, wrong inode preservation, or bad rollback; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosrename.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosrestore.pl -->
# sources/distributed-fs/openafs/src/tests/vosrestore.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_restore` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_restore; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_restore

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_restore`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_restore; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
uses `/tmp` scratch files; requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosrestore.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vossyncserv.pl -->
# sources/distributed-fs/openafs/src/tests/vossyncserv.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_syncserv` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_syncserv; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_syncserv

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_syncserv`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_syncserv; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vossyncserv.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vossyncvldb.pl -->
# sources/distributed-fs/openafs/src/tests/vossyncvldb.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_syncvldb` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_syncvldb; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_syncvldb

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_syncvldb`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_syncvldb; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vossyncvldb.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosunlock.pl -->
# sources/distributed-fs/openafs/src/tests/vosunlock.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_unlock` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_unlock; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_unlock

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_unlock`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_unlock; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosunlock.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosunlockall.pl -->
# sources/distributed-fs/openafs/src/tests/vosunlockall.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_lock` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_lock, AFS_vos_unlockvldb; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_lock, AFS_vos_unlockvldb

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_unlockvldb`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_lock, AFS_vos_unlockvldb; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 21 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosunlockall.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/voszap.pl -->
# sources/distributed-fs/openafs/src/tests/voszap.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_zap` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_zap; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_zap

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_zap`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_zap; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/voszap.pl -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vwarn.c -->
# sources/distributed-fs/openafs/src/tests/vwarn.c

## Purpose
Implements or declares BSD-style `err(3)`/`warn(3)` compatibility helpers for the test programs.

## Important APIs, Types, and Functions
functions: vwarn

## Control Flow
`main` drives the test through helper functions `vwarn` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls ``; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 43 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vwarn.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vwarnx.c -->
# sources/distributed-fs/openafs/src/tests/vwarnx.c

## Purpose
Implements or declares BSD-style `err(3)`/`warn(3)` compatibility helpers for the test programs.

## Important APIs, Types, and Functions
functions: vwarnx

## Control Flow
`main` drives the test through helper functions `vwarnx` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls ``; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 43 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vwarnx.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/warn.c -->
# sources/distributed-fs/openafs/src/tests/warn.c

## Purpose
Implements or declares BSD-style `err(3)`/`warn(3)` compatibility helpers for the test programs.

## Important APIs, Types, and Functions
functions: warn

## Control Flow
`main` drives the test through helper functions `warn` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls ``; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 46 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/warn.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/warnerr.c -->
# sources/distributed-fs/openafs/src/tests/warnerr.c

## Purpose
Implements or declares BSD-style `err(3)`/`warn(3)` compatibility helpers for the test programs.

## Important APIs, Types, and Functions
functions: getprogname, setprogname, set_progname, get_progname, warnerr

## Control Flow
`main` drives the test through helper functions `getprogname, setprogname, set_progname, get_progname, warnerr` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls ``; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 100 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/warnerr.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/warnx.c -->
# sources/distributed-fs/openafs/src/tests/warnx.c

## Purpose
Implements or declares BSD-style `err(3)`/`warn(3)` compatibility helpers for the test programs.

## Important APIs, Types, and Functions
functions: warnx

## Control Flow
`main` drives the test through helper functions `warnx` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls ``; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 46 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/warnx.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write-closed.c -->
# sources/distributed-fs/openafs/src/tests/write-closed.c

## Purpose
Runs a focused C filesystem test with entry points `doit, main`.

## Important APIs, Types, and Functions
functions: doit, main

## Control Flow
`main` drives the test through helper functions `doit` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, fchmod, ftruncate, mmap, munmap`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
targets mmap/cache coherency and writeback edge cases; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 94 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write-closed.c -->
