# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/annotation_status_v1beta2.yaml

Purpose: beta2 source fixture with detailed per-volume snapshot status used for downgrade testing.

Important content: v1beta2 `VolumeGroupSnapshotContent`, empty annotations, ready and group handle status, and `status.volumeSnapshotInfoList` entries with creation time, ready flag, restore size, snapshot handle, and volume handle.

Control flow: converter serializes this detailed list into an annotation, strips entry-level beta2-only fields for beta1 status, and renames the list.

State and persistence: represents rich beta2 API state before downgrade.

Dependencies and integration: paired with the expected beta1 fixture.

Risks and test signals: ensures downgrade path has source data for all fields that need preservation.
