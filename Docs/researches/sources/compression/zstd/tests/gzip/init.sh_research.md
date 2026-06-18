<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/init.sh -->
## sources/compression/zstd/tests/gzip/init.sh

Purpose: Shared POSIX shell harness for the imported gzip tests. It normalizes shell behavior, provides diagnostics and comparison helpers, creates an isolated temporary directory, manages cleanup traps, and supports `$EXEEXT` executable shims.

Important APIs and functions: Test scripts use `Exit`, `fail_`, `skip_`, `fatal_`, `framework_failure_`, `returns_`, `compare`, and `path_prepend_`. Internal helpers include `warn_`, `emit_diff_u_header_`, `compare_dev_null_`, `find_exe_basenames_`, `create_exe_shims_`, `setup_`, `remove_tmp_`, `rand_bytes_`, and `mktempd_`.

Control flow: The script computes `ME_`, defines helpers, sanitizes zsh/POSIX shell mode, and if necessary re-execs under a shell that supports command substitution, `local`, and extra `$EXEEXT` features. It enables `MALLOC_PERTURB_`, chooses a portable `compare` implementation from `diff -u`, other diff modes, or `cmp`, sources `init.cfg`, calls `setup_`, and installs an exit trap to remove the temporary directory.

State and persistence: Exports `MALLOC_PERTURB_`, possibly `gl_set_x_corrupts_stderr_`, `PATH` changes from `path_prepend_`, and `$re_shell` on re-exec. It creates a per-test temporary directory with restrictive permissions and removes it on exit or signals. Cleanup can be customized through `cleanup_`.

Dependencies and integration points: Depends on common shell utilities (`expr`, `sed`, `diff`, `cmp`, `mktemp`, `dd`, `tr`, `mkdir`, `chmod`, `rm`) and optionally `/dev/urandom`. Test files rely on its temp-directory isolation, output comparison, skip/fail exit codes, and `EXEEXT` aliasing for Windows-like builds.

Risks: This harness is intentionally broad and portable but fragile if shell feature probes are changed. `rand_bytes_` fallback can run host inspection commands and pipe through `gzip`; this matters if `gzip` on `PATH` is the program under test. Signal traps and re-exec logic are order-dependent. `returns_` uses `local`, which is why shell selection enforces that extension.

Test signals: Test scripts exiting through `Exit` should preserve status through cleanup. `compare /dev/null file` should emit useful diffs for non-empty files. `path_prepend_` should make local symlinked test programs win over system programs.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/init.sh -->
