<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/test.rs -->
## sources/cloud-native/ostree/tests/inst/src/test.rs

Purpose: shared Rust helper library for installed tests, including command assertions, temporary HTTP serving, environment parsing, and autopkgtest reboot integration.

Important APIs/functions: `cmd_fails_with()`, `cmd_has_output()`, `write_file()`, `TestHttpServerOpts`, `TEST_HTTP_BASIC_AUTH`, `validate_authz()`, `http_server()`, `with_webserver_in()`, `getenv_utf8()`, `get_reboot_mark()`, `reboot()`, and `prepare_reboot()`.

Control flow/state: HTTP server binds localhost port 0 and serves static files with optional Basic auth and random per-request delay. Reboot helpers exec or call `/tmp/autopkgtest-reboot*` with a mark.

Dependencies/integration: depends on Hyper/Tokio, `hyper-staticfile`, `base64`, `rand`, and test command wrappers. Used by `repobin.rs` and `destructive.rs`.

Risks/test signals: random delay uses blocking sleep inside request handling; reboot uses `exec()` and never returns on success. Unit tests cover command matching and Basic auth decoding.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/test.rs -->
