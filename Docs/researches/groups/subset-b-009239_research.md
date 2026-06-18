# subset-b-009239 Research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/iozone/src/current/fileop.c -->
# sources/test-tools/iozone/src/current/fileop.c

## Purpose

`fileop.c` is the standalone `fileop` metadata benchmark shipped with iozone. It creates a deterministic filesystem tree, times common directory and file operations, prints throughput in operations per second, then removes the generated tree. The force factor `x` controls scale: the benchmark works over `x` first-level directories, `x` second-level directories per first-level directory, and `x` files or leaf directories per second-level directory. This makes the file workload `x^3` files and the directory-create/delete workload include all three directory levels.

The command-line interface supports a single force factor with `-f`, a range with `-l`, `-u`, and `-i`, file size with `-s`, output shape with `-t`, `-e`, `-b`, and `-w`, working directory selection with `-d`, and optional cache-disruption remounts with `-U`.

## Important APIs, Types, and Global State

- `struct stat_struct` stores timing and count data for each operation class: `starttime`, `endtime`, last `speed`, `best`, `worst`, `total_time`, and `counter`.
- `stats[_NUM_STATS]` is a global volatile array indexed by `_STAT_*` constants for create, write, close, link, unlink, delete, stat, access, chmod, readdir, directory create/delete/traverse, read, and open.
- `time_so_far()` abstracts platform timing. It uses `QueryPerformanceCounter()` on Windows, `getclock(TIMEOFDAY, ...)` on older OSF platforms, and `gettimeofday()` otherwise.
- `thedir` is the benchmark root, defaulting to `"."`; `main()` changes into it before running tests.
- `mountname` is set by `-U` and used by `purge_buffer_cache()` to issue shell `umount` and `mount` commands between tests.
- `sz` is the per-file byte count. `-s` accepts raw bytes plus `K`/`M` suffixes.
- `mbuffer` is heap allocated to `sz` bytes and reused for writes and reads.
- `best`, `worst`, `excel`, and `verbose` control result formatting.

The file uses legacy C style throughout: global mutable variables, implicit-style forward declarations such as `void bzero();`, direct `sprintf()` into fixed 100-byte local path buffers, and `junk`/`junkp` assignments to consume ignored return values.

## Control Flow

`main()` first requires at least one argument. It parses options with `getopt(argc, argv, "hbwetvf:s:l:u:d:U:i: ")`, initializes `mbuffer`, prints the non-verbose header, and `chdir()`s into `thedir`. If no range was supplied, `lower` and `upper` are both set to `x`; if `x` was never provided, it defaults to 1.

For each force factor from `lower` to `upper` stepping by `incr`, `main()` clears all counters and runs this sequence:

1. `purge_buffer_cache(); dir_create(x);`
2. `purge_buffer_cache(); dir_traverse(x);`
3. `purge_buffer_cache(); dir_delete(x);`
4. `purge_buffer_cache(); file_create(x);`
5. `purge_buffer_cache(); file_stat(x);`
6. `purge_buffer_cache(); file_read(x);`
7. `purge_buffer_cache(); file_access(x);`
8. `purge_buffer_cache(); file_chmod(x);`
9. `purge_buffer_cache(); file_readdir(x);`
10. Non-Windows only: `file_link(x)` and `file_unlink(x)`.
11. `purge_buffer_cache(); file_delete(x);`

Verbose mode prints a detailed block after each operation class with total time, average operations per second, best operation time, and worst operation time. Non-verbose mode prints one compact row of average operation rates, with optional best (`-b`) and worst (`-w`) rows. On Windows, link and unlink columns are omitted.

## Filesystem Operations

`dir_create(int x)` builds directories named `fileop_L1_i`, `fileop_L1_i_L2_j`, and `fileop_dir_i_j_k`. Each `mkdir()` is individually timed. The function repeatedly `chdir()`s into and out of generated directories to keep path strings short.

`dir_traverse(int x)` walks the already-created directory tree using `chdir()` and times entry/exit operations. It folds the measured time to enter parent directories into the per-directory timing for the later return operation.

`dir_delete(int x)` removes the directory-only tree created by `dir_create()`. It times `rmdir()` calls for leaf, second-level, and first-level directories, but it does not check `rmdir()` return values.

`file_create(int x)` creates a fresh directory tree for the file tests, writes one file per second-level directory slot, flushes with `fsync(fd)`, and closes. It times `creat()`, `write()`, and `close()` separately. File data is a repeated byte derived from `(i ^ j ^ k) & 0xff`, allowing later read validation.

`file_stat(int x)` stats each generated file and exits on stat failure.

