# sources/cloud-native/soci-snapshotter/fs/client.go

Purpose: provides an OCI artifact/referrers client abstraction used to find SOCI index artifacts attached to an image manifest.

Important APIs and flow: `IndexSelectionPolicy` chooses one descriptor from a descriptor list; `SelectFirstPolicy` returns `descs[0]`. `ReferrersClient` exposes `SelectReferrer`. `ReferrersCaller` abstracts ORAS `Repository.Referrers` for tests. `Inner` combines ORAS content storage and referrers. `OCIArtifactClient` embeds `Inner`. `SelectReferrer` calls `AllReferrers`, maps fetch failures, returns `ErrNoReferrers` for an empty list, and otherwise applies the supplied policy. `AllReferrers` calls `Referrers` with `soci.SociIndexArtifactType` and appends all pages passed to the callback.

State and persistence: no state beyond the embedded remote/content store. It reads registry referrer metadata and does not write artifacts.

Dependencies and integration: used by `fs.findSociIndexDescReferrer` when SOCI v1 referrer discovery is enabled. Depends on ORAS content/referrers interfaces, OCI descriptors, and SOCI artifact type constants.

Risks and test signals: `SelectFirstPolicy` assumes the list is non-empty and is safe only after `SelectReferrer` checks length. Selection policy quality determines which index is mounted when multiple SOCI indexes exist. Tests cover empty referrers and first-descriptor selection with a fake ORAS inner, but not pagination errors, artifact type filtering, or richer selection policies.
