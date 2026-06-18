# sources/cloud-native/nydus-snapshotter/pkg/auth/labels_test.go

Purpose: tests label-sourced credentials and base64 encode/decode helpers.

Important APIs and functions: `TestFromLabels` constructs maps using `label.NydusImagePullUsername` and `label.NydusImagePullSecret`, calls `NewLabelsProvider().GetCredentials`, `PassKeyChain.ToBase64`, and `FromBase64`.

Control flow: the test checks a successful label lookup, verifies encoded `mock:mock`, decodes it back, then checks empty labels and secret-only labels return nil credentials with errors.

State and persistence: no external state; pure unit test.

Dependencies and integration points: exercises `pkg/label` constants and `keychain.go` base64 helpers.

Risks and gaps: no coverage for nil `AuthRequest`, nil labels, empty secret, empty username, invalid base64, colon-containing passwords, or token-based keychains.

Test signals: confirms the label provider's normal success path and basic failure behavior.
