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
