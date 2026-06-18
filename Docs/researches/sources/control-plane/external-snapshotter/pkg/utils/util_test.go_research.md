# sources/control-plane/external-snapshotter/pkg/utils/util_test.go

Purpose: unit-tests broad utility behavior used by snapshot controllers.

Important APIs/functions: `TestRemoveString`, `TestGetSecretReference`, `TestRemovePrefixedCSIParams`, default annotation tests, and `TestShouldEnqueueContentChange`.

Control flow: table tests validate finalizer slice removal, secret reference template pairing and DNS validation, reserved CSI parameter stripping/erroring, snapshot and group default-class annotations, and update-event filtering across spec, status, finalizer, managed-field, sidecar annotation, external annotation, resync, and ready-transition scenarios.

State and persistence: test state is in-memory CRD/core objects; no Kubernetes client calls are made in this file.

Dependencies and integration: depends on snapshot CRDs, core API objects, metadata, pointer helpers, reflection, and utility constants.

Risks and test signals: strong signal for preventing controller self-update loops and reserved parameter leakage to CSI drivers. Gaps include `GetCredentials`, group secret reference templating, many finalizer/deletion predicates, logging helpers, and malformed resource versions.
