<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-prune-collections.sh -->
# sources/cloud-native/ostree/tests/test-prune-collections.sh

## Purpose
`test-prune-collections.sh` validates prune behavior for collection refs and mirror refs.

## Important APIs, Types, And Functions
It defines `set_up_repo`, uses `ostree_repo_init --collection-id`, `commit`, collection/mirror ref manipulation, `ostree prune`, `prune --delete-commit`, and output assertions for total/deleted objects.

## Control Flow
The setup creates a repo with collection-bound commits and refs. The test first verifies that deleting a commit still referenced by collection metadata fails or leaves no unreachable objects. It then removes refs in controlled ways and confirms prune either preserves reachable collection objects or deletes unreachable objects.

## State And Persistence
Repository state includes commit objects, ordinary refs, collection refs under mirror namespaces, and temporary checksum files. The script directly removes `refs/mirrors` for one scenario.

## Dependencies And Integration Points
It covers prune reachability analysis with collection-aware refs, delete-commit semantics, and object deletion accounting.

## Risks And Test Signals
The test guards against pruning commits reachable only through collection refs. Passing signals include `No unreachable objects` while collection refs exist and deletion counts only after those refs are removed.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-prune-collections.sh -->
