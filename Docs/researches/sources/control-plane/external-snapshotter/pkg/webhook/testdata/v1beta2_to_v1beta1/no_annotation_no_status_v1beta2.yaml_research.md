# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/no_annotation_no_status_v1beta2.yaml

Purpose: minimal beta2 source fixture for downgrade conversion.

Important content: v1beta2 `VolumeGroupSnapshotContent`, same name and empty spec, with no status.

Control flow: converter should leave object content unchanged except APIVersion assigned by framework.

State and persistence: no conversion preservation state.

Dependencies and integration: paired with minimal beta1 expected fixture.

Risks and test signals: verifies no-op downgrade baseline.
