# subset-b-008562 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/gnu_parallel -->
# sources/storage-engines/rocksdb/build_tools/gnu_parallel

## Purpose
This file is a vendored Perl copy of GNU Parallel 20141122, with RocksDB-specific behavior in its progress loop: when CI-style progress output has not advanced for about five minutes, it runs `build_tools/ps_with_stack` from the script directory, falling back to `ps -wwf`. RocksDB uses it from the top-level `Makefile` to run generated test commands in parallel with `--joblog=LOG`, `--eta`, `--plain`, and `--tmpdir=$(TEST_TMPDIR)`. Keeping the tool vendored makes parallel test scheduling available even when GNU Parallel is not installed system-wide, while letting RocksDB modify hang diagnostics.

## Important APIs, types, and functions
The script is executable Perl and uses `IPC::Open3`, `POSIX`, `Symbol`, `File::Temp`, `File::Path`, `Getopt::Long`, and `File::Basename`. It is organized as top-level orchestration plus several package-style classes.

`parse_options`, `options_hash`, `read_options`, `read_args_from_command_line`, `open_joblog`, `parse_env_var`, and `find_compression_program` establish global option state in `opt::` and `Global::`. They support normal GNU Parallel features such as `-j/--jobs`, `--joblog`, `--resume`, `--results`, `--pipe`, `--pipepart`, `--sshlogin`, `--return`, `--transfer`, `--halt`, `--timeout`, `--eta`, `--bar`, `--colsep`, xargs compatibility flags, semaphore mode, profiles, and `$PARALLEL`.

`JobQueue`, `CommandLineQueue`, `CommandLine`, `RecordQueue`, `RecordColQueue`, `MultifileQueue`, and `Arg` form the input and command construction pipeline. `CommandLineQueue->new` rewrites replacement strings such as `{}`, `{#}`, `{%}`, `{/}`, `{/.}`, positional variants, and `{= perl code =}` into internal markers. `CommandLine->populate`, `len`, `replace_placeholders`, and `Arg->replace` decide how many records fit under command-line length limits and produce the final shell command.

`SSHLogin` models each local or remote execution target. It tracks job counts, CPU/core discovery, load and swap probes, host groups, SSH command parsing, ControlMaster path setup, rsync transfer commands, remote cleanup commands, and per-host process limits. `remote_hosts`, `read_sshloginfiles`, `parse_sshlogin`, `filter_hosts`, `setup_basefile`, and `cleanup_basefile` integrate that model with command-line options.

`Job` models one running command. Important methods include `wrapped`, `sshlogin_wrap`, `openoutputfiles`, `start`, `print`, `linebuffer_print`, `print_joblog`, `should_be_retried`, `kill`, `family_pids`, `transfer`, `sshtransfer`, `return`, `sshreturn`, `sshcleanup`, and `workdir`. It owns stdout/stderr temp files or result files, process IDs, sequence number, slot number, exit status, timeout state, retry state, transfer sizes, and remote wrapping.

`init_run_jobs`, `start_more_jobs`, `start_another_job`, `drain_job_queue`, `progress`, `compute_eta`, `reaper`, `process_failed_job`, and `print_earlier_jobs` implement scheduling, progress display, failure accounting, and output ordering. This is also where RocksDB's hang diagnostic hook calls `ps_with_stack`.

`pipe_part_files`, `find_header`, `find_split_positions`, `cat_partial`, `spreadstdin`, `write_record_to_pipe`, and related helpers implement `--pipe` and `--pipepart` by splitting stdin or files on record boundaries and feeding chunks to jobs.

`Semaphore` implements GNU Parallel's semaphore mode using link-count-based locks in `~/.parallel/semaphores/id-<name>`.

## Control flow
At startup the script saves original stdin/stdout/stderr and inherited file descriptors, installs signal handlers, parses options and profiles, determines how many input records each command should consume, and opens input sources from `-a`, `::::`, or stdin. Header processing can rewrite command placeholders from column names to positional placeholders.

