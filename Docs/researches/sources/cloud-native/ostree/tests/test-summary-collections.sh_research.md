# sources/cloud-native/ostree/tests/test-summary-collections.sh

## Purpose
This test validates collection-aware summary generation and summary view output for local collection refs, mirrored collection refs, and pulled remote collection refs.

## Important APIs, Types, And Functions
It uses `ostree_repo_init --collection-id`, `ostree commit`, `ostree summary --update`, `ostree summary --view`, `ostree refs --collections --create`, `ostree remote add --collection-id`, and `ostree pull`.

## Control Flow
The script creates a collection-enabled repo with five commits, updates the summary, and checks all refs are shown with the repo collection ID and that the summary collection ID metadata is present. It creates a mirrored collection ref under another collection and verifies it appears. It then pulls from a remote with a collection ID and confirms that ref appears in summary view, then pulls from a remote without a collection ID and verifies that ref is omitted.

## State And Persistence
State includes local collection refs, mirror refs, remote refs, summary metadata, and temporary collection/no-collection remote repos.

## Dependencies And Integration Points
This integrates summary generation, collection ID metadata, collection ref namespace, remote pull behavior, and summary human-readable rendering.

## Risks
Summary generation must include only refs with meaningful collection IDs and avoid leaking no-collection remote refs into collection-aware output. Mirrored refs need correct collection association.

## Test Signals
The single TAP result follows regex checks for all expected collection/ref tuples and absence of no-collection `rcommit2`.