`file_read(int x)` opens each generated file, reads `sz` bytes into `mbuffer`, validates the repeated-byte pattern with `validate()`, and tracks open/read timings separately. A validation mismatch only prints an error and does not fail the benchmark.

`file_access(int x)` checks `W_OK|F_OK` for each file.

`file_chmod(int x)` changes each file to mode `0666`.

`file_readdir(int x)` opens each second-level directory, times one `readdir()` call, and closes it. This measures a single directory-entry lookup rather than enumerating the complete directory.

`file_link(int x)` creates hard links named with an `L` suffix for each file. `file_unlink(int x)` removes those hard links. These operations are excluded at compile time on Windows.

`file_delete(int x)` unlinks each generated file and removes the directories around them. Like `dir_delete()`, it does not validate deletion return codes.

## State and Persistence Behavior

The benchmark intentionally mutates the selected working directory. It creates names with fixed `fileop_` prefixes and expects to own those paths for the duration of the run. On normal completion it removes the generated file and directory trees. On failure it usually calls `exit(1)` immediately, leaving any already-created paths behind for manual cleanup.

`purge_buffer_cache()` is the only routine that reaches outside the working tree. When `-U` is supplied, it saves the current directory, changes to `/`, executes `umount <mountname>` with retry sleeps from 1 to 9 seconds, then executes `mount <mountname>` and returns to the saved directory. This behavior depends on system mount configuration and process privileges.

All benchmark counters live in process memory and are reset by `clear_stats()` at each force factor. The only persistent outputs are stdout/stderr text and filesystem side effects in the target directory.

## Dependencies and Integration Points

The implementation depends on POSIX filesystem and process APIs: `mkdir`, `rmdir`, `chdir`, `creat`, `open`, `write`, `read`, `close`, `fsync`, `stat`, `access`, `chmod`, `opendir`, `readdir`, `closedir`, `link`, `unlink`, `gettimeofday`, `getopt`, `sleep`, and `system`. Windows builds include `Windows.h` and switch timing to high-performance counters while skipping hard-link tests.

Within the iozone tree, this file integrates as an auxiliary benchmark executable rather than as a library module. Its output can be consumed by scripts or spreadsheets; the compact header labels and `-e`/best/worst flags are its stable external interface.

## Risks and Edge Cases

- Path and command construction uses unchecked `strcpy`, `strcat`, and `sprintf()` into fixed buffers. `mountname`, generated names, or future naming changes can overflow local buffers.
- `-d` uses `strncpy(thedir, optarg, dirlen)` without bounding `dirlen` to `PATH_MAX - 1`.
- `purge_buffer_cache()` passes user-controlled mount text to `system()` without quoting, creating command injection risk if `-U` is exposed to untrusted input.
- Many `chdir()`, `rmdir()`, `unlink()`, `write()`, `fsync()`, `close()`, and `system()` results are ignored. Failures can skew measurements or leave state behind.
- `creat(buf, O_RDWR|0600)` passes flag bits in the mode argument. Because `creat()` is equivalent to `open(..., O_CREAT|O_WRONLY|O_TRUNC, mode)`, this does not request read/write access; it creates files with a mode that happens to include permission bits from `0600`.
- Timings use wall-clock time on non-Windows platforms, so clock adjustments can produce negative durations. The code clamps negative operation times to zero, which can lead to divide-by-zero or inflated rates.
- `malloc(sz)` is not checked before `memset()`. Large or invalid `-s` inputs can crash.
- Force-factor multiplication `x*x*x` uses `int` arithmetic for display and can overflow. Large `x` values also create massive filesystem side effects.
- Best/worst reporting divides by `best` or `worst`; zero-duration operations can print infinities or implementation-defined floating output.
- The benchmark assumes no preexisting `fileop_*` paths in the target directory. Collisions cause early exits or cleanup of paths the user did not intend to target.

## Test Signals

Useful test coverage would compile the program on POSIX and, where supported, Windows. Behavioral smoke tests should run in a temporary directory with a small force factor such as `-f 1 -s 1`, assert exit status 0, verify expected output columns, and confirm no `fileop_*` entries remain. Range behavior can be tested with `-l 1 -u 2 -i 1`. Verbose, best, worst, and `-v` output are simple output-shape checks.

Fault-oriented tests should run in an unwritable directory, with preexisting colliding `fileop_*` paths, and with invalid or very large `-s`, `-d`, and `-U` values. The `-U` path should be tested only in an isolated environment because it can unmount filesystems. Data validation is signaled by the literal `Error: Data Mis-compare` line rather than process failure.
<!-- END_FILE_RESEARCH: sources/test-tools/iozone/src/current/fileop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/iozone/src/current/gengnuplot.sh -->
# sources/test-tools/iozone/src/current/gengnuplot.sh

