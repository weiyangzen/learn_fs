## sources/distributed-fs/openafs/src/libuafs/afsload/afsload_check.pl

Purpose: Validates an afsload configuration for a given MPI process count before execution.

Important APIs and functions: Calls `AFS::Load::Config::check_conf($np, $conf_file)`. Local `usage` enforces the argument form `-p <NP> <testconfig.conf>`.

Control flow: The script requires at least three arguments, validates the first is `-p`, validates process count as decimal digits, prints a status line, calls `check_conf`, and prints success if no fatal error is thrown.

State and persistence: No persistent state. Warnings and fatal parse errors are emitted to stdout/stderr.

Dependencies and integration: Depends on the `AFS::Load::Config` Perl module and shares the same config grammar as the runtime runner. The shell front-end invokes this unless quiet mode is requested.

Risks: Only validates syntactic/config coverage rules, not filesystem availability, cache directory existence, MPI readiness, or action runtime semantics. Argument parsing is positional and minimal.

Test signals: Bad argument count, nonnumeric `-p`, invalid flag, malformed config, node range warnings, and successful validation for provided simple and large example configs.
