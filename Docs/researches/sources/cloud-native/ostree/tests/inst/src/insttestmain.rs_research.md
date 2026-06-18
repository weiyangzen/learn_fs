<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/insttestmain.rs -->
## sources/cloud-native/ostree/tests/inst/src/insttestmain.rs

Purpose: entry point for `ostree-test`, dispatching non-destructive libtest-mimic tests and guarded destructive tests.

Important APIs/types/functions: `Opt` supports `list-destructive`, `run-destructive`, and `non-destructive`; `TESTS` lists sysroot and repo tests; `DESTRUCTIVE_TESTS` lists transactionality and composefs. `DESTRUCTIVE_TEST_STAMP` gates destructive execution.

Control flow/state: always switches to a tempdir under `/var/tmp`, initializes `procspawn`, parses CLI args, runs selected tests, and for destructive tests requires both `/etc/ostree-destructive-test-ok` and `/run/ostree-booted`.

Dependencies/integration: used by kola install wrappers and direct installed tests. Depends on modules `composefs`, `destructive`, `repobin`, `sysroot`, `test`, and `treegen`.

Risks/test signals: destructive-test matching is string-based from function paths. Missing stamp correctly fails closed. Signals are libtest-mimic output or `ok destructive test: <name>`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/insttestmain.rs -->
