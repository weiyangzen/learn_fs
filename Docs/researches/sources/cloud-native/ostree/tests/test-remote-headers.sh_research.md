# sources/cloud-native/ostree/tests/test-remote-headers.sh

## Purpose
This test verifies that `ostree pull` sends caller-specified HTTP headers and appends a custom user-agent suffix to the default libostree user agent.

## Important APIs, Types, And Functions
It uses `skip_without_ostree_httpd`, `ostree --version` parsed with Python YAML, `setup_fake_remote_repo1 --expected-header`, `ostree pull --http-header`, and `--append-user-agent`.

## Control Flow
The script computes the current libostree version, starts a fake remote that expects `foo=bar`, `baz=badger`, and `User-Agent=libostree/$V dodo/2.15`, creates a client repo, and adds the remote. It verifies pulls fail with no headers and with missing or wrong user-agent suffix, then succeeds when both custom headers and the expected appended user agent are supplied.

## State And Persistence
The only persistent repository state is the remote configuration and pulled objects after the successful final pull. Header expectations live in the temporary HTTP server process.

## Dependencies And Integration Points
This integrates HTTP request configuration, user-agent construction, CLI option parsing, version reporting, and the test server's request validation.

## Risks
Header handling can drop duplicates, override user-agent incorrectly, or fail to combine the default agent with the appended suffix. Version parsing depends on the YAML structure of `ostree --version`.

## Test Signals
Two TAP results cover failed setup cases and successful pull. Expected failures are enforced by `assert_fail`.
