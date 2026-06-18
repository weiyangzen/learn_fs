# sources/cloud-native/nydus-snapshotter/pkg/stargz/testdata/stargz.index.json lines 1-10123

## Scope And Purpose

This chunk is the opening portion of a large eStargz TOC JSON fixture. It starts the top-level object with `"version": 1` and the `"entries"` array, then lists the first 1,067 complete filesystem entries plus the beginning of entry 1,068. The span begins at `bin/` and reaches `usr/lib/x86_64-linux-gnu/libdebconfclient.so.0` as the last complete entry; line 10122 starts `usr/lib/x86_64-linux-gnu/libdebconfclient.so.0.0.0`, and line 10123 only records its `"type": "reg"`, so this chunk is not a standalone valid JSON document.

The file is test data for the `pkg/stargz` resolver path. Runtime code extracts a tar member named `stargz.index.json` from an eStargz TOC gzip stream, persists it under snapshot storage, and passes it to `nydus-image create --source-type stargz_index` to generate Nydus bootstrap/blob metadata for stargz-compatible layers. This fixture captures the JSON shape and realistic Debian/Ubuntu-like filesystem density that conversion code must tolerate.

## Data Model In This Chunk

Each complete entry is a TOC record with fields matching the stargz/estargz index contract:

- Common metadata: `name`, `type`, `modtime`, `mode`, and `NumLink`.
- Regular-file metadata: `size`, compressed blob `offset`, and uncompressed content `digest`.
- Link metadata: `linkName` for symlinks and hardlinks.
- Ownership metadata appears sparsely as `gid` in this span; no `uid`, xattr, `chunkOffset`, or `chunkSize` fields appear in lines 1-10123.

The observed complete-entry counts in this chunk are 848 regular files, 108 directories, 110 symlinks, and 2 hardlinks. There are 841 `offset` fields and 847 `digest` fields; digest count exceeds offset count because empty regular files have the well-known empty SHA-256 digest but no compressed payload offset. The maximum observed offset in the complete entries is `18743676`, reached by `usr/lib/x86_64-linux-gnu/libdb-5.3.so`.

The path distribution is broad enough to exercise root-level directories and many package-managed files: `bin`, `boot`, `dev`, `etc`, `home`, `lib`, `lib64`, `media`, `mnt`, `opt`, `proc`, `root`, `run`, `sbin`, `srv`, `sys`, `tmp`, and `usr`. Dense areas include 73 `bin` entries, 156 `etc` entries, 219 `lib` entries, 202 `usr/bin` entries, 333 `usr/lib` entries, and 255 `usr/lib/x86_64-linux-gnu/gconv` entries.

## Important Integration Code

The key runtime integration is in `pkg/stargz/resolver.go`. `TocFileName` is set to `stargz.index.json`, `Blob.GetTocOffset()` delegates footer parsing to `estargz.OpenFooter`, and `Blob.ReadToc()` reads the blob range from the TOC offset to the 47-byte footer, opens it as gzip, disables gzip multistream, reads the first tar entry, validates that its name is `stargz.index.json`, then returns the tar member content as an `io.Reader`.

The filesystem adaptor in `pkg/filesystem/stargz_adaptor.go` consumes this output. `PrepareStargzMetaLayer()` calls `blob.ReadToc()`, writes the returned reader into `<storagePath>/stargz.index.json` with mode `0440`, and runs `nydus-image create --source-type stargz_index --bootstrap <tmp> --blob-id <layer-digest-hex> --repeatable --disable-check --fs-version 6 --chunk-size 0x400000 --blob-meta <path> <storagePath>/stargz.index.json`. The resulting bootstrap is renamed to the digest-derived bootstrap path and chmodded `0440`.

`resolver_test.go` validates the lower-level transport and archive assumptions using `testdata/stargzfooter.bin` and `testdata/stargztoc.bin`: it resolves a mock blob, reads the 47-byte footer, parses the TOC offset, downloads the TOC range, opens gzip/tar, and asserts that the first tar header name is `stargz.index.json`. The JSON fixture here documents the content shape that the asserted tar member carries.

