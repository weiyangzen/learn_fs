# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_status_v1beta1.yaml

Purpose: beta1 input with legacy status list but no preservation annotation.

Important content: v1beta1 content with ready flag, group snapshot handle, and `status.volumeSnapshotHandlePairList` entries containing only snapshot and volume handles.

Control flow: converter should rename the legacy pair list to `status.volumeSnapshotInfoList` without adding beta2-only fields.

State and persistence: models native beta1 status that never passed through beta2 downgrade.

Dependencies and integration: paired with `no_annotation_status_v1beta2.yaml`.

Risks and test signals: verifies non-annotated upgrade remains lossy and does not invent creation/ready/restore per-entry values.
