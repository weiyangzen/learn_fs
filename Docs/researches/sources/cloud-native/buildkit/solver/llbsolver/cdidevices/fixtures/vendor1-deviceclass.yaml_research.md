<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-deviceclass.yaml -->
## sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-deviceclass.yaml

Purpose: CDI fixture for device class annotation lookup.

Important fields: declares `kind: "vendor1.com/deviceclass"`, a spec annotation `foo.bar.baz: FOO`, auto-allow annotation, and four devices. `foo` and `bar` carry `org.mobyproject.buildkit.device.class: class1`, `baz` carries `class2`, and `qux` has no BuildKit class annotation.

Control flow and state: static test data read into the CDI cache. It contributes both spec-level and device-level annotations that `deviceAnnotations` merges.

Dependencies and integration: `manager_test.go` expects class lookup for `class1` to find `vendor1.com/deviceclass=foo` and `vendor1.com/deviceclass=bar` from this file.

Risks and test signals: changing names or annotations will alter class-based device resolution tests. It also helps cover that unrelated spec annotations do not interfere with BuildKit-specific annotations.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-deviceclass.yaml -->
