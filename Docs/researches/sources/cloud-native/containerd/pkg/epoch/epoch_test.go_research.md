<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/epoch/epoch_test.go -->
# sources/cloud-native/containerd/pkg/epoch/epoch_test.go

Purpose: tests for `SOURCE_DATE_EPOCH` parsing and environment access.

Important APIs and functions: `TestSourceDateEpoch` covers unset, empty, valid UTC/non-UTC time conversion, invalid env values, and direct parse errors.

Control flow and state: tests set/unset environment values, call `SourceDateEpoch` and `ParseSourceDateEpoch`, and assert nil/error/time equality expectations.

Dependencies and integration: uses testify `require` and standard `os/time`.

Risks and test signals: confirms empty environment is treated as unset by `SourceDateEpoch`, while direct parsing of empty string is an error.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/epoch/epoch_test.go -->
