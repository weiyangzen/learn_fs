## sources/control-plane/rook/cmd/rook/ceph/osd_test.go

Purpose: unit-tests the local helper behavior in `osd.go`, specifically configured device parsing and Ceph secret loading. It does not exercise the full Cobra command paths or Kubernetes/Ceph orchestration.

Important APIs and functions: `TestParseDesiredDevices()` builds `osdcfg.ConfiguredDevice` slices, marshals them to JSON, calls `parseDevices()`, and asserts the resulting `osddaemon.DesiredDevice` fields. `TestReadSecretFile()` calls `readCephSecret()` against missing, env-backed, empty, and populated secret sources.

Control flow: tests are table-like but implemented inline. The parsing test covers multiple devices, invalid negative and zero `OSDsPerDevice`, propagation of `DatabaseSizeMB`, `DeviceClass`, and `MetadataDevice`, and empty input returning an empty slice. The secret test first expects a missing file error, then sets `ROOK_CEPH_SECRET` to verify fallback, creates a temp file to verify empty-file rejection, and finally writes a keyring value to confirm file-based loading.

State and persistence: uses temp files and environment variables, and mutates package-level `clusterInfo.CephCred.Secret`. Because global state is shared with other package tests, future tests should reset env and `clusterInfo` carefully.

Dependencies and integration points: depends on `testify/assert`, Go `encoding/json`, and the OSD config/daemon types whose field names define the JSON contract expected by the operator. These tests provide useful regression signals for CLI/operator data handoff but do not validate downstream Ceph or Kubernetes side effects. Risks include missing coverage for flag validation, filter/path-filter exclusivity, OSD removal boolean parsing, orchestration status updates, and fatal termination behavior.
