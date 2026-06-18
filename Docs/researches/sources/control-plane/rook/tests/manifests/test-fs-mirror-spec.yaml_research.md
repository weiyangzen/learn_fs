<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-fs-mirror-spec.yaml -->
# sources/control-plane/rook/tests/manifests/test-fs-mirror-spec.yaml

Purpose: YAML fragment for enabling Ceph filesystem mirroring in a test manifest. It is not a full resource and is intended for composition or patching.

Important structure: under `spec.mirroring`, it sets `enabled: true`, adds a snapshot schedule for `/` every `24h`, and a snapshot retention entry for `/` with duration string `"h 24"`.

State, persistence, and integration: when merged into a `CephFilesystem`, it causes Rook/Ceph to manage mirroring and snapshot scheduling metadata. Dependencies include a consumer that inserts the fragment into a valid filesystem CR. Risks include fragment-only validity and the unusual retention duration format, which may intentionally exercise validation behavior. Test signals are accepted CR reconciliation and fs-mirror daemon/status checks in cluster validation scripts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-fs-mirror-spec.yaml -->
