# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_status_v1beta2.yaml

Purpose: expected v1beta2 output when beta1 legacy status is upgraded without annotation data.

Important content: v1beta2 content retaining top-level status fields and containing `status.volumeSnapshotInfoList` with only snapshot and volume handle pairs.

Control flow: target for rename-only conversion path.

State and persistence: converted status remains less detailed because no preservation annotation was available.

Dependencies and integration: paired with `no_annotation_status_v1beta1.yaml`.

Risks and test signals: catches accidental addition/removal of per-entry fields during rename-only upgrade.