## Control Flow And State Behavior

This JSON itself has no executable control flow, but it drives conversion control flow through ordered TOC entries:

1. The resolver fetches only blob ranges needed for the footer and TOC, not the full stargz layer.
2. The TOC tar member content is materialized as `stargz.index.json` in snapshot storage.
3. `nydus-image` parses the JSON as a `stargz_index` source and maps every TOC entry to Nydus bootstrap and blob-meta records.
4. Later layer preparation and merge logic use those generated bootstraps/blob-meta files rather than repeatedly parsing the JSON fixture.

The persistent artifacts are the saved TOC JSON, generated bootstrap, and generated blob-meta. For fscache, blob-meta is deliberately written into the snapshot work directory rather than the cache directory. The fixture's offsets, digests, modes, symlinks, and hardlinks therefore affect durable conversion output and later lazy-read addressing into the original stargz blob.

## Dependencies And External Contracts

The fixture depends on the eStargz TOC JSON schema used by `containerd/stargz-snapshotter/estargz`, Go gzip/tar readers, OCI-style `sha256:` digests, Unix mode bits, RFC3339 UTC timestamps, and Nydus `nydus-image` support for `--source-type stargz_index`.

The surrounding code also depends on registry range-read behavior. `Resolver.resolve()` creates an `io.SectionReader` backed by HTTP `Range` GETs, and `getSize()` infers blob size from `Content-Range`. Correct TOC conversion depends on registries returning accurate ranges, the footer pointing to the right TOC offset, gzip/tar decoding exactly one TOC member, and the JSON preserving the offset/digest values that locate and verify file content.

## Risks And Edge Cases

- Lines 1-10123 end mid-entry, so parsing this chunk alone as JSON will fail. Whole-file consumers need the remaining lines.
- The fixture uses `NumLink` with capitalized JSON spelling. Schema readers that only expect lower-case keys could silently drop link-count metadata.
- Empty regular files can have a digest without an offset; conversion code must not assume every regular file has a payload offset.
- Symlinks and hardlinks carry `linkName` instead of size/offset/digest. Hardlink handling is especially important because `bin/uncompress` links to `bin/gunzip` and similar metadata must not be converted into duplicate regular-file payloads.
- Sparse ownership fields such as `gid` appear only on selected entries. Consumers must default missing ownership fields consistently while preserving explicit group IDs.
- Offsets are monotonic in this observed span but should still be treated as data from the TOC, not recomputed from uncompressed file sizes. Compressed byte ranges and uncompressed sizes are different domains.
- The adaptor currently passes a fixed `--chunk-size 0x400000` and has a FIXME about detecting chunk size and compressor from the estargz TOC file. This fixture lacks explicit chunk metadata in the opening span, so converter assumptions around unchunked or whole-file records are compatibility-sensitive.
- Because `PrepareStargzMetaLayer()` writes the TOC before running `nydus-image`, partial writes or interrupted conversions can leave a saved `stargz.index.json` without a matching converted bootstrap.

## Test Signals

Useful validation for this chunk includes:

- Confirm the full fixture parses as JSON and the top-level `version` remains `1`.
- Validate entry counts and type coverage for the first 10,123 lines after merging with adjacent chunks: directories, regular files, symlinks, hardlinks, sparse `gid`, and the incomplete boundary entry.
- Round-trip `testdata/stargztoc.bin` through gzip/tar and assert the member name is `stargz.index.json`, then compare the extracted content against this JSON fixture when appropriate.
- Run `go test ./pkg/stargz` to cover footer parsing, range reads, gzip/tar decoding, and TOC-member name validation.
- Exercise `PrepareStargzMetaLayer()` or an integration harness with `nydus-image create --source-type stargz_index` to ensure modes, symlinks, hardlinks, empty files, digests, and offsets produce stable bootstrap/blob-meta output.
- Add negative tests for malformed or truncated JSON, missing `offset` on non-empty regular files, invalid digest strings, wrong TOC tar member name, missing `Content-Range`, and registries that do not honor byte ranges.
