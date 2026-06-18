# Research: sources/cloud-native/nydus-snapshotter/pkg/stargz/testdata/stargz.index.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000213`: lines 1-10123, `Docs/researches/chunks/subset-b-000213_research.md`
- `subset-b-000214`: lines 10124-19594, `Docs/researches/chunks/subset-b-000214_research.md`
- `subset-b-000215`: lines 19595-29784, `Docs/researches/chunks/subset-b-000215_research.md`
- `subset-b-000216`: lines 29785-39848, `Docs/researches/chunks/subset-b-000216_research.md`
- `subset-b-000217`: lines 39849-41900, `Docs/researches/chunks/subset-b-000217_research.md`

## Chunk Research

### subset-b-000213: lines 1-10123

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

### subset-b-000214: lines 10124-19594

# sources/cloud-native/nydus-snapshotter/pkg/stargz/testdata/stargz.index.json lines 10124-19594

## Scope And Purpose

This chunk is a partial view of the decompressed eStargz table-of-contents fixture `stargz.index.json`. The file is JSON testdata, not executable code. Its purpose is to provide a realistic `stargz.index.json` payload for the stargz resolver tests under `pkg/stargz`, where the resolver locates the stargz footer, reads the compressed TOC tar member, verifies the member is named `stargz.index.json`, and returns the TOC content to callers.

The assigned line range starts inside the regular-file entry for `usr/lib/x86_64-linux-gnu/libdebconfclient.so.0.0.0` at its `size`, `modtime`, `mode`, `offset`, `NumLink`, and `digest` fields. The first complete entry in this chunk is the symlink `usr/lib/x86_64-linux-gnu/libformw.so.5` at line 10132. The range ends inside the regular-file entry for `usr/share/keyrings/debian-archive-removed-keys.gpg`, stopping at its `modtime` field on line 19594; the remaining `mode`, `offset`, `NumLink`, and `digest` fields appear immediately after the chunk. The final per-file merge lane should reconcile those boundary fragments with adjacent chunks.

Within the complete named entries whose `name` lines fall in this range, this chunk covers 1,012 TOC records: 784 regular files, 206 directories, and 22 symlinks. The paths move from shared libraries in `usr/lib/x86_64-linux-gnu/`, through a large `perl-base` subtree, then `usr/local`, `usr/sbin`, and a broad `usr/share` section containing bash-completion, Debian documentation, common licenses, dpkg metadata, GCC/GDB Python helpers, and Debian keyrings.

## Data Model And Important Fields

The enclosing file has top-level `version: 1` and an `entries` array. Each element models a tar filesystem object in the stargz layer. The important schema-like fields visible in this chunk are:

- `name`: normalized archive path, with directory entries ending in `/`.
- `type`: object kind, primarily `reg`, `dir`, and `symlink` in this range.
- `size`: uncompressed file size for regular-file entries.
- `modtime`: RFC3339 timestamp used to preserve filesystem metadata.
- `mode`: numeric Unix mode. This range includes regular file modes `33188` and `33261`, directory mode `16877`, symlink mode `41471`, and sticky/world-writable directory mode `17917`.
- `offset`: stargz blob byte offset for regular-file payload access.
- `digest`: per-regular-file `sha256:` digest used to verify TOC content identity.
- `linkName`: symlink target for symlink entries.
- `NumLink`: link count metadata, consistently `0` in this fixture slice.

Regular-file entries in this chunk all carry both `offset` and `digest` when the complete record is visible. Directory entries carry metadata only and do not have blob offsets or digests. Symlink entries carry `linkName` and no payload offset. No `chunkDigest`, `chunkOffset`, or `chunkSize` fields appear in the named entries in this range, so this fixture slice represents one TOC entry per regular file rather than explicit sub-file chunk records.

## Path Coverage

The chunk is dominated by Debian/Ubuntu root filesystem content:

- `usr/lib`: 637 named entries, including architecture-specific libraries, `perl-base` modules, Perl `.so` extension modules, Unicode tables, and Perl pod files.
- `usr/share`: 309 named entries, including bash-completion scripts, Debian package docs and copyright files, common license symlinks, dpkg architecture tables, GCC libstdc++ Python helpers, GDB auto-load helpers, and keyrings.
- `usr/sbin`: 55 named entries for administrative commands such as user/group management, service/init helpers, filesystem utilities, and alternatives-managed tools.
- `usr/local`: 11 named entries, mostly empty directory scaffolding plus `usr/local/man -> share/man`.

The largest regular-file payloads visible in this chunk include `usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.22` at 1,566,168 bytes, `usr/lib/x86_64-linux-gnu/perl-base/auto/re/re.so` at 495,120 bytes, `usr/lib/x86_64-linux-gnu/perl-base/unicore/To/NFKCCF.pl` at 398,291 bytes, `usr/lib/x86_64-linux-gnu/libsemanage.so.1` at 248,032 bytes, and `usr/lib/x86_64-linux-gnu/libustr-1.0.so.1.0.4` at 215,040 bytes. The complete regular-file entries whose names are inside this chunk sum to 8,165,824 bytes of uncompressed file content, with monotonically increasing stargz offsets from `19593588` through `22662459` when including the last entry resolved from adjacent boundary context.

## Symlink Semantics

The 22 symlink entries are important because they exercise TOC consumers that must distinguish metadata-only links from regular payload files. Library soname links include `libformw.so.5 -> libformw.so.5.9`, `liblz4.so.1 -> liblz4.so.1.7.1`, `libmenuw.so.5 -> libmenuw.so.5.9`, `libpanelw.so.5 -> libpanelw.so.5.9`, `libpcreposix.so.3 -> libpcreposix.so.3.13.3`, `libstdc++.so.6 -> libstdc++.so.6.0.22`, `libtic.so.5 -> libtic.so.5.9`, and `libustr-1.0.so.1 -> libustr-1.0.so.1.0.4`.

