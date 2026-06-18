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
