## sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/libtap.sh

Purpose: portable Bourne-shell TAP helper library for shell tests. It mirrors the C helper surface with planning, assertions, block skip/status helpers, program-output checks, diagnostics, bailout, source/build file lookup, and temporary-directory creation.

Important APIs/functions: `plan`, `plan_lazy`, `finish`, `skip_all`, `ok`, `skip`, `ok_block`, `skip_block`, `puts`, `ok_program`, `strip_colon_error`, `bail`, `diag`, `test_file_path`, and `test_tmpdir`. It uses shell globals `count`, `planned`, and `failed`, and `tap_`-prefixed temporaries because Solaris `/bin/sh` lacks `local`.

Control flow: tests source the script, call `plan` or `plan_lazy`, then assertions. `plan*` installs `trap finish 0`. `finish()` calculates the highest test number, emits a lazy plan if needed, and prints TAP diagnostic summaries for count mismatches, failures, or all-success cases. `ok()` shifts off a description and runs the remaining command as the predicate.

State and persistence: state is shell-global in the current process. `test_tmpdir()` creates `$C_TAP_BUILD/tmp` or `./tmp` and returns the path, but this script does not provide a cleanup function. `ok_program()` captures combined stdout/stderr and compares both status and exact output.

Dependencies: POSIX-ish `/bin/sh`, `expr`, `cat`, `sed`, `mkdir`, and standard shell redirection. It intentionally avoids `local` and uses a here-doc in `puts()` for portability.

Integration points: shell tests produce TAP for `runtests.c`. `test_file_path()` integrates with runner-provided `C_TAP_BUILD` and `C_TAP_SOURCE`. `strip_colon_error()` normalizes platform-specific strerror suffixes for portable expected-output tests.

Risks: shell globals can be clobbered by tests. `ok_program()` exact-output comparisons are sensitive to whitespace and shell command substitution trimming. `puts()` comments warn against using it via backticks inside double quotes on Solaris due to escaping behavior. Lazy planning emits a plan even after zero tests unless caller controls flow.

Test signals: run shell tests under a strict `/bin/sh`, including lazy planning, skip-all, failing command predicates, exact output/status comparison, colon-error stripping, source/build lookup precedence, and tmpdir creation.