Administrative and documentation symlinks include `usr/local/man -> share/man`, `usr/sbin/addgroup -> adduser`, `usr/sbin/cpgr -> cppw`, `usr/sbin/delgroup -> deluser`, `usr/sbin/rmt -> /etc/alternatives/rmt`, `usr/sbin/vigr -> vipw`, `usr/share/bash-completion/completions/debconf-show -> debconf`, common-license aliases `GFDL -> GFDL-1.3`, `GPL -> GPL-3`, `LGPL -> LGPL-3`, and Debian documentation aliases such as `libgcc1 -> gcc-6-base`, `libncursesw5 -> libtinfo5`, `libstdc++6 -> gcc-6-base`, and `perl-base -> perl`.

These entries are integration signals for snapshotter behavior because lazy filesystem readers must not try to fetch blob ranges for symlinks, but must still surface the correct path, mode, target, and modification time.

## Control Flow And Persistence Behavior

The JSON file itself has no functions or runtime branches. Its effective control flow is imposed by the stargz reader:

1. `Resolver.resolve` obtains a remote blob URL and wraps it in an `io.SectionReader` backed by HTTP range requests.
2. `Blob.GetTocOffset` calls `estargz.OpenFooter` over the section reader to find the TOC offset.
3. `Blob.ReadToc` reads the compressed TOC tar/gzip range from `tocOffset` to `blobSize - FooterSize`, opens a gzip reader, disables multistream processing, reads the first tar header, requires the tar member name to equal `stargz.index.json`, then returns the member body.
4. Downstream TOC consumers parse the returned JSON and use entries like those in this chunk to map paths to metadata, regular-file offsets, and digests.

Persistence is fixture-based. The source file stores stable TOC metadata in the repository, while `resolver_test.go` serves compressed bytes from `testdata/stargztoc.bin` and footer bytes from `testdata/stargzfooter.bin` through a mock range-capable HTTP transport. Any change to this JSON fixture should be coordinated with the compressed TOC binary if tests expect them to represent the same payload.

## Dependencies And Integration Points

This chunk depends on the eStargz TOC schema used by `github.com/containerd/stargz-snapshotter/estargz` and by nydus-snapshotter's `pkg/stargz` resolver. It also mirrors tar filesystem metadata, Unix modes, symlink targets, gzip/tar TOC packaging, and content-addressed digests.

The main local integration points are `sources/cloud-native/nydus-snapshotter/pkg/stargz/resolver.go` and `resolver_test.go`. The tests do not inspect individual entries from this line range directly, but the fixture content is part of the TOC member that validates resolver behavior: footer parsing, HTTP range reads, gzip decompression, tar header validation, and successful extraction of the `stargz.index.json` body.

The file content also gives later snapshotter or TOC-parser tests realistic coverage for Debian root filesystem layouts: deep Perl directories, shared-library soname symlinks, executable files under `usr/sbin`, documentation trees, license symlinks, and package-management/keyring metadata.

## Risks And Edge Cases

Boundary handling is the main chunking risk. Lines 10124-10130 are the tail of a record whose `name` and `type` are in the previous chunk, while lines 19591-19594 begin a record whose remaining fields are in the next chunk. A merge step that treats this chunk as standalone JSON would lose or misclassify both entries.

The second risk is fixture skew. `resolver_test.go` serves `stargztoc.bin`, not this JSON text file directly. If the text fixture is edited without regenerating or verifying the compressed TOC binary, code research can describe a JSON state that is no longer the one exercised by the resolver tests.

TOC readers must preserve numeric and path semantics exactly. Offsets are byte positions into the stargz blob and must remain monotonic for regular entries in this slice. Symlinks lack file payloads and should not trigger range reads. Directory paths include trailing slashes. Modes are numeric Unix modes rather than symbolic permissions, and several entries use executable or sticky directory bits that should not be normalized away.

Digest coverage is a test signal and a data-integrity risk. Every complete regular-file entry in the range carries a `sha256:` digest. Missing, malformed, or mismatched digests would weaken verification and could hide incorrect TOC-to-blob mapping.

Large-file and deep-directory entries stress lazy snapshot behavior. The chunk includes large shared objects, Perl Unicode tables, many small metadata files, and nested paths under `perl-base`, `bash-completion`, `doc`, `gcc-6`, and `gdb`; parsers should not assume shallow paths, fixed file sizes, or a narrow set of package directories.

## Test Signals

Useful validation for this chunk starts with whole-file JSON parsing, because the assigned range is not independently valid JSON. The full fixture should parse as `version: 1` with an `entries` array, and the complete named entries in this chunk should retain the observed distribution of 784 regular files, 206 directories, and 22 symlinks.

Schema checks should assert that complete regular-file entries have `size`, `modtime`, `mode`, `offset`, `NumLink`, and `digest`; symlink entries have `linkName` and no `offset`; directory entries have no `digest` or payload offset; and path names remain unique within the full TOC. Offset-order checks should confirm regular-file offsets in this range are increasing from the first complete regular entry `usr/lib/x86_64-linux-gnu/libformw.so.5.9` through the keyring entries near the end.

Resolver-level tests should continue to verify that the mock blob range for the TOC decompresses to a tar member named `stargz.index.json`. A stronger fixture test could decompress `testdata/stargztoc.bin`, extract the TOC body, and compare it byte-for-byte or digest-for-digest with `testdata/stargz.index.json` so text and binary fixtures cannot drift silently.

Snapshotter or parser tests can use representative entries from this range to cover shared-library symlinks, executable `usr/sbin` regular files, empty/scaffold directories under `usr/local`, deep Perl module paths, documentation symlinks, common-license aliases, and Debian keyring regular files.

### subset-b-000215: lines 19595-29784

# sources/cloud-native/nydus-snapshotter/pkg/stargz/testdata/stargz.index.json lines 19595-29784

## Scope And Purpose

