# sources/cloud-native/ostree/src/libostree/ostree-metalink.c

## Purpose
This file implements synchronous Metalink fetching for OSTree. It downloads a metalink document, parses the requested file entry, validates size and SHA-256/SHA-512 checksums, and tries listed HTTP(S) target URLs until one succeeds.

## Important APIs and Control Flow
`_ostree_metalink_new(fetcher, requested_file, max_size, uri, n_network_retries)` stores a fetcher, requested filename, metalink URI, maximum size, and retry count. `_ostree_metalink_request_sync()` creates a private main context, downloads the metalink into memory with `_ostree_fetcher_request_uri_to_membuf()`, parses it with `GMarkupParseContext`, then calls `try_metalink_targets()`. The parser is a state machine over `metalink/files/file/size/verification/hash/resources/url`, with passthrough state for unknown or ignored elements. Only URLs with `protocol` `http` or `https` are collected. `try_one_url()` downloads a candidate target, checks exact byte size, and verifies SHA-512 preferentially, then SHA-256.

## State, Dependencies, Integration, Risks, and Tests
Persistent state is none; request state includes parsed size, hashes, URL array, last error, and parser state. Dependencies include `OstreeFetcher`, fetcher URI helpers, GMarkup, GBytes, and GChecksum. Integration points are summary or content fetch paths using metalink indirection. Risks include strict XML shape assumptions, lowercase-only hex validation, collecting URLs in document order without preference sorting, full in-memory downloads capped only by `max_size`, and parser text callbacks overwriting hash text if split unexpectedly. Tests should cover missing file entries, unknown elements, bad sizes, invalid hash length/characters, multiple URLs with fallback, checksum mismatch, non-HTTP filtering, and max-size enforcement.
