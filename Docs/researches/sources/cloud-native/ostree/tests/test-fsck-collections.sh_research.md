<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-fsck-collections.sh -->
# sources/cloud-native/ostree/tests/test-fsck-collections.sh

## Purpose
`test-fsck-collections.sh` validates `ostree fsck` consistency checks for collection refs, collection binding metadata, ref binding metadata, and back-reference validation.

## Important APIs, Types, And Functions
Helpers `set_up_repo_with_collection_id` and `set_up_repo_without_collection_id` create repos and commits with binding metadata. The script uses `ostree fsck`, `fsck --verify-bindings`, `fsck --verify-back-refs`, `refs --collections`, direct ref-file deletion, and commit-object counts.

## Control Flow
The test first checks a repo with a collection ID, deletes ordinary heads or mirror refs, and ensures fsck notices missing binding references only when the relevant verification mode is enabled. It then mutates remote collection IDs and requested refs to provoke binding failures. A second repo without a collection ID checks ordinary ref binding behavior and back-reference failures for missing refs.

## State And Persistence
The test mutates temporary repository state directly, including `refs/heads`, `refs/mirrors`, remote config, and commit metadata. Commit objects persist across ref deletions so fsck can validate reachability and binding relationships.

## Dependencies And Integration Points
It covers fsck's integration with commit metadata fields for ref and collection bindings, collection-aware ref namespaces, remote collection configuration, and repository object enumeration.

## Risks And Test Signals
The test relies on exact diagnostic messages for binding mismatches. Passing signals include `Validating refs...` and `Validating refs in collections...` phases appearing as expected, missing refs causing failures under verification flags, and normal fsck staying tolerant where binding checks are not requested.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-fsck-collections.sh -->
