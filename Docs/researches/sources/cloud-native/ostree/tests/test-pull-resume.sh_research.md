<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-resume.sh -->
# sources/cloud-native/ostree/tests/test-pull-resume.sh

## Purpose
`test-pull-resume.sh` verifies pull resumption after interrupted or failed HTTP transfers using range requests.

## Important APIs, Types, And Functions
It uses `skip_without_ostree_httpd`, `setup_fake_remote_repo1 "archive" "" "--force-range-requests"`, initializes repos, repeatedly runs `ostree pull`, and finishes with `ostree fsck`.

## Control Flow
The script creates a repo, performs pulls in a retry loop intended to exercise resume state, and checks whether fsck succeeds after the resumable transfer completes. It cleans temporary repo paths afterward.

## State And Persistence
State includes partially downloaded objects in the repo tmp area, HTTP range request state, final refs/objects, and error output from failed attempts.

## Dependencies And Integration Points
It covers HTTP range requests, temporary object staging, resume/retry logic, and final fsck validation.

## Risks And Test Signals
The test depends on the HTTP fixture forcing range behavior. Passing signals include eventual successful pull and clean fsck, demonstrating partial downloads do not corrupt final objects.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-resume.sh -->
