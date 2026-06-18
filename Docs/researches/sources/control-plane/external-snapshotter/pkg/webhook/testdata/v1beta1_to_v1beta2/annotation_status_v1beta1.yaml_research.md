# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_status_v1beta1.yaml

Purpose: beta1 golden input where both the legacy status pair list and preservation annotation are present.

Important content: v1beta1 `VolumeGroupSnapshotContent` with ready and group handle status, `status.volumeSnapshotHandlePairList`, and annotation JSON containing the richer beta2 `volumeSnapshotInfoList` entries.

Control flow: conversion should use annotation content for beta2 status, remove the legacy pair list, preserve other status fields, and clear the annotation.

State and persistence: represents a downgraded object that carried beta2-only fields in metadata while retaining beta1-compatible status.

Dependencies and integration: paired with `annotation_status_v1beta2.yaml`.

Risks and test signals: verifies reversibility path from beta2 downgrade back to beta2 upgrade. It signals that annotation data can override/augment existing legacy status.
