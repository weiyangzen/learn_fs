# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_no_status_v1beta2.yaml

Purpose: expected v1beta2 result for a minimal beta1 object with no annotation/status.

Important content: v1beta2 API version, same kind/name/spec, and no status.

Control flow: equality target for no-op beta1-to-beta2 conversion.

State and persistence: no status or metadata conversion state beyond APIVersion.

Dependencies and integration: paired with the beta1 minimal fixture.

Risks and test signals: catches accidental creation of empty status or annotation blocks in no-op conversion.
