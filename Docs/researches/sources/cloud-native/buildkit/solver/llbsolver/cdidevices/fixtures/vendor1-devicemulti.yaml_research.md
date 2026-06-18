<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-devicemulti.yaml -->
## sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-devicemulti.yaml

Purpose: CDI fixture for first-device, wildcard, class, and auto-allow behavior on a multi-device kind.

Important fields: `kind: "vendor1.com/devicemulti"` with devices `foo`, `bar`, `baz`, and `qux`; each injects a distinct env var. Device `baz` is annotated with BuildKit class `class1`; the spec has auto-allow enabled.

Control flow and state: static YAML used by CDI cache tests. Device order matters for the manager's "first device of kind" resolution path.

Dependencies and integration: `manager_test.go` expects `vendor1.com/devicemulti` with no name to resolve to the first matching device, wildcard to return all four devices, and class lookup to include `baz`.

Risks and test signals: reordering devices changes first-device expectations. The fixture covers dedup and class fallback combined with qualified CDI names.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-devicemulti.yaml -->