This chunk is a line-bounded segment of the `stargz.index.json` fixture used by `pkg/stargz`. The full file is an eStargz table-of-contents JSON document with `version: 1` and an `entries` array describing files, directories, and symlinks inside a sample Debian-like image layer. This slice is not standalone JSON: it starts in the tail of the `usr/share/keyrings/debian-archive-removed-keys.gpg` entry at its `mode`, `offset`, `NumLink`, and `digest` fields, and ends inside the `usr/share/zoneinfo/posix/Australia/` directory entry at its `type` field.

Within the selected lines, the fixture covers `usr/share` metadata-heavy paths: `libc-bin`, `lintian`, `locale`, `man`, `menu`, `misc`, PAM configuration files, `pam-configs`, Debconf and Debian Perl modules under `usr/share/perl5`, terminal tabsets, pixmaps, terminfo, and a large run of timezone data under `usr/share/zoneinfo` and `usr/share/zoneinfo/posix`. The slice contains 1,151 `name` fields, 65 directory type markers, 523 complete regular-file type markers in the line window, and 563 symlink type markers. It also includes 524 digests and 563 symlink `linkName` values.

The package does not execute this JSON directly. `resolver.go` retrieves a remote stargz blob, reads the eStargz footer, range-reads the compressed TOC tar member named `stargz.index.json`, and returns the decompressed JSON bytes. This fixture is therefore an expected TOC payload for tests and regression inspection rather than a runtime parser implementation.

## Important APIs, Types, And Data Shape

The relevant production APIs are in `pkg/stargz/resolver.go`. `Resolver.GetBlob(ref, digest, keychain)` resolves an image reference and digest to a `Blob`. `Blob.GetTocOffset()` delegates footer parsing to `estargz.OpenFooter`. `Blob.ReadToc()` range-reads the TOC area, opens it as gzip, reads the first tar member, verifies that the member name is `stargz.index.json`, and returns the uncompressed TOC content. The constants `FooterSize = 47` and `TocFileName = "stargz.index.json"` define the expected footer length and TOC tar entry name.

The JSON schema represented by this chunk is the eStargz TOC entry schema consumed by downstream stargz tooling. Entries use `name`, `type`, `modtime`, `mode`, and `NumLink` for all inode-like records. Regular files additionally carry `size`, compressed blob `offset`, and a per-file `digest` such as the first digest visible in this chunk, `sha256:ac8b1500ec8cd69c437ff1b23a2b47f60cc740573cdae02a42abe342890faa09`. Symlinks carry `linkName` and no file payload digest or offset. Directories carry no payload fields.

The important path families in this slice are:

- `usr/share/perl5/...`: Debconf frontends, elements, database drivers, templates, formatting modules, and Debian client helpers. These are mostly small regular files with offsets and digests.
- `usr/share/pam/...` and `usr/share/pam-configs/...`: PAM common config files and checksum metadata, regular files with payload locations.
- `usr/share/zoneinfo/...`: timezone database directories, regular timezone data files, compatibility symlinks, and `posix` symlink trees. This is the largest part of the chunk.
- `usr/share/menu`, `usr/share/tabset`, `usr/share/pixmaps`, `usr/share/terminfo`, and small directory placeholders such as `locale`, `man`, and `misc`.

The visible regular file offsets range from `22662459` through `23049504` in this line window. These offsets are part of the stargz random-access contract: a reader can use the TOC entry to locate the compressed blob segment for a file without unpacking the whole layer.

## Control Flow

At runtime the control flow that makes this data observable is outside the JSON file. `Resolver.resolve` converts an image reference into a registry reference, asks the transport resolver for a blob URL and `RoundTripper`, discovers blob size with a `Range: bytes=0-0` request, and builds an `io.SectionReader` backed by HTTP range requests. `Blob.GetTocOffset` reads the 47-byte footer from the end of that section reader. `Blob.ReadToc` then reads `size - tocOffset - FooterSize` bytes from the TOC area, decompresses the gzip stream with multistream disabled, opens the tar stream, requires the first tar header to be `stargz.index.json`, and copies the JSON payload into memory.

This chunk participates after that read path succeeds. A consumer of the returned TOC can scan the `entries` array, find a path such as `usr/share/zoneinfo/Africa/Cairo` or `usr/share/perl5/Debconf/ConfModule.pm`, inspect its `type`, and then either follow `linkName`, treat it as a directory, or use `offset`, `size`, and `digest` to fetch and verify a regular file payload. The fixture also exercises large-directory traversal behavior because paths appear in a sorted, tar-like order and include nested directories, compatibility aliases, and path names with underscores, hyphens, plus signs, and mixed case.

## State And Persistence Behavior

The JSON is immutable testdata checked into the repository. It represents persistent stargz metadata for a specific fixture layer, not mutable application state. The state encoded in each entry is filesystem metadata: path identity, file type, modification time, POSIX mode, link count, symlink target, payload size, payload digest, and compressed offset.

The chunk's persistence-sensitive fields are `offset` and `digest`. Offsets tie TOC metadata to byte positions in the corresponding stargz blob, so any regeneration of `stargz.index.json`, `stargztoc.bin`, or `stargzfooter.bin` must keep those artifacts mutually consistent. Digests provide content identity for regular files; changing fixture file contents, compression layout, or TOC generation can legitimately change them, but partial edits to only this JSON would create a misleading fixture.

Symlink entries are also stateful for filesystem reconstruction. Many timezone aliases point to relative targets such as `../Africa/Abidjan`, `../../Asia/Calcutta`, or canonical names such as `Japan`, `PRC`, `ROC`, and `ROK`. Preserving these exact `linkName` strings matters for compatibility with archive extraction and lazy filesystem views.

## Dependencies And Integration Points

The fixture integrates with `resolver_test.go`. The mock resolver returns range responses for a 24,613,186-byte stargz blob: one request discovers total size, one reads `stargzfooter.bin`, and one reads `stargztoc.bin`. The test verifies that footer parsing finds a TOC offset and that the TOC tar member is named `stargz.index.json`. Although the test does not parse this JSON fixture directly in the visible code, the file mirrors the decompressed TOC payload and provides a human-readable reference for the binary TOC fixture.

