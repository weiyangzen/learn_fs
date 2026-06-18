# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_no_status_v1beta1.yaml

Purpose: beta1 golden input for converting an annotated `VolumeGroupSnapshotContent` with no status into v1beta2.

Important content: API version `groupsnapshot.storage.k8s.io/v1beta1`, kind `VolumeGroupSnapshotContent`, name `new-groupsnapshot-demo`, empty spec, and `groupsnapshot.storage.kubernetes.io/volume-snapshot-info-list` annotation containing two JSON entries with snapshot handle, volume handle, creation time, ready flag, and restore size.

Control flow: used by `TestFromBeta1ToBeta2`; the converter must deserialize the annotation, create `status.volumeSnapshotInfoList`, and remove the annotation.

State and persistence: represents persisted CRD metadata with conversion-preservation data stored only in an annotation.

Dependencies and integration: paired with `annotation_no_status_v1beta2.yaml`.

Risks and test signals: verifies annotation-driven restoration when beta1 has no status field. It also depends on annotation JSON being valid and shaped as a slice.