If `--filter-hosts` is active, remote hosts are tested with nested `parallel` invocations that query remote CPU/core counts, maximum command length, and login latency. `--onall` and `--nonall` take an alternate path that spawns one sub-parallel per host and exits after all host runs complete.

The normal path constructs `Global::JobQueue`, optionally pre-counts jobs for `--eta` or `--bar`, prepares `--pipepart` cat commands, asks each `SSHLogin` for its maximum runnable job count, optionally acquires a semaphore, and starts jobs. `start_more_jobs` walks hosts round-robin and starts a job only when host slots, load, swap, SSH delay, process limits, and file descriptor checks permit it. `start_another_job` pulls a `Job` from the queue, skips already-completed commands for `--resume`/`--results`, binds the host, and calls `Job->start`.

`Job->start` prepares grouped, ungrouped, result-directory, compressed, or file-output handles, sets `PARALLEL_SEQ` and `PARALLEL_PID`, and launches the wrapped command through the selected shell using `open3`. For remote hosts, `Job->wrapped` layers quoting, `nice`, `--cat`/`--fifo`, SSH, file transfer, return-file retrieval, cleanup, `--pipe` EOF detection, and optional tmux wrapping in a strict order.

`drain_job_queue` loops until no jobs are running and the queue is empty or no-new-jobs has been requested. It periodically calls `reaper`, starts more jobs when slots free up, prints ETA/progress, and in non-terminal CI mode emits progress every 30 seconds only when progress is advancing. If progress does not advance for around 300 seconds, it runs `ps_with_stack` to dump process and stack state for relative-path test binaries.

`reaper` handles child exits, updates exit status and runtime, releases slots, updates timeout statistics, prints output or buffers it for `--keep-order`, logs job rows, applies retry logic, and decrements host counts. Final cleanup removes base files, releases semaphores, terminates SSH master processes, and exits with either the bounded global failure count or a halt-on-error status.

## State and persistence behavior
Most runtime state is in global package variables, including `Global::running`, `Global::host`, `Global::total_running`, `Global::total_started`, `Global::JobQueue`, `Global::exitstatus`, `Global::job_already_run`, and replacement maps. Jobs also store state in per-object hashes.

Persistent and semi-persistent files are important. `--joblog` writes tab-separated rows with sequence, host, start time, runtime, bytes sent/received, exit value, signal, and command; `--resume` and `--resume-failed` read this file back to skip completed work. `--results` creates a directory tree derived from input arguments and writes `stdout`/`stderr` files. Profile and environment behavior reads `/etc/parallel/config`, `~/.parallel/config`, `~/.parallelrc`, `~/.parallel/<profile>`, `$PARALLEL`, and `~/.parallel/ignored_vars`.

The script writes temp files under `$TMPDIR` with names like `parXXXXX` for grouped output, arg files, host checks, and disk-full probes. It also uses `~/.parallel/tmp` for command-line length caches, load-average probes, swap probes, ControlMaster directories, and dynamic workdirs, and `~/.parallel/will-cite` to suppress citation notices. Semaphore mode persists lock directories and process-id files under `~/.parallel/semaphores`.

## Dependencies and integration points
RocksDB's `Makefile` invokes this script for `make check` and related parallel test paths, and comments there explicitly depend on this tool handing jobs out in input order. `Makefile` also notes that `--eta` is always used and this vendored copy has been modified for useful output on non-terminal CI systems. The script invokes `build_tools/ps_with_stack` by deriving the sibling script path from `dirname($0)`.

External tools used at runtime can include `ssh`, `rsync`, `tmux`, `ps`, `vmstat`, `sysctl`, `nproc`, `resize`, shell utilities, compression programs such as `lzop` or `gzip`, `gdb`/`pstack` indirectly through `ps_with_stack`, and remote `parallel` when querying remote hosts. Perl modules beyond core/standard modules are optional for debugging (`Time::HiRes`, `Text::ParseWords`, `Data::Dump`, `Data::Dumper`, `Devel::Size`, `Carp`, `Cwd`, `Fcntl`, `IO::Poll` in a remote wrapper string).

