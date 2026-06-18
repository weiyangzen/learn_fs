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
