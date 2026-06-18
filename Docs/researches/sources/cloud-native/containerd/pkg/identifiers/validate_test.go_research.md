<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/identifiers/validate_test.go -->
# sources/cloud-native/containerd/pkg/identifiers/validate_test.go

Purpose: tests for identifier validation rules and error classification.

Important APIs and functions: `TestValidIdentifiers` and `TestInvalidIdentifiers`.

Control flow and state: table tests call `Validate` for accepted and rejected inputs. Invalid cases assert an error is returned and that `errdefs.IsInvalidArgument` classifies it.

Dependencies and integration: validates both local regexp/length rules and cross-package errdefs wrapping behavior.

Risks and test signals: the examples define the practical identifier contract for callers. Boundary length and character-class coverage are important when updating validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/identifiers/validate_test.go -->
