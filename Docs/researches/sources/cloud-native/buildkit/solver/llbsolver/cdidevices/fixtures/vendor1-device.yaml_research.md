<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-device.yaml -->
## sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-device.yaml

Purpose: CDI test fixture defining one concrete `vendor1.com/device=foo` device.

Important fields: `cdiVersion: "0.6.0"`, `kind: "vendor1.com/device"`, one `devices` entry named `foo`, and a container edit that injects `FOO=injected`.

Control flow and state: static YAML loaded by `cdi.NewCache(cdi.WithSpecDirs("./fixtures"))` in tests. It does not execute code or persist runtime state.

Dependencies and integration: consumed by the CDI library and `cdidevices.Manager` tests to validate exact device-name matching and annotation-derived auto-allow behavior.

Risks and test signals: fixture correctness depends on CDI schema compatibility. Its spec-level `org.mobyproject.buildkit.device.autoallow: true` annotation exercises manager annotation merging and auto-allow detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-device.yaml -->
