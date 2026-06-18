# sources/compression/zstd/tests/DEPRECATED-test-zstd-speed.py

## Purpose

This deprecated Python script continuously benchmarks zstd branches and emails warnings when speed or compression ratio regresses relative to previous results.

## Important APIs, Types, and Functions

Core helpers include `execute`, `does_command_exist`, `send_email`, `send_email_with_attachments`, `git_get_branches`, `git_get_changes`, `get_last_results`, `benchmark_and_compare`, `update_config_file`, `double_check`, and `test_commit`. Command-line arguments define test files, email recipients, dictionary, repo URL, speed/ratio thresholds, load limit, compression level range, sleep interval, timeout, dry-run, and verbosity.

## Control Flow, State, and Persistence

The script validates test files and dictionary, requires `mail` or `mutt`, clones the repo into `speedTest/zstd` if needed, writes `speedTest.pid`, then loops forever. On each tick it fetches branches, detects new commits, builds gcc/clang/32-bit binaries, records MD5/compiler metadata, benchmarks files, appends result files, and sends alerts. It persists commit markers and result/log/email files under `speedTest`.

## Dependencies and Integration Points

It depends on Git, make, gcc, clang, taskset on Linux, mail/mutt, and zstd program make targets. It is superseded by `automated_benchmarking.py`.

## Risks and Test Signals

Risks include `shell=True` command construction, no filename-with-space support, persistent pid cleanup only on keyboard interrupt, load-average dependence, external email tools, and branch-name result-file collisions. Test signals are mostly operational: dry-run path, clone/build success, result parsing, timeout handling, alert generation, and cleanup of `speedTest.pid`.
