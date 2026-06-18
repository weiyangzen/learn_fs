<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-mirror-summary.sh -->
# sources/cloud-native/ostree/tests/test-pull-mirror-summary.sh

## Purpose
`test-pull-mirror-summary.sh` verifies that mirror pulls copy summary metadata, summary signatures, and additional summary-indexed files correctly.

## Important APIs, Types, And Functions
It optionally signs commits with GPG, uses `setup_fake_remote_repo1`, creates extra files referenced by summary metadata, initializes archive mirror repos, runs `ostree pull --mirror`, checks `repo/summary` and `repo/summary.sig`, and tests truncated signature behavior.

## Control Flow
The script mirrors a remote and checks summary presence plus copied extra files. If GPG is unavailable, signature-specific checks are skipped. With GPG, it verifies signed summary mirroring, failure when signature verification is required but unavailable/bad, and behavior when summary signatures are truncated or missing.

## State And Persistence
State includes remote summary and summary signature files, extra file directories under the HTTP repo, archive mirror repos, and checkout copies used to inspect mirrored content.

## Dependencies And Integration Points
It covers mirror-mode summary copying, summary signatures, additional metadata files, GPG verification, and checkout of mirrored refs.

## Risks And Test Signals
The test is sensitive to GPG availability and signature file corruption. Passing signals include mirrored summaries/signatures where expected, extra files present with expected content, and failure for invalid signed summary scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-mirror-summary.sh -->
