# sources/cloud-native/nydus-snapshotter/pkg/auth/labels.go

Purpose: provides the highest-priority auth provider that reads registry credentials directly from snapshot labels.

Important APIs and functions: `LabelsProvider` implements `String` and `GetCredentials`; `NewLabelsProvider` constructs it. It looks for `label.NydusImagePullUsername` and `label.NydusImagePullSecret`.

Control flow: `GetCredentials` rejects nil labels, then requires non-empty username and secret labels. On success it returns a `PassKeyChain`.

State and persistence: stateless; all data is carried in `AuthRequest.Labels`.

Dependencies and integration points: depends on `pkg/label` label constants and is first in `buildProviders`, so explicit pull labels override CRI, Docker config, kubelet plugins, and Kubernetes secrets. It is excluded from renewal because labels are only available during pull/snapshot operations.

Risks: no nil request guard is present; callers currently construct a non-nil `AuthRequest`. It does not support token-only auth and treats missing labels as errors, which are later aggregated by `fetchFromProviders`.

Test signals: `labels_test.go` checks successful lookup, base64 conversion, missing-label errors, and missing-username errors.
