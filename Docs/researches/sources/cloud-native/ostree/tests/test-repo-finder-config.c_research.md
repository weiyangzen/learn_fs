# sources/cloud-native/ostree/tests/test-repo-finder-config.c

## Purpose
This C unit test validates `OstreeRepoFinderConfig`, which resolves collection refs using configured remotes and their summaries. It also validates the higher-level `ostree_repo_find_remotes_async()` wrapper.

## Important APIs, Types, And Functions
Important types include `Fixture`, `OstreeRepo`, `OstreeRepoFinderConfig`, `OstreeCollectionRef`, `OstreeRepoFinderResult`, `GMainContext`, and `GAsyncResult`. Helpers include `setup`, `teardown`, `result_cb`, `assert_create_remote_config`, and variadic `assert_create_remote`. Tested APIs include `ostree_repo_finder_resolve_async/finish`, `ostree_repo_find_remotes_async/finish`, `ostree_repo_remote_add`, `ostree_repo_regenerate_summary`, and ref-setting APIs.

## Control Flow
The fixture creates a tempdir and parent repo. `no_configs` resolves two refs with no remotes and expects no results. `mixed_configs` creates collection and non-collection remote repos, configures valid, duplicate, mismatched, and no-collection remotes, resolves five collection refs, and asserts only valid collection-matching results remain. `find_remotes` repeats the scenario through `ostree_repo_find_remotes_async()` and additionally validates checksum strings and big-endian timestamps for requested and missing refs.

## State And Persistence
Temporary remote repositories are created with summaries, refs, collection IDs, commits, and remote config in the parent repo. Cleanup removes both the tempdir and harness-created parent repo source files.

## Dependencies And Integration Points
This integrates libglnx tempdirs, GLib async main-context iteration, repository summary generation, collection ref lookup, remote configuration, and result deduplication/canonicalization.

## Risks
Config finder results must ignore remotes whose configured collection ID does not match the remote summary, avoid non-collection remotes for collection refs, keep duplicates deterministic, and preserve checksum/timestamp maps for all queried refs. Async completion must happen on the expected context.

## Test Signals
GLib paths are `/repo-finder-config/init`, `/no-configs`, `/mixed-configs`, and `/find-remotes`. Result lengths, ref hash-table membership, checksum validation, and timestamp values are primary assertions.