Production dependencies around this fixture include `github.com/containerd/stargz-snapshotter/estargz` for footer parsing, Go's `gzip` and `tar` readers for extracting the TOC member, `io.SectionReader` for random access, and the repository's registry transport resolver for HTTP range-backed reads. Downstream stargz or Nydus conversion logic can depend on this TOC shape when mapping lazy stargz metadata into filesystem metadata or another snapshot representation.

The data also depends on Debian base image conventions: `/usr/share/perl5` module layout, Debconf naming, PAM common config names, and the tzdata directory structure. These are fixture contents, but they provide broad path and metadata coverage for tools that must handle real Linux distribution layers.

## Risks And Edge Cases

The biggest fixture risk is artifact drift. `stargz.index.json`, `stargztoc.bin`, and `stargzfooter.bin` describe the same sample blob from different representations. If the JSON is edited without regenerating the binary TOC and footer, tests that only inspect tar member names may still pass while the readable fixture becomes inaccurate.

Chunk boundaries are another documentation risk. This work item begins after the `name`, `type`, `size`, and `modtime` fields for `usr/share/keyrings/debian-archive-removed-keys.gpg` and ends before the remainder of `usr/share/zoneinfo/posix/Australia/`. Any parser or analysis script for this chunk must account for partial entries at both ends instead of treating the line range as valid JSON.

Regular-file offsets and digests are brittle by design. Reordering entries, changing compression, or changing any payload can shift offsets and digests for many later files. Tests should not assert arbitrary offsets unless they intentionally lock the exact fixture blob layout.

The timezone portion has many symlink aliases and relative targets. Bugs in path normalization, symlink resolution, or extraction root handling could misinterpret targets like `../Africa/Abidjan` and `../../Atlantic/Stanley`. The `posix` subtree also uses deeper relative links than the top-level timezone aliases, which is useful coverage for relative symlink depth.

The data contains both directories with trailing slashes and non-directory paths without trailing slashes. Consumers that infer type from name suffix instead of the explicit `type` field can mishandle entries. Mode values also need to be interpreted consistently: directories commonly use `16877`, regular files use values such as `33188`, and symlinks use `41471`.

## Test Signals

Useful fixture checks should parse the full `stargz.index.json` file, not this isolated chunk, and assert that it remains valid JSON with `version: 1` and an `entries` array. Every entry should have `name`, `type`, `modtime`, `mode`, and `NumLink`; regular files should have `size`, `offset`, and `digest`; symlinks should have `linkName`; directories should not require payload fields.

Resolver tests should continue validating the binary path: mocked HTTP range size discovery, footer offset extraction, TOC byte range reads, gzip and tar decoding, and exact TOC member name `stargz.index.json`. A stronger regression test could compare the decompressed `stargztoc.bin` payload with this JSON fixture, or at least parse both and compare selected entries from this line range.

Data-focused tests for this chunk should sample each major class: a small regular file such as `usr/share/libc-bin/nsswitch.conf`, PAM files such as `usr/share/pam/common-auth`, Debconf Perl modules such as `usr/share/perl5/Debconf/ConfModule.pm`, top-level timezone files, top-level timezone symlinks, and `usr/share/zoneinfo/posix/...` symlinks. These samples should verify type-specific fields, digest syntax, offset monotonicity for regular files where applicable, and correct preservation of relative symlink targets.

Boundary tests should ensure line-range tooling records that `subset-b-000215` is a partial slice, while merge/reconciliation lanes combine it with adjacent chunks before making per-file conclusions about complete JSON structure.

### subset-b-000216: lines 29785-39848

# sources/cloud-native/nydus-snapshotter/pkg/stargz/testdata/stargz.index.json lines 29785-39848

## Scope And Purpose

This chunk is part of the `stargz.index.json` test fixture used by `pkg/stargz` resolver tests. The file is a stargz TOC JSON document with top-level `version: 1` and an `entries` array describing filesystem entries from a container layer. It is not executable code, but it is a contract fixture for code that locates, decompresses, and reads the embedded `stargz.index.json` tar member from an eStargz/stargz blob.

The requested line range begins inside the `usr/share/zoneinfo/posix/Australia/` directory entry and ends inside the `var/lib/dpkg/info/libgpg-error0:amd64.list` regular-file entry. For semantic accuracy, this research treats the complete overlapping TOC entries as the chunk. Those complete entries span entry indexes 3230 through 4347: 1,118 entries total, with 49 directories, 481 symlinks, and 588 regular files.

The content represents the middle-late portion of a Debian-like root filesystem. It covers POSIX and leap-second-aware timezone trees under `usr/share/zoneinfo`, then transitions into `/var` package-manager state such as debconf cache files, apt state directories, dpkg alternatives, dpkg package database files, and dpkg maintainer metadata under `var/lib/dpkg/info`.

## Data Model And Important Fields

Each TOC entry is a JSON object whose schema matches stargz TOC metadata expected by the resolver ecosystem. The important fields visible in this chunk are:

- `name`: archive path of the entry, using directory names with trailing `/`.
- `type`: entry kind; this chunk uses `dir`, `symlink`, and `reg`.
- `modtime`: preserved filesystem modification timestamp.
- `mode`: numeric POSIX file mode including file-type bits, for example `16877` for directories, `41471` for symlinks, `33188` for normal `0644` files, and `33261` for executable maintainer scripts.
- `linkName`: symlink target, present only on `symlink` entries.
- `size`: uncompressed file size, present on `reg` entries.
- `offset`: stargz blob data offset for regular files; in this complete overlapping chunk offsets range from `23065057` through `24139397`.
- `digest`: per-file sha256 digest for regular files, used to validate payload identity.
- `NumLink`: hard-link count metadata. It is consistently `0` in this chunk.

