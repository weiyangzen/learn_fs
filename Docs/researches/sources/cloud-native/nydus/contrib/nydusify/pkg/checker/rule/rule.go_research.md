# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/rule.go

Purpose: defines the minimal checker rule contract used by the `checker/rule` package.

Important APIs and flow: `type Rule interface` requires `Validate() error` and `Name() string`. Implementations such as `ManifestRule` and filesystem rules can be registered or run polymorphically by the checker without exposing implementation-specific fields.

State and persistence: none. This file contains only an interface and has no side effects.

Dependencies and integration: no imports. The integration point is package-level: any validation rule in `nydusify` must return a human-readable name and signal failure with an error.

Risks and test signals: the contract is intentionally narrow, so compatibility risk is low. It does not model context, logging, or severity, so callers must handle cancellation and reporting outside the interface.
