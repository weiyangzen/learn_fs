<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/suggest/error.go -->
# sources/cloud-native/buildkit/util/suggest/error.go

Purpose: attaches “did you mean” suggestions to errors based on Levenshtein distance against allowed options.

Important APIs and types: `Search`, `WrapError`, `WrapErrorMaybe`, `suggestError`, and `matchCase`.

Control flow: `Search` optionally lowercases the input/options, rejects exact matches as unrelated errors, selects the closest option under distance threshold 3, and preserves broad input casing. `WrapErrorMaybe` returns `(true, wrappedError)` only when a suggestion exists; otherwise it leaves the original error unchanged.

State and persistence: pure string/error transformation.

Dependencies and integration: uses `github.com/agext/levenshtein`. Useful for config/CLI validation.

Risks: fixed distance threshold can miss longer near-matches or suggest short accidental matches. Case restoration only handles all-lower and all-upper input specially.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/suggest/error.go -->
