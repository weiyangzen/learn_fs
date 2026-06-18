# sources/control-plane/external-snapshotter/pkg/webhook/convert.go

Purpose: implements conversion for `VolumeGroupSnapshotContent` between `groupsnapshot.storage.k8s.io/v1beta1` and `v1beta2`, preserving v1beta2-only per-snapshot status fields through a reversible annotation when downgrading.

Important APIs/functions: `convertGroupSnapshotCRD`, `convertVolumeGroupSnapshotContentFromV1beta1ToV1beta2`, `convertVolumeGroupSnapshotContentFromV1beta2ToV1beta1`, and `volumeSnapshotInfoAnnotationName`.

Control flow: the top-level converter rejects same-version conversions, unexpected kinds, and unsupported version pairs. Beta1-to-beta2 prefers the serialized annotation when present, installs it into `status.volumeSnapshotInfoList`, removes old `volumeSnapshotHandlePairList`, and clears the annotation. Without annotation it renames the old pair list. Beta2-to-beta1 serializes `volumeSnapshotInfoList` into the annotation, strips beta2-only fields from each entry, writes `status.volumeSnapshotHandlePairList`, and removes `volumeSnapshotInfoList`.

State and persistence: mutates an unstructured object copy that is returned to the API conversion framework. The annotation is durable storage for fields that v1beta1 cannot express.

Dependencies and integration: depends on unstructured Kubernetes object helpers, JSON serialization, metav1 statuses, and the webhook framework in this package.

Risks and test signals: risks include a panic-prone type assertion after JSON unmarshal if annotation content is not a slice, data loss if annotation is removed externally, and mutation of nested map entries in-place. Testdata covers annotation/no-annotation and status/no-status round trips in both directions.
