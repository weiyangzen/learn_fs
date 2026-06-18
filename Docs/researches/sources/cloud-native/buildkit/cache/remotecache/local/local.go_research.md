# sources/cloud-native/buildkit/cache/remotecache/local/local.go

## Purpose

This file implements the `local` remote cache backend. It exports and imports cache manifests and blobs through a client session content store rooted at a user-provided local directory.

## Important APIs, Types, and Functions

- Attribute constants define `digest`, `src`, `dest`, `image-manifest`, and `oci-mediatypes`.
- `ResolveCacheExporterFunc` parses `dest`, media-type, and compression attributes, obtains a session content store, and returns a generic remote cache exporter.
- `ResolveCacheImporterFunc` parses `digest` and `src`, obtains a session content store, looks up the root descriptor size, and returns a generic remote cache importer.
- `getContentStore` resolves the active session and wraps `sessioncontent.NewCallerStore`.
- `unlazyProvider.UnlazySession` exposes the session group for later remote materialization.

## Control Flow and State

Exporter resolution requires `dest`, creates a content store ID `local:<dest>`, and delegates all cache graph serialization and content writing to `remotecache.NewExporter`. `oci-mediatypes` defaults to true. `image-manifest` defaults to true unless Docker media types are requested, preserving compatibility with non-OCI output.

Importer resolution requires explicit `digest` and `src`. It locates `local:<src>`, obtains content info for the digest to fill a descriptor, and creates a generic importer over that store. The descriptor media type is intentionally left empty because local `index.json` support is incomplete and the generic importer can infer manifest type from bytes.

State persists in the client-side directory accessed through the session content service. BuildKit itself only retains transient provider wrappers.

## Dependencies and Integration Points

This backend depends on BuildKit session management, session content stores, generic `remotecache.NewExporter`/`NewImporter`, compression attribute parsing, and OCI descriptors. It is used when cache options specify `type=local`.

## Risks and Edge Cases

Both import and export require a live client session; `getContentStore` fails without one. Session selection uses the next session from the session group, with a TODO noting that store support detection should be improved. Content-store acquisition has a five-second timeout and can fail in slow or disconnected clients. The importer requires the digest explicitly; if a user points at a directory without passing the root digest, import cannot proceed.

## Test Signals

This subset contains no direct tests for the local cache backend. Generic cache import/export behavior and integration suites elsewhere are expected to exercise it.
