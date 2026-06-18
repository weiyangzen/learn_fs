# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/annotation_status_v1beta1.yaml

Purpose: expected beta1 result when downgrading a detailed v1beta2 status object.

Important content: v1beta1 content with a serialized `volume-snapshot-info-list` annotation preserving full entries, while `status.volumeSnapshotHandlePairList` contains only snapshot/volume handle pairs and top-level status fields remain.

Control flow: used by beta2-to-beta1 conversion test to confirm annotation creation and field stripping.

State and persistence: represents the reversible downgrade storage format.

Dependencies and integration: paired with `annotation_status_v1beta2.yaml`.

Risks and test signals: validates that beta2-only per-entry data is preserved outside the beta1 schema instead of being permanently lost.
