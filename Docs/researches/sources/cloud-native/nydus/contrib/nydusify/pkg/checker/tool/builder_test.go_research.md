# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/builder_test.go

Purpose: validates `Builder` initialization and `Check` command construction.

Important APIs and flow: `TestNewBuilder` checks binary path and default streams. `TestBuilderCheck/success` creates a temporary shell script that records its arguments, injects buffer streams, invokes `Check`, and asserts exact argument order. `TestBuilderCheck/command failed` uses a script that exits nonzero and expects an error.

State and persistence: uses temporary directories and writes fake executable scripts plus an argument log. No external Nydus binary is required.

Dependencies and integration: depends on `testify/require`, `bytes`, `os`, and `filepath`. It tests the wrapper boundary rather than real bootstrap parsing.

Risks and test signals: strong signal for CLI argument regression. It does not assert stdout/stderr content propagation beyond stream assignability and does not cover missing binary behavior separately from nonzero exit.
