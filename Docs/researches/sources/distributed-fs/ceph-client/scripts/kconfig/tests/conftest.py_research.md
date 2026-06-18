# sources/distributed-fs/ceph-client/scripts/kconfig/tests/conftest.py

## Purpose
`conftest.py` provides the pytest fixture framework for Kconfig unit tests. It runs `scripts/kconfig/conf` in isolated temporary directories and offers helpers to compare stdout, stderr, and generated config output with expected fixtures.

## Important APIs, Types, and Functions
`CONF_PATH` points at `scripts/kconfig/conf`. Class `Conf` stores test directory, return code, stdout, stderr, and config content. Runner methods include `_run_conf()`, `oldaskconfig()`, `oldconfig()`, `olddefconfig()`, `defconfig()`, `_allconfig()`, `allyesconfig()`, `allmodconfig()`, `allnoconfig()`, `alldefconfig()`, and `randconfig()`. Checker methods continue below the displayed portion and include content/match helpers referenced by tests, such as `stdout_contains()`, `stderr_contains()`, `stderr_matches()`, `config_contains()`, `config_matches()`. A pytest fixture returns `Conf(request)`.

## Control Flow
`_run_conf()` builds `[CONF_PATH, mode, 'Kconfig']`, sets `srctree` to the test directory, clears `KCONFIG_DEFCONFIG_LIST`, creates a temporary directory, optionally copies an input `.config`, starts `conf`, feeds explicit keys and/or repeated newlines for interactive modes, waits, captures stdout/stderr, reads the generated config if expected, and prints captured diagnostics for pytest failure output.

## State and Persistence
All generated files are isolated in `tempfile.TemporaryDirectory()` and removed after each run. Test output is stored on the `Conf` instance for assertions. Environment overrides are passed to child processes.

## Dependencies and Integration Points
Depends on pytest, Python stdlib, and a built `scripts/kconfig/conf` binary. It integrates all Kconfig test packages in this tree through the `conf` fixture.

## Risks and Edge Cases
Interactive handling writes repeated newlines until the process exits; if `conf` blocks without consuming stdin correctly, tests can hang. The default argument `extra_env={}` is mutable and can leak modifications between calls in Python, though current usage typically overwrites deterministic keys. The fixture assumes expected files are named consistently in each test directory.

## Test Signals
Every Kconfig pytest module in this subset depends on this file. Failures in process launching, env setup, stdin handling, or expected matching will surface broadly.
