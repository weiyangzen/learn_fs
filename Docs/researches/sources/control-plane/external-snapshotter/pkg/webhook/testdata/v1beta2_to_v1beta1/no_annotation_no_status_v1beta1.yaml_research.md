# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/no_annotation_no_status_v1beta1.yaml

Purpose: expected beta1 result for downgrading a minimal beta2 object.

Important content: v1beta1 `VolumeGroupSnapshotContent`, name `new-groupsnapshot-demo`, empty spec, and no status or annotations.

Control flow: equality target for no-op beta2-to-beta1 conversion when no `volumeSnapshotInfoList` exists.

State and persistence: minimal object state.

Dependencies and integration: paired with `no_annotation_no_status_v1beta2.yaml`.

Risks and test signals: catches accidental annotation/status creation in no-op downgrade.
