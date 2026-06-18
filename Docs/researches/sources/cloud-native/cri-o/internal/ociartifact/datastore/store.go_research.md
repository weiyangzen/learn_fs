# sources/cloud-native/cri-o/internal/ociartifact/datastore/store.go

## Purpose
Extends the OCI artifact store with data retrieval: pulling artifacts, locating them by digest/name, reading artifact layer blobs into memory, enforcing size limits, and verifying layer digests.

## Important APIs and Control Flow
`ArtifactData` wraps raw bytes. `Store` embeds `ociartifact.Store`, stores system context, and uses an injectable `Impl`. `New` creates a main artifact store without additional read-only stores. `PullOptions` controls config media type placeholder, max in-memory size, and copy options. `PullData` sanitizes options, resolves a docker reference, pulls through `ociartifact.Store.Pull`, then loads layer data by manifest digest. `artifactData` resolves digest/name, opens an OCI layout image source, iterates manifest layer infos, reads each blob, and enforces cumulative size. `readBlob` checks known blob size, reads at most `max+1`, and verifies the digest with `verifyDigest`. `getByNameOrDigest` accepts full or short digests of at least 3 chars, otherwise resolves fully qualified named candidates and compares reference/canonical name. `getImageReference` normalizes and tags image names before creating docker references.

## State, Persistence, Dependencies, and Integration
Artifact bytes remain in memory; blobs persist in the embedded OCI artifact store under `<root>/artifacts`. Depends on containers/image, libimage copy options, blob info cache, manifest APIs, and `ociartifact.Store`. This is likely used by CRI-O features that need small artifact payloads such as profiles/config snippets.

## Risks and Test Signals
The `EnforceConfigMediaType` option is defined but not enforced in this file. Short digest matching can be ambiguous because it returns the first listed match. Size enforcement is both per-layer and cumulative, but a `ReadAll` error from `LimitReader` must be interpreted carefully. Digest verification is strong. Tests cover parse and docker-reference failure injection only.