## Purpose

`gengnuplot.sh` is a small helper that converts `iozone -a` tabular output into a three-column data file suitable for gnuplot. It copies the supplied iozone output into a fixed working file named `iozone_gen_out`, selects one benchmark column based on the requested test name, and writes `record_size file_size selected_metric` rows into a per-test directory.

The script expects exactly two arguments:

- `$1`: an iozone auto-mode output file.
- `$2`: a test selector such as `write`, `rewrite`, `read`, `reread`, `randread`, `randwrite`, `bkwdread`, `recrewrite`, `strideread`, `fwrite`, `frewrite`, `fread`, or `freread`.

## Important APIs and Functions

The only defined function is `write_gnuplot_file()`. It echoes a comment identifying the selected test, then uses a `case` statement over global variable `query`.

Each supported case runs `awk '$1 ~ /^[0-9]+/ { print $1 " " $2 " " $N }' < $file_name`, where `$N` maps to the iozone result column:

- `write` -> column 3.
- `rewrite` -> column 4.
- `read` -> column 5.
- `reread` -> column 6.
- `randread` -> column 7.
- `randwrite` -> column 8.
- `bkwdread` -> column 9.
- `recrewrite` -> column 10.
- `strideread` -> column 11.
- `fwrite` -> column 12.
- `frewrite` -> column 13.
- `fread` -> column 14.
- `freread` -> column 15.

The numeric-row filter skips headers and comments by requiring the first field to begin with a digit.

## Control Flow

At startup, the script runs `cp $1 iozone_gen_out`, sets `file_name=iozone_gen_out`, sets `filename=iozone_gen_out` even though `filename` is not subsequently used, and assigns `query=$2`.

It then runs `if (! [ -e $query ] ) ; then mkdir $query; fi`, creating a directory named after the requested test when no filesystem entry of that name exists. If exactly two arguments are present, it redirects `write_gnuplot_file` output to `$query/$(basename $file_name.gnuplot)`, which resolves to `$query/iozone_gen_out.gnuplot`. Otherwise it prints usage text.

Unsupported test names are handled inside `write_gnuplot_file()` by writing usage text to stderr, but the outer control flow still creates the output directory and output file for the unsupported name.

## State and Persistence Behavior

The script always overwrites or creates `iozone_gen_out` in the current working directory before validating the argument count. It also creates a directory whose name is exactly `$2`, and it writes or truncates `$2/iozone_gen_out.gnuplot` when two arguments are present. Output names are fixed, so repeated runs overwrite the previous copied input and gnuplot data for the same test.

There is no cleanup of the copied `iozone_gen_out` file. The generated files are relative to the caller's current directory, not relative to the source file or input file.

## Dependencies and Integration Points

The script depends on `/bin/sh`, `cp`, `mkdir`, `basename`, and `awk`. It is coupled to the classic iozone `-a` report column order and to gnuplot-style three-column data files. It does not invoke gnuplot itself; it only prepares data files for later plotting.

Its integration point is manual or scripted post-processing after an iozone benchmark run. A caller would run one invocation per desired metric and then point gnuplot at the resulting `iozone_gen_out.gnuplot` files.

## Risks and Edge Cases

- Arguments are unquoted throughout. Input paths, test names, glob characters, whitespace, and leading dashes can break commands or change behavior.
- `cp $1 iozone_gen_out` executes before checking `$#`, so missing arguments produce a `cp` error before the usage text.
- The directory creation test checks `-e $query`; if a non-directory file already exists with the test name, redirection to `$query/iozone_gen_out.gnuplot` fails.
- The script accepts arbitrary `$2` values as path names. A selector like `../out` writes outside the current directory; shell metacharacters can also be dangerous because the value is unquoted.
- The `if (! [ -e $query ] )` syntax is non-idiomatic and may not be portable to all `/bin/sh` implementations even though it works in common shells.
- Unsupported test names still create an output file containing only the `#test` line plus stderr usage output elsewhere, which can look like a successful data generation to weak callers.
- Fixed temporary/output file names make concurrent runs in the same directory race with each other.

## Test Signals

Smoke tests should create a tiny representative iozone table with one numeric row and invoke the script for each supported selector, then assert that the third output column matches the expected input column. Usage behavior should be checked for zero, one, and three arguments.

Edge tests should cover input paths with spaces, unsupported selectors, preexisting non-directory selector names, selector names containing slashes, and concurrent invocations in the same working directory. Since the output file is deterministic (`<selector>/iozone_gen_out.gnuplot`), tests can assert exact output content for known input.
<!-- END_FILE_RESEARCH: sources/test-tools/iozone/src/current/gengnuplot.sh -->
