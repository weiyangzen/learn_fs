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
