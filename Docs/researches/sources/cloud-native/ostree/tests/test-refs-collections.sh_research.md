# sources/cloud-native/ostree/tests/test-refs-collections.sh

## Purpose
This shell test validates collection-aware ref listing, filtering, creation, deletion, remote ref visibility, and compatibility with older repositories that lack `refs/mirrors`.

## Important APIs, Types, And Functions
The test uses `ostree_repo_init --collection-id`, `ostree commit`, `ostree refs`, `ostree refs --collections`, `--list`, `--delete`, `--create=COLLECTION:REF`, `ostree remote add --collection-id`, and `ostree pull`.

## Control Flow
It creates a repo with collection ID `org.example.Collection`, commits five refs, confirms plain `refs` hides collection IDs while `--collections` shows them, tests collection filtering, exercises deletion by explicit refs and by collection ID, creates a mirrored collection ref, then pulls from a remote with a collection ID and confirms it appears in collection listings. A second remote without a collection ID is pulled and must not appear. The final phase removes `repo/refs/mirrors` before list, create, and delete operations to verify old-repo tolerance.

## State And Persistence
State is stored under normal heads and collection/mirror ref namespaces, remote config, local remote refs, and temporary remote repositories. Removing `refs/mirrors` simulates historical repository layout.

## Dependencies And Integration Points
This integrates ref storage, collection ID metadata, remote configuration, pull-created collection refs, and compatibility paths for missing mirror directories.

## Risks
Risks include leaking collection refs into plain output, deleting too broadly without `--collections`, failing on old repos, or showing remote refs for remotes without collection IDs. Ref namespace operations are especially sensitive to prefix matching.

## Test Signals
Two TAP results cover current repository behavior and old repository compatibility. Counts and regex matches verify exact ref visibility after each mutation.
