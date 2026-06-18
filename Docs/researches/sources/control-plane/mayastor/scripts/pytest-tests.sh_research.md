# sources/control-plane/mayastor/scripts/pytest-tests.sh

Purpose: orchestrates Python docker-compose pytest suites and report generation.

Important APIs/types/functions: requires `SRCDIR`, creates `test/python/reports`, activates `test/python/venv`, defines `cleanup_handler`, `trap_setup`, `clean_all`, `is_test`, and `run_tests`. Supports `--clean-all`, `--clean-all-exit`, direct test paths/selectors, and pass-through pytest args.

Control flow: validates environment and NVMe config, cleans reports, resolves arguments to tests or extra args, installs traps, then runs selected tests or a built-in suite list with `python -m pytest --tc-file test_config.ini --docker-compose=... --junit-xml=...`.

State/persistence: removes/recreates reports, tears down docker-compose clusters, and writes junit XML under reports.

Dependencies/integration: integrates Python virtualenv, pytest, pytest-docker-compose config, NVMe host config, and many Mayastor test suites.

Risks: `clean_all` scans from current directory after `cd "$SRCDIR/test/python"` and can affect all compose tests. Argument parsing with `realpath $1` is unquoted. Duplicate `tests/cli_controller` appears in the default list.

Test signals: per-suite XML reports and exit status provide Python e2e regression signals.
