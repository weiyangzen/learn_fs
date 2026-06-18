# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/python_version.py

Purpose: Checks whether the running Python meets a minimum version, discovers newer `python3.x` binaries on `PATH`, optionally prints alternatives, and can re-exec the current script under a newer interpreter.

Important APIs/types/functions: `PythonVersion.parse_version()` and `ver_str()` convert version strings/tuples. `cmd_print()` shell-quotes command lines with wrapping. `get_python_version()` executes `<cmd> --version`. `find_python()` scans PATH for `python3.[0-9]` and `python3.[0-9][0-9]`. `check_python()` is the main policy API.

Control flow: `check_python()` returns immediately when `sys.version_info[:3]` satisfies `min_version`. Otherwise it discovers candidates, optionally prints commands, optionally exits, or calls `os.execv()` with the newest candidate and the current script path plus original arguments.

State and persistence: Stateless except for subprocess execution and possible process replacement. No files are written.

Dependencies/integration: Uses stdlib `os`, `re`, `subprocess`, `shlex`, `sys`, `glob`, and `textwrap.indent`. Intended for scripts that need newer Python during documentation builds or tooling execution.

Risks: `get_python_version()` only parses `stdout`, but some Python versions historically printed version to `stderr`; those would be treated as `(0,0,0)`. PATH scanning can include duplicate symlinked interpreters. `os.execv()` failure exits the current script. `find_python()` compares tuples directly, so unusual version tuple lengths can affect ordering.

Test signals: Mock subprocess and PATH scanning for versions below/above minimum, stdout vs stderr version output, `bail_out` with `success_on_error`, alternatives printing, and failed `execv()`.
