# sources/cloud-native/buildkit/cache/remotecache/registry/registry.go

## Purpose

This file implements the `registry` remote cache backend. It exports cache manifests to container registries, imports cache manifests from registries, supports insecure registry configuration, and annotates imported layer descriptors with distribution-source metadata for efficient later pulls and snapshot labels.

## Important APIs, Types, and Functions

- `canonicalizeRef` validates and normalizes registry references, applying a default tag.
- `ResolveCacheExporterFunc` parses compression and media-type attributes, resolves a pusher, and returns a generic cache exporter over the registry pusher.
- `ResolveCacheImporterFunc` resolves a registry reference, creates a fetcher, wraps it in `withDistributionSourceLabel`, and returns a generic cache importer.
- `withDistributionSourceLabel` implements `remotecache.DistributionSourceLabelSetter` and snapshot label helpers.
- `registryConfig` swaps in plain HTTP/insecure registry hosts when `registry.insecure=true`.

## Control Flow and State

Export resolution canonicalizes `ref`, parses `oci-mediatypes`, `image-manifest`, `registry.insecure`, and compression attributes, then constructs a resolver scoped for push. It creates a pusher and delegates cache manifest construction and upload to `remotecache.NewExporter`.

Import resolution canonicalizes the same reference, creates a resolver scoped for pull, resolves the reference to a descriptor, and builds a limited fetcher provider. The provider wrapper records distribution source labels in the local content store and injects `containerd.io/distribution.source.ref` annotations into descriptors during generic cache import. It can also produce inherited snapshot labels, including estargz labels and target-ref labels.

Persistent state lives in the target registry. Local content state may be updated with distribution-source labels so later snapshot/content operations know where blobs came from.

## Dependencies and Integration Points

The backend uses containerd resolver, fetcher, pusher, content, snapshot label, and Docker distribution label APIs. It integrates with BuildKit resolver pools, session-authenticated registry access, generic remote cache import/export, compression parsing, and estargz snapshot labeling.

## Risks and Edge Cases

Invalid or missing refs fail early. `registry.insecure=true` replaces host configuration for the reference domain and sets both insecure and plain HTTP, which is useful for tests but sensitive in production. The importer ignores errors when setting source labels because layers may not exist locally; failures there do not stop import. `SnapshotLabels` checks `len(descs) < index`, which does not guard `index == len(descs)` and could panic if called with an out-of-range equal index.

## Test Signals

No direct tests for this file are present in the subset. It is indirectly exercised by client integration tests that push/pull images and by broader cache import/export tests outside this assignment.
