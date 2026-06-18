# sources/cloud-native/ostree/tests/test-remote-cookies.sh

## Purpose
This test verifies remote HTTP cookie management and confirms pull requests send exactly the configured cookies expected by the test server.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1 --expected-cookies`, `ostree remote add-cookie`, `ostree remote delete-cookie`, `ostree pull`, and assertions against `repo/origin.cookies.txt`.

## Control Flow
The fake HTTP remote is configured to require `foo=bar` and `baz=badger`. A pull without cookies must fail. The test adds both cookies, confirms they are persisted, and verifies pull success. It deletes one cookie, checks the cookie file no longer contains it, and confirms pull failure. Finally it re-adds the removed cookie and confirms pull succeeds again.

## State And Persistence
Cookies are persisted in `repo/origin.cookies.txt`. Remote config stores the origin URL. Pull success depends on the cookie file being consumed by the HTTP fetch layer.

## Dependencies And Integration Points
This integrates remote cookie CLI operations, libsoup or curl HTTP request cookie handling, test webserver expected-cookie validation, and repo-local cookie persistence.

## Risks
Deleting one cookie must not remove unrelated cookies. Cookie domain/path matching must match the server address used in the test. Stale cookie files could create false positives if cleanup is incomplete.

## Test Signals
Four TAP results cover setup failure without cookies, initial cookie pull, delete failure, and second successful cookie pull.