The regular files in this chunk total 3,218,157 bytes by TOC `size`. The largest regular-file entries are package metadata rather than application payloads, including `var/cache/debconf/templates.dat` at 725,910 bytes, `var/cache/debconf/templates.dat-old` at 708,570 bytes, `var/lib/dpkg/info/debconf.templates` at 143,753 bytes, `var/lib/dpkg/info/libapt-pkg5.0:amd64.symbols` at 143,029 bytes, `var/lib/dpkg/info/libc6:amd64.symbols` at 114,353 bytes, and `var/lib/dpkg/info/base-passwd.templates` at 108,623 bytes.

## Covered Filesystem Areas

The first major section is `usr/share/zoneinfo/posix`. In this chunk it starts with Australia aliases and continues through Brazil, Canada, Chile, `Etc`, Europe, Indian, Mexico, Pacific, SystemV, US, and many legacy top-level timezone names such as `CET`, `GMT`, `PRC`, `ROC`, `ROK`, `UTC`, and `Zulu`. These are mostly symlink entries. Their `linkName` values often point back into the canonical timezone tree, for example `../../Australia/ACT`, `../GMT`, `../../UTC`, or `../../Europe/Belgrade`.

The next large section is `usr/share/zoneinfo/right`, which contains regular timezone files and directories for leap-second-aware timezone data. This chunk includes `right/Africa`, `right/America`, `right/Antarctica`, `right/Arctic`, `right/Asia`, `right/Atlantic`, `right/Australia`, `right/Europe`, `right/Pacific`, and compatibility aliases. These entries exercise a mix of directories, symlinks, and many small regular timezone files with offsets and digests.

The chunk also includes `usr/share/zoneinfo/zone.tab`, `usr/share/zoneinfo/zone1970.tab`, `usr/share/zoneinfo/posixrules`, and the start of `/var` state. The `/var` portion includes `var/cache/debconf`, `var/cache/ldconfig`, `var/lib/apt`, `var/lib/dpkg`, `var/lib/dpkg/alternatives`, `var/lib/dpkg/available`, `var/lib/dpkg/diversions`, and `var/lib/dpkg/info`.

The final visible area, `var/lib/dpkg/info`, contains Debian package metadata and maintainer scripts for base packages including `adduser`, `apt`, `base-files`, `base-passwd`, `bash`, `bsdutils`, `coreutils`, `dash`, `debconf`, `debian-archive-keyring`, `debianutils`, `diffutils`, `dpkg`, `e2fslibs`, `e2fsprogs`, `findutils`, `gcc-6-base`, `gpgv`, `grep`, `gzip`, `hostname`, `init-system-helpers`, `libacl1`, `libapt-pkg5.0`, `libattr1`, `libaudit-common`, `libaudit1`, `libblkid1`, `libbz2-1.0`, `libc-bin`, `libc6`, `libcap-ng0`, `libcomerr2`, `libdb5.3`, `libdebconfclient0`, `libfdisk1`, `libgcc1`, `libgcrypt20`, and the first `libgpg-error0` list file.

## Resolver Integration

The direct code consumer is `sources/cloud-native/nydus-snapshotter/pkg/stargz/resolver.go`. The resolver defines `TocFileName = "stargz.index.json"` and reads stargz blobs by:

1. Resolving an image blob URL through the repository transport resolver.
2. Determining blob size with an HTTP range request.
3. Reading the fixed 47-byte stargz footer.
4. Parsing the TOC offset from the gzip footer extra field.
5. Range-reading the compressed TOC tar stream.
6. Opening the gzip stream, reading the first tar header, and requiring the tar member name to be `stargz.index.json`.
7. Returning the decompressed JSON TOC as an `io.Reader`.

This fixture supplies the JSON payload that should be produced by that read path. The neighboring binary fixtures, `stargzfooter.bin` and `stargztoc.bin`, are used by `resolver_test.go` to simulate range-based blob reads. The mock blob reports total size `24613186`; the test reads footer range `24613139-24613185` and TOC range `24442675-24613138`, then asserts that the first tar member is `stargz.index.json`.

## Control Flow Semantics

Although the chunk itself is static data, its ordering and metadata drive lazy-access behavior. A consumer parses the TOC, indexes entries by `name`, and uses `type` to decide whether a path is a directory, symlink, hardlink, or regular file. For regular files, `offset`, `size`, and `digest` provide the information needed to fetch and validate the file's payload from the stargz blob without reading the whole layer.

Directory entries establish traversal and parent-child structure. Symlink entries resolve path aliases without payload offsets. The heavy use of timezone symlinks in this chunk is useful coverage for relative link targets, parent-directory traversals in `linkName`, and compatibility names that point to canonical timezone files. The `/var/lib/dpkg/info` entries exercise regular files with colons in names, maintainer script execute bits, many small metadata files, and several large metadata files.

The chunk also demonstrates that TOC consumers must treat line boundaries as irrelevant. The requested range cuts through object boundaries, but parsers operate on the complete JSON object stream. Any research, validation, or generated fixture slicing must preserve whole JSON entries when reconstructing behavior.

## State And Persistence Behavior

This file is persisted testdata, not runtime state mutated by nydus-snapshotter. Its role is to preserve a known stargz TOC snapshot for regression tests and research. The persisted fields encode filesystem state from an image layer: path names, file types, symlink targets, file modes, modification times, uncompressed sizes, content offsets, and sha256 payload digests.

For a runtime stargz reader, the TOC is effectively the metadata database for lazy reads. If `offset`, `size`, or `digest` changes, the reader may fetch the wrong blob range, truncate or over-read payload data, or fail digest verification. If `mode`, `type`, or `linkName` changes, mounted filesystem behavior changes even when file bytes remain the same. If entry ordering or path names change, tests that compare exact TOC content or rely on deterministic metadata can fail.

