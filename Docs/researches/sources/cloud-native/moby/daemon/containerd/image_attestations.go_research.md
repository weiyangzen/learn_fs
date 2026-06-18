# sources/cloud-native/moby/daemon/containerd/image_attestations.go

## Purpose
Exposes BuildKit in-toto attestation statements attached to a local OCI index image for a requested platform.

## Important APIs, Types, And Functions
- `ImageService.ImageAttestations` implements the daemon image attestation API.
- `localReferrersProvider` adapts local content to `policyimage.ReferrersProvider` with no remote referrer fetching.
- `inTotoPredicateTypeAnnotation` identifies statement layers.

## Control Flow
The method resolves the image, exits early for non-index targets, asks `policyimage.ResolveSignatureChain` to locate the platform image manifest and sibling attestation manifest, reads the attestation manifest, filters layers by `in-toto.io/predicate-type` and requested predicates, and optionally reads statement blobs into `json.RawMessage`.

## State And Persistence
Read-only against local content. It does not cache attestations or fetch remote referrers.

## Dependencies And Integration Points
Depends on containerd content, Moby policy helpers, OCI descriptors, and image backend attestation options. It integrates with `GET /images/{name}/attestations` and BuildKit's sibling-manifest attestation storage model.

## Risks And Edge Cases
Docker Hardened Image and Sigstore referrer discovery are unsupported because `FetchReferrers` is a no-op. Statement bodies are read eagerly when requested, so large attestations can consume memory. Missing platform maps to `errdefs.NotFound`, while absent attestation manifests return nil without error.

## Test Signals
No direct tests in this subset. Expected coverage should include non-index images, missing platform, missing attestation manifest, predicate filtering, and include-statement read errors.
