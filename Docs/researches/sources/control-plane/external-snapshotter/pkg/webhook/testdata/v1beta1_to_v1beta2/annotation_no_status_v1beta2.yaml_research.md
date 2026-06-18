# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_no_status_v1beta2.yaml

Purpose: expected v1beta2 output for annotated beta1 input without status.

Important content: API version `v1beta2`, same kind/name/spec, empty annotations map, and `status.volumeSnapshotInfoList` with two fully detailed entries including beta2-only creation/ready/restore fields.

Control flow: loaded as the expected object for `annotation_no_status_v1beta1.yaml`.

State and persistence: models the converted v1beta2 status that the API server should store or return.

Dependencies and integration: paired with beta1 source golden file and conversion test glob naming.

Risks and test signals: signals that annotation data takes precedence and annotation cleanup leaves an explicit empty annotations map.
