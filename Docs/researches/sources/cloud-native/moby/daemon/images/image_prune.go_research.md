<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_prune.go -->
# sources/cloud-native/moby/daemon/images/image_prune.go

Purpose: removes unused images and reports reclaimed space for the legacy image store.

Important APIs and control flow: `ImagePrune` uses an atomic guard to reject concurrent prune operations, validates filters, chooses dangling heads or all images, filters intermediary images, `until`, and labels, then deletes refs or dangling IDs through `ImageDelete` with `PruneChildren`. It records delete responses, computes reclaimed space from deleted layer chain IDs, logs cancellation details, and emits a prune event. `matchLabels` handles positive and negative label filters. `getUntilFromPruneFilters` parses one `until` value.

State and persistence: mutates image, reference, and layer state through `ImageDelete`; reads layer sizes; writes events. The `pruneRunning` atomic flag is transient process state.

Dependencies and integration: integrates filters, timestamp parsing, image delete semantics, layer store maps, daemon events, and conflict/error classification.

Risks: cancellation stops additional deletes but still reports already reclaimed data. `imageDeleteFailed` suppresses conflicts and cancellation/deadline errors as prune misses rather than hard failures. Reclaimed space is estimated from layer records captured before deletion.

Test signals: no direct tests here; prune API and image delete tests are the main coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_prune.go -->