## Risks and edge cases
The script executes constructed shell strings and also evaluates replacement Perl expressions from user-provided `{= ... =}` placeholders. That is GNU Parallel behavior, but it means untrusted commands, arguments, profiles, `PARALLEL`, or replacement expressions must not be accepted in privileged contexts.

The file is an old vendored GNU Parallel snapshot. It has portability code for many operating systems, but modern environments may expose behavior changes in Perl, OpenSSH, rsync, shells, process listings, or CI signal handling. The script writes to `$HOME/.parallel`; missing, shared, or permission-constrained home directories can affect caches, citation notices, load probes, and semaphores. `HOME` is forced to `/tmp` when absent, which can create shared state across users or jobs.

Resource probing intentionally forks children and opens many file handles to estimate limits. On constrained CI hosts this can emit warnings, reduce concurrency, or fail before running tests. Grouped output and `--eta` pre-counting can read large input streams and write temporary files; full `$TMPDIR` is detected with `exit_if_disk_full`, but a disk-full event can still make test output incomplete.

Remote execution and transfer paths rely heavily on shell quoting, rsync semantics, login shell detection, ControlMaster cleanup, and remote GNU Parallel availability. Pathnames with unusual characters are quoted, but remote commands and user profiles remain high-risk surfaces. `--timeout` percentage mode depends on observed runtimes and can terminate slow tests if the remedian-derived threshold is too low.

The RocksDB-specific `ps_with_stack` hook runs only after progress has stopped in non-terminal output. It is diagnostic, not a scheduler fix; if `pstack` or `gdb` is unavailable or blocked by ptrace restrictions, the fallback is basic `ps`.

## Test signals
Primary test signal is indirect: RocksDB's `make check`, parallel test targets, and valgrind test paths exercise this script with `--joblog`, `--eta`, and `--tmpdir`. Successful runs should produce a valid `LOG`, per-test logs under `t/`, preserved or intentionally grouped output, and a zero exit code when all test commands pass.

Useful focused checks include `build_tools/gnu_parallel --gnu --help`, `build_tools/gnu_parallel --version`, a small local run such as `printf 'a\nb\n' | build_tools/gnu_parallel -j2 --plain echo {}`, a `--joblog`/`--resume` run, a `--keep-order` run, and a `--pipe` run against record-separated input. For the RocksDB modification, a CI-style non-terminal parallel run with a deliberately hung relative-path command should eventually print process information and attempt stack dumps through `ps_with_stack`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/gnu_parallel -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/make_package.sh -->
# sources/storage-engines/rocksdb/build_tools/make_package.sh

## Purpose
This Bash script builds a RocksDB static library, stages an install tree, and packages it as either a Debian package or RPM using `fpm`. It accepts exactly one argument, the RocksDB version string to pass to the package metadata. In RocksDB's top-level `Makefile`, it is invoked by the package target with the shared major/minor version.

## Important APIs, types, and functions
The script uses Bash functions rather than external APIs. `log` emits `[+]` status lines. `fatal` emits `[!]` and exits non-zero. `platform` detects `centos` from `/etc/yum.conf` or `ubuntu` from `/etc/dpkg/dpkg.cfg`, otherwise exits. `package` installs an OS package only when not already present, using `dpkg --get-selections`/`apt-get install` on Ubuntu and `rpm -qa`/`yum install` on CentOS. `detect_fpm_output` sets exported `FPM_OUTPUT` to `deb` or `rpm`. `gem_install` installs a Ruby gem if `gem list` does not already show it. `main` validates arguments, prepares build dependencies for Vagrant-like environments, builds and stages RocksDB, and invokes `fpm`.

## Control flow
The script enables `set -e`, defines helpers, detects `OS`, detects `FPM_OUTPUT`, and then calls `main "$@"` with shellcheck suppression for unquoted argument expansion.

`main` first requires exactly one version argument. When `/vagrant` exists, it assumes a Vagrant packaging VM and installs compiler, gflags, Ruby, and RPM build prerequisites. Ubuntu Vagrant installs `g++-4.8`, exports `CXX=g++-4.8`, installs `libgflags-dev`, and installs `ruby-all-dev`. CentOS Vagrant installs the devtools 1.1 repo when missing, installs GCC/G++ from that repo, exports `CC`, `CPP`, `CXX`, and extends `PATH`, installs a gflags RPM directly if needed, and installs Ruby, Ruby headers, RubyGems, and `rpm-build`.

