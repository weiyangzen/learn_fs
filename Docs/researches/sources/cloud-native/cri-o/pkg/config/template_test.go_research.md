# sources/cloud-native/cri-o/pkg/config/template_test.go

This file provides focused tests for config template rendering and runtime map equality. `WriteTemplate` is exercised with `displayAllConfig=true` against a buffer and is expected to succeed. The `RuntimesEqual` tests check map length mismatch, key mismatch, scalar field mismatch, slice field mismatch, and equal values.

State is limited to local runtime maps and the shared `sut` fixture for template rendering. Dependencies are Ginkgo/Gomega, bytes.Buffer, and the config package. Integration signal is narrow but useful: it verifies the generated template parses and executes for default config, and that `RuntimesEqual` detects the differences `template.go` relies on to decide whether runtime config should be commented as default.

Risks not covered include full textual output correctness, every template field's presence, `WorkloadsEqual`, and non-default comment stripping behavior. Those are mostly covered indirectly by tests that serialize config to temp files.
