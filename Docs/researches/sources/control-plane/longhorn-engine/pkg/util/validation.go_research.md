## sources/control-plane/longhorn-engine/pkg/util/validation.go

### Purpose
`validation.go` vendors Kubernetes-style qualified-name and DNS-1123 subdomain validation for Longhorn label keys.

### Important APIs, Types, And Functions
Constants define qualified-name regex fragments, error messages, maximum name length, DNS label/subdomain regexes, and max subdomain length. `IsQualifiedName` validates optional `prefix/name` strings. `IsDNS1123Subdomain` validates DNS prefixes. `MaxLenError`, `RegexError`, `EmptyError`, and `prefixEach` format error messages.

### Control Flow
`IsQualifiedName` splits on `/`, validates optional prefix through DNS-1123 rules, validates non-empty and max-length name parts, then applies the qualified-name regexp. More than one slash returns a combined qualified-name error. DNS validation checks length then regex.

### State, Persistence, And Dependencies
There is no state beyond compiled regex values. Dependencies are `fmt`, `regexp`, and `strings`.

### Integration Points
`ParseLabels` in `util.go` uses `IsQualifiedName` for label keys. The logic mirrors Kubernetes validation, making Longhorn labels compatible with Kubernetes naming expectations.

### Risks
The file is copied code; future Kubernetes validation changes will not arrive automatically. Error text may be used in tests or user output, so wording changes can be externally visible.

### Test Signals
Tests should include valid names, invalid start/end characters, too-long names, valid and invalid DNS prefixes, empty parts, and multiple slash cases.
