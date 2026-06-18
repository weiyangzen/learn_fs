<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/archive.go

Purpose: public chroot-aware archiver facade that routes tar/untar/copy/apply operations through safer platform-specific implementations.

Important APIs/types/functions: `NewArchiver`, `NewArchiverWithChown`, `Untar`, `UntarWithRoot`, `UntarUncompressed`, `untarHandler`, `Tar`, `CopyFileWithTarAndChown`, `CopyWithTarAndChown`, and `UntarPathAndChown`.

Control flow: `untarHandler` validates non-nil archive, defaults options and rootless `InUserNS`, ensures destination exists with mapped root ownership, creates an `unpackDestination`, optionally decompresses, and invokes platform-specific unpack. `Tar` delegates to platform-specific pack. Copy/chown helpers create archive archivers with untar mappings and optional chown overrides; when a hasher is supplied, they wrap `Untar` with `io.TeeReader` or a pipe to hash either whole archives or file payload.

State/persistence: creates destination directories, extracts archives, writes copied files, and may hash streamed content. No independent persistent metadata is stored.

Dependencies/integration: wraps `pkg/archive` archiver APIs, `idtools`, `unshare`, and platform-specific `newUnpackDestination`, `invokeUnpack`, and `invokePack`.

Risks: security depends on correct `root` selection; `UntarWithRoot` is intended for attacker-controlled destination paths. Hasher goroutine/pipe handling must not deadlock if untar fails. Chown/ID map interactions affect file ownership.

Test signals: `archive_test.go` covers chroot tar/untar, huge exclude lists, nil archive errors, copy/chown helpers, empty slow readers, and dot-dot-like safe names. `archive_unix_test.go` covers CVE-2018-15664 symlink attack scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive.go -->
