# sources/distributed-fs/juicefs/pkg/meta/interface_test.go

## Purpose

`interface_test.go` verifies credential helper behavior used by `NewClient` for MySQL and Postgres metadata URIs. The coverage is focused on password injection, environment/file password sourcing, precedence, whitespace trimming, and error handling.

## Important Tests

`Test_injectPasswordIntoURI` supplies `dbPasswd` to SQL URI shapes. It confirms existing passwords are preserved; empty or absent passwords are inserted; MySQL socket-style authorities and Postgres host/socket URLs work; missing `@` and malformed userinfo with too many colon-separated fields error. It also documents edge handling for usernames containing `@`, because the helper uses the last `@` as authority terminator.

`Test_setPasswordFromEnv` creates a temporary password file and exercises `META_PASSWORD`, `META_PASSWORD_FILE`, both variables together, neither variable, and nonexistent password file. `META_PASSWORD` takes precedence over file content. Tests clean both environment variables before and after each case.

`Test_readPasswordFromFile` creates temporary files with plain passwords, surrounding whitespace, empty content, and special characters. It confirms `strings.TrimSpace` behavior and reports an error for missing files.

## Control Flow And State

All tests use temporary directories and same-package access to unexported helpers. Environment mutation is localized with `os.Unsetenv` and deferred cleanup, which prevents test pollution across subtests in normal serial execution.

## Dependencies And Integration Points

The tests touch only `os`, `filepath`, and `testing`; they avoid live database clients. They validate the pre-driver URI transformation path used by `NewClient` for `mysql` and `postgres` schemes.

## Risks And Gaps

The tests do not call `NewClient` itself, so they do not verify that password injection is applied only to SQL drivers or that redacted logging hides injected passwords. They do not test percent-escaping of password characters that need URL escaping, although `url.UserPassword` is used by the implementation. Since environment tests are not explicitly parallel-safe, adding `t.Parallel()` would be unsafe.

## Test Signals

These are deterministic unit tests. Failures indicate regressions in secure/noninteractive SQL metadata configuration, especially deployment flows that supply credentials through environment variables or mounted secret files.
