<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-collections.sh -->
# sources/cloud-native/ostree/tests/test-pull-collections.sh

## Purpose
`test-pull-collections.sh` validates pull and pull-local behavior for collection-aware refs and collection binding metadata.

## Important APIs, Types, And Functions
Helpers include `do_commit`, `do_summary`, `do_collection_ref_show`, `ensure_no_collection_ref`, `do_join`, `ensure_collection_ref`, `do_remote_add`, `do_pull`, and `do_local_pull`. The script uses `ostree_repo_init`, commits with collection/ref binding metadata, summaries, remotes, pull, pull-local, refs, and mirror pulls.

## Control Flow
It creates repos with and without collection IDs, local and remote variants, commits refs with valid and invalid binding metadata, and checks whether collection refs are created or omitted as appropriate. It then attempts pulls that should fail for bad collection bindings and confirms mirror pulls do not rewrite existing summaries unexpectedly.

## State And Persistence
State includes multiple repos, collection IDs, summary files/signatures, local and remote refs, collection mirror refs, and checksum comparisons for summaries.

## Dependencies And Integration Points
It integrates collection ID config, commit binding metadata, summary updates, normal pull, local pull, mirror behavior, and ref namespace storage.

## Risks And Test Signals
Binding validation is subtle: wrong collection IDs or refs must fail without corrupting local refs. Passing signals include expected collection ref creation, failure of bad binding pulls, and stable summary content in mirror subset pulls.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-collections.sh -->