After VM-specific dependency setup, it ensures the `fpm` gem is installed, runs `make static_lib`, chooses `LIBDIR=/usr/lib` for Debian-style packages or `rpm --eval '%_libdir'` for RPMs, removes any existing `package` staging directory, runs `make install DESTDIR=package PREFIX=/usr LIBDIR=$LIBDIR`, and finally calls `fpm -s dir -t $FPM_OUTPUT -C package -n rocksdb -v <version>` with URL, maintainer, license, vendor, description, and the staged `usr` tree.

## State and persistence behavior
The script mutates the working tree by deleting and recreating the `package` staging directory. It also produces package artifacts in the current directory through `fpm`. On Vagrant images it mutates system package state via `apt-get`, `yum`, `rpm -i`, `gem install`, and possibly downloads `/etc/yum.repos.d/devtools-1.1.repo`. Environment variables exported by the script include `OS`, `FPM_OUTPUT`, and compiler-related variables for old Ubuntu/CentOS build environments.

## Dependencies and integration points
The script depends on Bash, `make`, the RocksDB Makefile's `static_lib` and `install` targets, RubyGems, `fpm`, OS package managers, and platform-specific package metadata tools. It integrates with the top-level RocksDB package target and uses the source tree's normal install rules to decide what gets packaged. It assumes package output type from distro detection rather than from a command-line option.

## Risks and edge cases
The script likely requires root privileges for package installation inside Vagrant, but it does not use `sudo`; callers must already have permissions. OS detection is coarse and misses modern derivatives or container images that do not have `/etc/yum.conf` or `/etc/dpkg/dpkg.cfg`. The fatal message for unknown OS contains a typo, but still exits.

Package/gem existence checks use simple `grep --quiet $1` patterns and unquoted variables, so package names that are substrings of other packages or contain regex metacharacters can produce false positives. The direct CentOS gflags RPM URL and devtools repo URL are historical external dependencies and may no longer be reachable. `gem list | grep` can also match unintended gems.

`rm -rf package` is intentional but destructive if a caller expected to preserve a local `package` directory. `set -e` catches most command failures, but the script does not trap cleanup or provide partial-state recovery. It builds `static_lib`, so package contents are limited by what `make install` installs from that build mode.

## Test signals
Basic validation is `bash -n build_tools/make_package.sh` and ShellCheck-style review, though the file already suppresses specific shellcheck findings. Functional validation requires a packaging VM or container matching Ubuntu or CentOS, a successful `make static_lib`, a successful staged `make install`, and a generated `.deb` or `.rpm` with the expected version and installed `usr` payload. Integration validation is the top-level `make package` target.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/make_package.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/ps_with_stack -->
# sources/storage-engines/rocksdb/build_tools/ps_with_stack

## Purpose
This Perl utility prints a wide process tree and attempts to dump stack traces for processes that look like locally built test binaries. It is designed as a diagnostic companion for `build_tools/gnu_parallel`: when parallel test progress stalls in CI, `gnu_parallel` runs this script to reveal which relative-path commands are still running and what their thread stacks look like.

## Important APIs, types, and functions
The script is small and procedural. It uses `strict`, opens `ps -wwf` as a read pipe, parses the header row to discover the `PID` and `CMD` column indexes, and then inspects each subsequent row. For matching rows, it invokes `system("pstack $pid || gdb -batch -p $pid -ex 'thread apply all bt'")`.

## Control flow
The script starts `ps -wwf`, initializes `$cols_known`, `$cmd_col`, and `$pid_col`, and loops over every output line. It prints each `ps` line immediately. Until it sees a line containing `CMD`, it treats that line as the header and records the positions of `PID` and `CMD`.

