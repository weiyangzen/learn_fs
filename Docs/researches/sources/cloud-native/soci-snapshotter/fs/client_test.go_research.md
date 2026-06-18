# sources/cloud-native/soci-snapshotter/fs/client_test.go

Purpose: verifies `OCIArtifactClient.SelectReferrer` behavior for empty and non-empty referrer lists.

Important APIs and flow: `fakeInner` implements `Inner` with no-op content store methods and a `Referrers` method that passes a predefined descriptor slice to the callback. `TestOCIArtifactClientSelectReferrer` constructs an empty case expecting `ErrNoReferrers` and a non-empty case expecting `SelectFirstPolicy` to return the first descriptor. It compares descriptors with `go-cmp`.

State and persistence: fully in-memory fake descriptors. No ORAS repository, registry, or content store is contacted.

Dependencies and integration: exercises the public client wrapper and policy callback shape. It confirms the error sentinel can be checked with `errors.Is`.

Risks and test signals: narrow but useful regression signal for referrer selection. It does not verify that `soci.SociIndexArtifactType` is passed to the underlying `Referrers` call, because the fake ignores the artifact type.
