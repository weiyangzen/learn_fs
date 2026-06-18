# sources/compression/lz4/tests/test-lz4-speed.py

## Purpose
This long-running Python daemon monitors LZ4 branch performance. It periodically fetches branches, builds GCC, 32-bit GCC, and Clang variants, benchmarks configured test files, compares against prior results, and emails warnings for speed or ratio regressions.

## Important APIs and Control Flow
Helpers include `execute()`, `does_command_exist()`, `send_email()`, `git_get_branches()`, `git_get_changes()`, `get_last_results()`, `benchmark_and_compare()`, `update_config_file()`, `double_check()`, and `test_commit()`. Main parsing requires test filenames and email recipients, validates mail tools, clones the repo into `speedTest/lz4`, creates a `speedTest.pid`, then loops forever based on load average and `sleepTime`. Each new branch commit is checked out, built, benchmarked with `programs/lz4 -rqi5b1e<level>`, recorded, and compared.

## State, Dependencies, and Integration
Persistent state includes cloned repo, commit marker files, result files, log files, email temp files, and pidfile under `speedTest`. Dependencies include `git`, `make`, GCC, Clang, `mutt` or `mail`, and benchmark input files. It integrates with the command-line benchmark output format and branch workflow.

## Risks and Test Signals
The script is intentionally operational, not a unit test. It uses `shell=True`, whitespace-split filename limitations, load-average gating, and persistent mutable files. It provides high-value performance regression signals but can loop indefinitely, send repeated emails, and fail noisily if toolchains or mail are missing.
