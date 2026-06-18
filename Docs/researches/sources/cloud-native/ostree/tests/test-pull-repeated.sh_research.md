<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-repeated.sh -->
# sources/cloud-native/ostree/tests/test-pull-repeated.sh

## Purpose
`test-pull-repeated.sh` validates HTTP pull retry behavior for repeated transient server errors.

## Important APIs, Types, And Functions
It requires `OSTREE_HTTPD`, optionally signs commits if GPGME is available, uses `setup_fake_remote_repo1` with `--random-500s` or `--random-408s`, `ostree pull --network-retries=N`, `assert_fail`, and repeated loops.

## Control Flow
The test first configures a remote that almost always returns HTTP 500 and verifies a zero-retry pull fails. It then runs many pulls against a 50 percent failure remote to ensure retries eventually succeed, and repeats the same pattern for HTTP 408 request timeouts. TAP cases cover no-retry failures, repeated successful retries, and mirror or normal pull variants.

## State And Persistence
State includes fake HTTP remotes with randomized error injection, fresh archive repos per scenario, error logs, and optional signed commit metadata.

## Dependencies And Integration Points
It covers network retry policy, HTTP status classification, pull idempotency, optional GPG verification under retries, and mirror-mode pulls.

## Risks And Test Signals
Randomized failures can be probabilistic, so loops and retry counts are chosen to expose retry regressions. Passing signals include expected immediate failures with `--network-retries=0` and successful repeated pulls with retries enabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-repeated.sh -->