After the header is known, each row is split on whitespace. The script extracts the PID and command by the recorded indexes. It only dumps stacks when the PID is numeric and the command looks like a relative path containing a slash but not starting with slash, using the pattern `^[^/ ]+[/]`. This matches commands such as `./my_test` or `foo/bar_test`, while avoiding `/usr/bin/time`, `grep`, and other commands found through absolute paths or `$PATH`.

## State and persistence behavior
The script has no persistent state and writes only to stdout/stderr inherited from its caller. It does not create files. Its only side effects are attaching to matching processes through `pstack` or `gdb`, which may temporarily stop or inspect processes depending on platform/tool behavior.

## Dependencies and integration points
It depends on Perl, `ps`, and either `pstack` or `gdb`. It is invoked by the vendored `gnu_parallel` script using `$script_dir/ps_with_stack || ps -wwf`, so if it fails, RocksDB still receives a process listing. It is intended for Linux-like development or CI hosts where built RocksDB tests are executed by relative path.

## Risks and edge cases
Parsing `ps` output by whitespace is inherently format-sensitive. Commands with whitespace before the first command word, unusual `ps` implementations, or headers that do not use `CMD`/`PID` as expected may lead to missed or incorrect matches. Because only the first whitespace-delimited command field is used, arguments do not affect matching.

`gdb -batch -p` and `pstack` can fail due to missing tools, ptrace restrictions, container security settings, different users, or hardened kernels. The command string interpolates only a numeric PID after validation, so shell injection risk is low. However, stack dumping every matching relative-path process can be expensive during large test runs.

## Test signals
A basic check is running `build_tools/ps_with_stack` during an active RocksDB test run and confirming it prints the `ps -wwf` listing plus "Dumping stacks for <pid>..." for relative-path test binaries. In restricted CI, an acceptable signal is that it still prints process lines even if `pstack` and `gdb` fail. Its integration signal is visible diagnostic output from stalled `make check` runs that use `gnu_parallel --eta`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/ps_with_stack -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/regression_build_test.sh -->
# sources/storage-engines/rocksdb/build_tools/regression_build_test.sh

## Purpose
This Bash script builds RocksDB in release mode, runs a fixed suite of `db_bench` performance benchmarks, stores benchmark output in temporary stat files, and reports selected throughput and latency metrics to Facebook ODS when running under Jenkins. When not under Jenkins, it prints the metric key/value pairs instead. The file is a regression/performance signal script rather than a unit test.

## Important APIs, types, and functions
The script uses `set -e` and a global `NUM=10000000` as the default key/write scale. It accepts one optional argument for `DATA_DIR` and a second optional argument for `STAT_FILE`; otherwise it creates temporary names via `mktemp`. `cleanup` deletes the database directory and all stat files matching `$STAT_FILE.*` and is installed as an EXIT trap.

Most of the script is a sequence of `./db_bench` invocations with explicit options. It exercises `fillseq`, `overwrite`, `readrandom`, `filluniquerandom`, `readwhilewriting`, `fillrandom`, `seekrandomwhilewriting`, and column-family-heavy configurations. Shared in-memory benchmark options are stored in `common_in_mem_args`.

`send_to_ods` accepts a metric key and value. Without `JENKINS_HOME`, it prints the pair. Under Jenkins, it sends the value to `https://www.facebook.com/intern/agent/ods_set.php` with entity `rocksdb_build` using `curl --silent --connect-timeout 60`. `send_benchmark_to_ods` parses a benchmark output file using `grep` and `awk` to derive QPS and p50/p75/p99 percentile latencies, then sends four metrics through `send_to_ods`.

## Control flow
The script chooses `DATA_DIR` and `STAT_FILE` from positional arguments or temp defaults, installs cleanup, and runs `make release` before any benchmark. It first fills a database with `fillseq`, measures overwrite, refills for read tests, and measures readrandom variants using 6 GB block cache, tailing iterators, 100 MB block cache, and a mixed overwrite/read case intended to leave data in memtable/SST state.

It then loads a smaller database using `filluniquerandom`, runs a dummy readrandom to compact or settle the data, measures readrandom with auto compactions disabled, and measures readwhilewriting with a write-rate limit. A memtable-focused benchmark runs `fillrandom,readrandom,` with a large write buffer and small value size.

