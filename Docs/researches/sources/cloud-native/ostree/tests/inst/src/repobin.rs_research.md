<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/repobin.rs -->
## sources/cloud-native/ostree/tests/inst/src/repobin.rs

Purpose: non-destructive repo/CLI tests using temporary repositories.

Important APIs/functions: `itest_basic()` checks `ostree --help`; `itest_nofifo()` verifies committing FIFOs fails; `itest_mtime()` verifies repo mtime changes after a second commit; `itest_extensions()` checks `repo/extensions`; `itest_pull_basicauth()` serves a repo over HTTP with Basic auth and validates unauth/badauth 403 versus good auth success.

Control flow/state: most tests run inside `with_procspawn_tempdir`; the auth test creates a server repo, client repo, remotes with credential variants, and uses `treegen::mkroot()` for content.

Dependencies/integration: relies on `sh_inline`, `with_procspawn_tempdir`, helper assertions from `test.rs`, local HTTP server, and OSTree CLI.

Risks/test signals: exact stderr strings and HTTP 403 are asserted. Auth URI embedding tests client credential handling and may expose URL parsing regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/repobin.rs -->
