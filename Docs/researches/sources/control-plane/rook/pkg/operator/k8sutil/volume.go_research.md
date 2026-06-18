# sources/control-plane/rook/pkg/operator/k8sutil/volume.go

## Purpose
`volume.go` converts arbitrary filesystem paths into Kubernetes DNS-1123-compatible volume names.

## Important APIs, Types, and Functions
`PathToVolumeName(path string) string` lowercases ASCII letters, preserves digits and lowercase letters, replaces all other runes with hyphens, trims leading/trailing hyphens, and truncates names longer than 63 characters with beginning/end samples plus an eight-character hash from `Hash()`.

## Control Flow, State, and Persistence
The function is pure. Long-name handling uses `validation.DNS1123LabelMaxLength` and a stable hash to reduce collisions.

## Dependencies and Integration Points
It depends on Kubernetes validation constants and package-level `Hash()` from `k8sutil.go`. It integrates with pod volume construction where host paths or arbitrary names must become legal Kubernetes volume names.

## Risks
Consecutive invalid characters become consecutive hyphens and are not collapsed. Inputs containing only invalid/trimmed characters can produce an empty string. Non-ASCII letters are converted to hyphens rather than transliterated.

## Test Signals
`volume_test.go` covers slashes, casing, digits, punctuation, currency/full-width symbols, and long-name hashing. Empty and all-invalid inputs are not covered.