The `/var/lib/dpkg` region in this chunk is particularly stateful from the image's point of view: it records installed-package manifests, checksums, maintainer scripts, shared-library metadata, symbols files, triggers, conffiles, and debconf templates. Stargz treats those as ordinary files, but they are meaningful to package-management tools inside a mounted or unpacked root filesystem.

## Dependencies And Integration Points

The fixture depends on the eStargz/stargz TOC schema used by containerd stargz tooling. The resolver code imports `github.com/containerd/stargz-snapshotter/estargz` for footer parsing and uses Go's `compress/gzip` and `archive/tar` packages to decompress and walk the TOC tar payload. It also integrates with registry/blob resolution through `github.com/containerd/nydus-snapshotter/pkg/utils/transport`, `github.com/google/go-containerregistry`, and distribution reference parsing.

The data itself reflects Debian package-management conventions, IANA timezone database layout, POSIX timezone aliases, leap-second-aware `right` timezone files, apt state files, debconf databases, and dpkg package metadata naming. These are external filesystem conventions that make the fixture valuable as a realistic rootfs sample rather than a minimal synthetic TOC.

The integration point with tests is `sources/cloud-native/nydus-snapshotter/pkg/stargz/resolver_test.go`, where mocked range requests return the binary footer and compressed TOC. This JSON fixture should stay consistent with `stargztoc.bin`; otherwise a test or external comparison that decompresses `stargztoc.bin` and compares it to `stargz.index.json` would detect drift.

## Risks And Edge Cases

The largest correctness risk is fixture drift between `stargz.index.json`, `stargztoc.bin`, and `stargzfooter.bin`. Editing the JSON alone does not update the compressed tar member or footer offsets. Any changed byte count, TOC compression, tar header, or footer offset can make resolver tests inconsistent with the source JSON.

Path handling is another risk. This chunk contains many relative symlink targets such as `../GMT`, `../../UTC`, and region-specific links, plus package metadata names containing colons, hyphens, dots, and architecture suffixes. Consumers that normalize paths too aggressively, assume no `..` in symlink targets, or treat colons specially can misrepresent the filesystem.

Mode handling must preserve file-type and executable bits. Directories, symlinks, ordinary metadata files, and executable maintainer scripts are all represented numerically. A decoder that treats `mode` as only permission bits can lose the distinction between file kinds or executable scripts such as `postinst`, `preinst`, and `postrm`.

Regular-file offsets must be interpreted as stargz blob offsets, not JSON offsets or tar-entry indexes. In this chunk, regular-file offsets are non-contiguous from the perspective of the JSON text and range from about 23.1 MB to 24.1 MB in the blob. Consumers should not infer payload ordering solely from lexical path ordering without checking TOC offset fields.

The line-range boundary is itself an edge case for chunk research: line 29785 starts inside the first directory entry and line 39848 ends before the final regular-file entry's digest. Any automated chunk processor that parses only those raw lines as standalone JSON will fail because the slice is not complete JSON.

## Test Signals

Basic validation should parse the full `stargz.index.json` as JSON, confirm `version == 1`, and confirm that `entries` remains a populated array. For this chunk's complete overlapping entries, useful invariants are 1,118 entries, with 49 `dir`, 481 `symlink`, and 588 `reg` entries, and the first and last complete entries `usr/share/zoneinfo/posix/Australia/` and `var/lib/dpkg/info/libgpg-error0:amd64.list`.

Schema checks should ensure directories lack `offset`, `size`, `digest`, and `linkName`; symlinks include `linkName` and lack regular-file payload fields; and regular files include `size`, `offset`, and `digest`. All entries in this chunk should retain `NumLink: 0`.

Fixture consistency checks should decompress `testdata/stargztoc.bin`, extract the `stargz.index.json` tar member, and compare it byte-for-byte with `testdata/stargz.index.json`. Resolver tests should continue to assert the footer size, parsed TOC offset, range requests, gzip/tar readability, and tar member name.

Path-focused tests should include relative timezone symlink targets, `right` timezone regular files, executable dpkg maintainer scripts, filenames with architecture suffixes such as `:amd64`, and large metadata files such as debconf templates and libc symbols. These cases exercise the filesystem metadata diversity that this chunk contributes to the whole fixture.

### subset-b-000217: lines 39849-41900

# sources/cloud-native/nydus-snapshotter/pkg/stargz/testdata/stargz.index.json lines 39849-41900

## Scope And Purpose

This chunk is the terminal slice of the eStargz TOC fixture used by `pkg/stargz`. The requested range starts on the final digest field of the preceding `var/lib/dpkg/info/libgpg-error0:amd64.list` entry, then covers complete TOC entries from `var/lib/dpkg/info/libgpg-error0:amd64.md5sums` through `var/tmp/`, followed by the closing `entries` array and root JSON object. The source file has 41899 lines, so the requested end line 41900 resolves to end-of-file.

The file is not executable code. It is persisted test data representing a `stargz.index.json` tar member inside an eStargz layer. `resolver.go` expects a blob footer to identify the TOC offset, reads the compressed tar member named `stargz.index.json`, and returns this JSON payload to callers. This chunk therefore acts as fixture coverage for the tail of a valid TOC: late-layer offsets, package-manager metadata, empty files, directories, symlinks, ownership-sensitive log files, and well-formed JSON closure.

The visible entries are a Debian/Ubuntu root filesystem tail. Most entries are under `var/lib/dpkg/info/` and describe package metadata files for libraries and base packages such as `libgpg-error0`, `liblz4-1`, `liblzma5`, `libmount1`, `libncursesw5`, PAM packages, `libpcre3`, SELinux libraries, `libstdc++6`, `libsystemd0`, `libudev1`, `login`, `mount`, `passwd`, `perl-base`, `sed`, `tar`, `tzdata`, `util-linux`, and `zlib1g`. The remainder covers dpkg database files, trigger locks, PAM state, systemd helper state, `/var` directories, `/var/lock` and `/var/run` symlinks, and log files.

## Important Data Model

