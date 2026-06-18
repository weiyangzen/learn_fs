<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-localcache.sh -->
# sources/cloud-native/ostree/tests/test-pull-localcache.sh

## Purpose
`test-pull-localcache.sh` verifies pulls using a local cache repository to avoid fetching objects already present locally.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1 "archive"`, a `repo-local` archive cache, helper `init_repo`, commits to the remote, `ostree pull --localcache-repo=...`, `rev-parse`, and output assertions about metadata/content fetched versus local counts.

## Control Flow
The script initializes a cache repo with existing remote content, creates fresh client repos, pulls with the local cache enabled, and checks fetch statistics. It then updates the remote, pulls again with cache assistance, and verifies the resulting commit checksum matches.

## State And Persistence
State includes the cache repo, client repo, remote commits, working `files` directories, and output logs.

## Dependencies And Integration Points
It covers pull's object lookup against an auxiliary local repository, fetch progress accounting, and fallback to remote for missing objects.

## Risks And Test Signals
The test is sensitive to progress wording and object counts. Passing signals include expected "local" object counts in output and matching final commit checksums.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-localcache.sh -->
