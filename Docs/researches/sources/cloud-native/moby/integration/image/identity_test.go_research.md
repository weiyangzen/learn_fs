# sources/cloud-native/moby/integration/image/identity_test.go

Purpose: raw HTTP integration tests for image identity fields introduced in newer API versions.

Important APIs and helpers: `TestImageListIdentity`, `TestImageListIdentityRequiresManifests`, `TestImageInspectIdentity`, `TestImageListIdentityAfterInspectWarmup`, `imageListRaw`, and `imageInspectRaw`.

Control flow: tests call versioned raw endpoints directly. List without `identity=1` must omit identity. List with `identity=1&manifests=1` scans manifest image data for object-shaped identity metadata. A missing `manifests=1` parameter must return 400. Inspect on API 1.53 checks identity shape when available. Warmup test inspects an image first, then verifies list with manifests/identity includes matching identity data.

State and persistence: no new images are created; tests read current environment images and may skip if none with identity metadata are available. They exercise cache/warmup behavior between inspect and list.

Dependencies and integration: depends on daemon API version gates, raw request helpers, JSON decoding into generic maps, and image metadata availability from the daemon store.

Risks: environment-dependent skips occur if no suitable identity-bearing images exist. Raw JSON map checks are flexible but can miss typed client regressions.

Test signals: protects API compatibility and parameter validation for image identity metadata in inspect/list responses.
