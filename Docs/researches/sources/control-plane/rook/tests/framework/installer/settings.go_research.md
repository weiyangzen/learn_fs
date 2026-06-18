# sources/control-plane/rook/tests/framework/installer/settings.go

Purpose: this file implements manifest reading from the local tree or GitHub release branches and rewrites the local Rook image tag for test manifests.

Important APIs/types/functions: package regexp `imageMatch`; functions `readManifest`, `buildURL`, `readManifestFromGitHub`, and `readManifestFromURL`.

Control flow: `readManifest` finds the Rook root, reads `deploy/examples/<filename>`, and rewrites `image: docker.io/rook/ceph:<tag>` to `local-build`. `buildURL` handles historical `v1.6` and `v1.7` release paths differently from current `deploy/examples`. `readManifestFromGitHub` constructs a raw GitHub URL, and `readManifestFromURL` retries HTTP GET up to three times before panicking and returns the response body.

State and persistence behavior: read-only except for network I/O. Returned manifest strings later become persisted Kubernetes resources.

Dependencies and integration points: depends on filesystem root discovery, GitHub raw content, HTTP client, regexp image replacement, and installer logger.

Risks: no HTTP status code validation means 404 pages can be treated as manifest content. `defer response.Body.Close()` will panic if all retries fail without a response, though the loop panics on third request error. URL path compatibility is hard-coded for only old releases. Image regexp only matches docker.io rook/ceph lines.

Test signals: local manifest reads, image replacement, previous-version URL construction, and HTTP status/error handling should be covered or observed by upgrade tests.
