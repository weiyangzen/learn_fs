# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_no_status_v1beta1.yaml

Purpose: minimal beta1 conversion input with no annotation and no status.

Important content: v1beta1 `VolumeGroupSnapshotContent`, name `new-groupsnapshot-demo`, and empty spec.

Control flow: converter should make no status changes beyond the framework-updated API version.

State and persistence: represents an empty persisted CRD object.

Dependencies and integration: paired with `no_annotation_no_status_v1beta2.yaml`.

Risks and test signals: establishes the no-op conversion baseline.
