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