The effective API surface is the eStargz TOC entry schema consumed by `github.com/containerd/stargz-snapshotter/estargz` and by this package's resolver tests. The root object has `version: 1` and an `entries` array. Every visible item uses the `name`, `type`, `modtime`, `mode`, and `NumLink` fields. Regular files can include `size`, `offset`, and `digest`. Symlinks include `linkName`. Directories omit file content fields. Several zero-length regular files omit `size` and `offset` but keep the SHA-256 digest of empty content.

The chunk contains 193 visible regular-file entries, 15 directories, and 3 symlinks. Regular files include content-bearing records with offsets from `24139809` through `24442396`, plus empty files such as `var/lib/dpkg/lock`, `var/lib/dpkg/statoverride`, dpkg trigger locks, timer marker files, `var/log/btmp`, and `var/log/wtmp` whose digest is the standard SHA-256 of empty content. This distinction is important for readers that must not assume every `reg` entry has an offset.

File modes cover several Unix metadata cases. Most package metadata files use `33188` (`0100644`). Maintainer scripts such as `postinst`, `postrm`, `preinst`, `prerm`, and `tzdata.config` use `33261` (`0100755`). Lock files include stricter modes such as `33184` (`0100640`) and `33152` (`0100600`). Log files `var/log/btmp`, `var/log/lastlog`, and `var/log/wtmp` carry group `43` with modes `33200` or `33204`. `var/local/` and `var/mail/` use group-specific directory modes and gids, while `var/tmp/` uses the sticky world-writable directory mode `17407`.

The three symlinks are `var/lock -> /run/lock`, `var/run -> /run`, and `var/spool/mail -> ../mail`. They use `type: "symlink"`, `linkName`, symlink mode `41471`, and no digest or offset. These entries validate that TOC consumers preserve absolute and relative symlink targets rather than treating all non-directory paths as regular file content.

## Chunk Contents

The first full section is package metadata under `var/lib/dpkg/info/`. It includes package file lists, md5sum manifests, shared-library dependency metadata (`.shlibs`), symbol files (`.symbols`), conffile declarations, maintainer scripts, debconf templates, and trigger files. Package groups in the chunk include `libgpg-error0`, `liblz4-1`, `liblzma5`, `libmount1`, `libncursesw5`, `libpam-modules-bin`, `libpam-modules`, `libpam-runtime`, `libpam0g`, `libpcre3`, `libselinux1`, `libsemanage-common`, `libsemanage1`, `libsepol1`, `libsmartcols1`, `libss2`, `libstdc++6`, `libsystemd0`, `libtinfo5`, `libudev1`, `libustr-1.0-1`, `libuuid1`, `login`, `lsb-base`, `mawk`, `mount`, `multiarch-support`, `ncurses-base`, `ncurses-bin`, `passwd`, `perl-base`, `sed`, `sensible-utils`, `sysvinit-utils`, `tar`, `tzdata`, `util-linux`, and `zlib1g`.

Large content records exercise high-size TOC metadata near the end of the layer. Notable examples are `libstdc++6:amd64.symbols` at `369490` bytes, `tzdata.templates` at `267379` bytes, `tzdata.list` at `73851` bytes, `tzdata.md5sums` at `55759` bytes, `perl-base.md5sums` at `47930` bytes, `perl-base.list` at `35267` bytes, `libpam0g:amd64.templates` at `35685` bytes, and `libpam-runtime.templates` at `34973` bytes. These are useful signals for validating offset arithmetic and read sizes in a TOC whose content is not uniformly small.

The dpkg database section includes `var/lib/dpkg/lock`, `parts/`, `statoverride`, `status`, `status-old`, `triggers/`, trigger files `Lock`, `Unincorp`, and `ldconfig`, plus `updates/`. `status` and `status-old` are substantial regular files with distinct offsets and digests, while the lock and trigger files show empty-file representation. This section models a package database snapshot rather than installed binaries.

The PAM and systemd-helper sections include `var/lib/pam/` state files (`account`, `auth`, `password`, `seen`, `session`, `session-noninteractive`) and `var/lib/systemd/deb-systemd-helper-enabled/` timer markers. The `session` and `session-noninteractive` entries intentionally share the same digest and size, providing a duplicate-content case with separate path names and offsets.

The final `/var` tree entries cover `var/local/`, `var/log/`, `var/log/apt/`, `btmp`, `faillog`, `lastlog`, `wtmp`, `var/mail/`, `var/opt/`, `var/spool/`, `var/spool/mail`, and `var/tmp/`. These entries preserve directory permissions, group ids, log-file modes, empty log-file digests, and terminal JSON structure.

## Control Flow

There is no local control flow in this JSON file. The relevant runtime flow is in `pkg/stargz/resolver.go`. `Resolver.GetBlob` resolves an image reference and layer digest through a transport resolver, wraps the remote blob as an `io.SectionReader`, and returns a `Blob`. `Blob.GetTocOffset` calls `estargz.OpenFooter` over that section reader to find the TOC offset. `Blob.ReadToc` reads from the TOC offset to `blob size - FooterSize`, decompresses the gzip stream with multistream disabled, opens the tar stream, requires the first tar header name to equal `stargz.index.json`, and returns the tar member body as a reader.

This fixture chunk is part of the body returned after that flow succeeds. The resolver test uses mock byte ranges for the blob size, footer, and TOC tar stream, then verifies that the extracted tar header is named `stargz.index.json`. Because this chunk closes the root JSON object, it is also part of the structural signal that the TOC body is complete and parseable after extraction.

TOC consumers process entries by walking the `entries` array in order. For regular files with offsets, a lazy snapshotter can use `offset`, `size`, and `digest` to locate and validate file content without eagerly unpacking the whole layer. For directories, the consumer materializes metadata and hierarchy. For symlinks, the consumer materializes the link target from `linkName`. For zero-length regular files without an offset, the consumer must materialize an empty file from metadata and digest rather than attempting a ranged read.

## State And Persistence Behavior

