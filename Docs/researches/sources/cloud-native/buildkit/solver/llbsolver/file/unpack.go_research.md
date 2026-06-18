<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/unpack.go -->
## sources/cloud-native/buildkit/solver/llbsolver/file/unpack.go

Purpose: implements docker-compatible archive detection and unpacking for file copy actions that request archive extraction.

Important APIs and types: `unpack` and `isArchivePath`.

Control flow: `unpack` resolves source/destination safely under their roots, returns false for non-archive sources, creates destination directory with requested ownership/timestamp, opens the source, builds tar options with best-effort xattrs, optional idmap and chown, then calls `chrootarchive.Untar`. `isArchivePath` rejects non-regular files, opens the source, creates a decompression stream, and checks whether a tar reader can read the first entry.

State and persistence: mutates destination filesystem by creating directories and extracting archive contents. Dependencies include Go tar, BuildKit archive/chrootarchive/compression packages, continuity fs, user idmap, and fsutil copy chowner.

Integration points: called from `docopy` before normal copy when `AttemptUnpackDockerCompatibility` is set.

Risks and test signals: archive sniffing opens/decompresses the source and treats any readable first tar entry as archive. Extraction correctness and security rely on chrootarchive and root path resolution. No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/unpack.go -->
