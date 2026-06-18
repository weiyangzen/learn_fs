<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/identifiers/validate.go -->
# sources/cloud-native/containerd/pkg/identifiers/validate.go

Purpose: validate containerd identifiers against length and character rules.

Important APIs and constants: `Validate` plus unexported maximum length and lazy regular expression. Valid identifiers must be non-empty, no more than 76 characters, and match the configured identifier regexp.

Control flow and state: `Validate` checks empty string, length, and regexp match in order, returning errors wrapped with `errdefs.ErrInvalidArgument`.

Dependencies and integration: uses containerd `internal/lazyregexp` and `errdefs` so callers can classify invalid argument errors.

Risks and test signals: regexp changes affect API compatibility for IDs. Tests cover representative valid and invalid strings plus `errdefs.IsInvalidArgument`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/identifiers/validate.go -->