The JSON file persists filesystem metadata for an image layer, not live process state. Its entries are effectively a static index from path names to file type, content address, layer offset, permissions, ownership where present, and timestamps. The persisted state represented by this chunk is package-manager and base-system state under `/var`, including dpkg package records, dpkg status databases, PAM update state, systemd timer enablement markers, and log-file placeholders.

Regular-file `digest` fields represent content identity and validation state. Repeated digests are meaningful: trigger files with identical contents share the same digest, empty files all use the empty SHA-256 digest, and `var/lib/pam/session` and `var/lib/pam/session-noninteractive` share a digest while remaining separate paths. Snapshotter logic should preserve the path-level metadata even when content digests collide.

Offsets are persistent references into the compressed stargz blob's content layout. The entries in this chunk live near the end of the layer, immediately before the TOC data range used by the test fixture. Any regeneration of the layer, tar ordering, gzip layout, or chunking would change many offsets and digests. This makes the file a brittle but valuable golden fixture for resolver behavior against a specific blob layout.

Directory and symlink entries persist metadata without content digests. The final directories and symlinks are important because container root filesystems depend on `/var/run`, `/var/lock`, `/var/spool/mail`, group-owned mail/log directories, and sticky `/var/tmp` semantics. A TOC reader that drops these fields would reconstruct a filesystem that is structurally valid JSON but semantically wrong.

## Dependencies And Integration Points

The direct integration point is `pkg/stargz/resolver.go`, especially constants `FooterSize` and `TocFileName`, `Blob.GetTocOffset`, `Blob.ReadToc`, `Resolver.GetBlob`, `Resolver.resolve`, and the range-backed `readerAtFunc`. `resolver_test.go` integrates the fixture with `testdata/stargzfooter.bin` and `testdata/stargztoc.bin`; the latter contains a tar/gzip member whose payload corresponds to this JSON fixture.

External dependencies include `github.com/containerd/stargz-snapshotter/estargz` for footer parsing, Go `gzip` and `tar` readers for TOC extraction, container registry resolution through `github.com/google/go-containerregistry` and distribution reference parsing, and Nydus transport resolution. The JSON schema itself follows the eStargz TOC conventions used by lazy image snapshotters.

The fixture also integrates with Linux filesystem semantics. The `mode`, `gid`, `linkName`, and empty-file representations are not optional decoration for a snapshotter: they drive reconstructed ownership, permissions, symlink targets, executable maintainer scripts, lock-file accessibility, log-file permissions, and sticky directory behavior.

## Risks And Edge Cases

The first line of the requested range is not a complete entry; it is the digest field closing the prior `libgpg-error0:amd64.list` object. Chunk-level research and future merge tooling must preserve that boundary and avoid treating line 39849 as the start of an independent JSON object.

The file ends in this chunk. Any edit that removes the final `]` or `}` would break the entire fixture even if every visible entry remains valid. The range also demonstrates that the source file has 41899 lines, so tools that assume the requested line 41900 exists should handle EOF gracefully.

Regular-file entries are not uniform. Some have `size`, `offset`, and `digest`; some empty regular files omit `size` and `offset`; executable maintainer scripts use different modes; some log files carry `gid`; and duplicate digests appear across different paths. Code that assumes every regular entry has an offset, that digest uniqueness implies path uniqueness, or that missing size means malformed data would mishandle this chunk.

Symlink handling is a specific risk. `var/lock` and `var/run` point to absolute `/run` targets, while `var/spool/mail` points to a relative target. A consumer that normalizes, strips, or resolves symlink targets during TOC parsing could alter image semantics or introduce path traversal/security issues when materializing the filesystem.

The dpkg and PAM sections include many package-management scripts and database files. Although this fixture is test data, downstream systems that display or process TOCs should treat path names and metadata as untrusted image content. Maintainer script executable bits, large template files, and package database content should not be executed or parsed with elevated trust merely because they appear in a valid TOC.

Offsets near the tail of the layer make this chunk sensitive to off-by-one errors in range reads. The resolver reads `size - tocOffset - FooterSize` bytes for the TOC gzip stream and relies on `ReadAt` against remote HTTP ranges. Incorrect blob size, footer size, offset parsing, or HTTP range boundaries could truncate exactly this tail section, causing JSON parse failures or missing final `/var` entries.

## Test Signals

Fixture-integrity tests should parse the full `stargz.index.json` as JSON, confirm `version == 1`, and ensure the `entries` array remains closed and complete. A focused check for this chunk should assert that entries from `var/lib/dpkg/info/libgpg-error0:amd64.md5sums` through `var/tmp/` are present and that the source ends at the root JSON close.

Schema tests should cover the visible field combinations: regular files with offset/size/digest, zero-length regular files with empty digest and no offset, directories with no digest, symlinks with `linkName`, entries carrying `gid`, executable file modes, sticky directories, and duplicate digests across distinct paths. These cases are all present in this chunk.

Resolver tests should continue verifying that the mocked blob range for `testdata/stargztoc.bin` decompresses to a tar member named `stargz.index.json`. Additional regression coverage could call `Blob.ReadToc`, parse the returned JSON, and assert tail entries such as `var/run`, `var/spool/mail`, `var/tmp/`, `var/log/lastlog`, `var/lib/dpkg/status`, and `var/lib/dpkg/info/tzdata.templates`.

Range-read tests should exercise the exact footer/TOC boundary used in `resolver_test.go`: mocked content length `24613186`, footer range `24613139-24613185`, and TOC range `24442675-24613138`. A truncated TOC should fail before consumers silently accept a partial JSON object missing this terminal chunk.

Materialization tests for a stargz reader should verify that `/var/lock` and `/var/run` remain symlinks to `/run/lock` and `/run`, `/var/spool/mail` remains a relative symlink to `../mail`, `/var/tmp/` has sticky directory semantics, empty files are created without attempting invalid reads, and log files preserve group/mode metadata where represented.