The in-memory section defines a plain-table, no-compression, `/dev/shm/rocksdb` configuration with WAL in `/dev/shm`, fills roughly 50 million keys, and then runs 600-second `readwhilewriting` and `seekrandomwhilewriting` benchmarks with 32 threads. Finally, it measures `fillseq` and `overwrite` with 500 column families.

After all benchmark files are produced, the script calls `send_benchmark_to_ods` for each expected output file, mapping benchmark names to ODS metric suffixes such as `rocksdb.build.overwrite.qps`, `rocksdb.build.readrandom_tailing.p99_micros`, and `rocksdb.build.seekwhilewriting_in_ram.p50_micros`.

## State and persistence behavior
The script creates and deletes a RocksDB data directory and stat files. By default, both are under `mktemp` locations, but callers can supply persistent paths. Cleanup removes the entire `$DATA_DIR` and `$STAT_FILE.*` on exit, including failures. The in-memory benchmarks use a hard-coded `/dev/shm/rocksdb` database and WAL directory through `common_in_mem_args`; this is not controlled by `DATA_DIR` and may overwrite or conflict with other users of that path.

Benchmark output is persisted only until cleanup unless the script is interrupted in a way that bypasses the EXIT trap. ODS reporting is external network state when `JENKINS_HOME` is set; otherwise results are printed locally. The script does not maintain a local historical baseline.

## Dependencies and integration points
The script depends on Bash, `make release`, the built `./db_bench` binary, `grep`, `awk`, `curl`, `mktemp`, sufficient disk space for `$DATA_DIR`, and enough RAM-backed storage for `/dev/shm/rocksdb`. It integrates with Jenkins through `JENKINS_HOME` and with Facebook's internal ODS endpoint. It assumes `db_bench` output format contains the benchmark line with QPS in field 5 and a "Percentiles" line within six following lines with percentile fields in fixed positions.

## Risks and edge cases
The benchmark suite is resource-intensive. It uses 10 million operations for many disk-backed runs, a 6 GB cache size, 55,000 open files, 16 to 32 threads, 600-second in-memory runs, and a 50-million-key `/dev/shm` database. Small CI hosts can fail due to memory, tmpfs capacity, file descriptor limits, runtime limits, or noisy-neighbor performance variance.

Argument validation is minimal. Supplying only two arguments works, but extra arguments are ignored. Variable expansions such as `$DATA_DIR`, `$STAT_FILE`, `$JENKINS_HOME`, and the ODS URL parameters are mostly unquoted, which can misbehave with paths or values containing whitespace or shell metacharacters. Cleanup uses `rm -rf $DATA_DIR`, so an incorrectly supplied or empty `DATA_DIR` would be dangerous; defaults are safer but caller-provided values require care.

The parser in `send_benchmark_to_ods` is brittle. If `db_bench` output changes, if a benchmark name appears in multiple contexts, or if the "Percentiles" layout changes, QPS or latency values may be empty or wrong. Under Jenkins, `send_to_ods` checks for empty values and reports an error, but it does not fail the script. The hard-coded internal ODS endpoint is not useful outside Meta/Facebook infrastructure.

The in-memory benchmarks ignore the cleanup trap's `$DATA_DIR` removal and instead use `/dev/shm/rocksdb`; if `db_bench` does not clean that path between runs, stale RAM-backed data could affect results or consume tmpfs. The script also disables WAL in many disk benchmarks, so metrics target specific RocksDB configurations rather than end-user durability defaults.

## Test signals
Syntax validation can be done with `bash -n build_tools/regression_build_test.sh`. Functional validation is expensive: `make release` must succeed, `./db_bench` must exist and complete every configured run, expected stat files must be non-empty, and local non-Jenkins output should print metric keys and values. Under Jenkins, network calls to ODS should return successfully and keys should appear in the expected `rocksdb.build.*` namespace. A smaller manual smoke test would require editing `NUM` or wrapping `db_bench`, because the script itself has no fast-mode option.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/regression_build_test.sh -->
