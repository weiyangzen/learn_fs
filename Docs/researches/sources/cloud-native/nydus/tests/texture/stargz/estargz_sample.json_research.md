# sources/cloud-native/nydus/tests/texture/stargz/estargz_sample.json

Purpose: fixture metadata describing a small eStargz/stargz file layout for tests.

Important APIs/types/functions: JSON object with `version: 1` and `entries`. Entries cover a directory `bin/`, regular files `bin/busybox`, `lib/ld-musl-x86_64.so.1`, `.prefetch.landmark`, and hardlink `bin/busybox2`. Regular files include size, modtime, mode, offset, `NumLink`, `digest`, and `chunkDigest`.

Control flow: none; tests parse it as data.

State and persistence: static test fixture only.

Dependencies and integration points: likely consumed by stargz/eStargz conversion or metadata tests to verify TOC parsing, hardlink handling, offsets, and prefetch landmark behavior. Digest strings use OCI-style `sha256:<hex>` format.

Risks: fixture accuracy matters because offsets and digests encode assumptions about a paired compressed sample. If the sample blob changes without updating this JSON, tests may fail or validate stale behavior. The JSON includes a trailing two-space ending after the final brace, which parsers tolerate.

Test signals: provides coverage for directory, regular file, hardlink, digest, chunk digest, and prefetch landmark entries in stargz tests.
