# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_status_v1beta2.yaml

Purpose: expected v1beta2 output for beta1 input with both annotation and status.

Important content: v1beta2 content with ready and group handle retained, annotation cleared to `{}`, and `status.volumeSnapshotInfoList` populated with full entries.

Control flow: used as semantic equality target after beta1-to-beta2 conversion.

State and persistence: represents restored beta2 status after a reversible downgrade/upgrade sequence.

Dependencies and integration: paired with `annotation_status_v1beta1.yaml`.

Risks and test signals: confirms non-list status fields survive conversion and legacy `volumeSnapshotHandlePairList` is not retained.
