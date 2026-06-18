<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/example_changes.go -->
# sources/cloud-native/containers-storage/pkg/archive/example_changes.go

Purpose: ignored build-tag example command that creates an archive stream from differences between an old and new directory.

Important APIs/types/functions: flags `-D`, `-newdir`, `-olddir`; `main`; helper `prepareUntarSourceDirectory`.

Control flow: `main` parses flags, enables debug logging, creates default temp old/new dirs when paths are absent, populates the new dir with files and optional hardlinks, calls `archive.ChangesDirs`, exports changes with `archive.ExportChanges`, copies the archive to stdout, and reports byte count on stderr.

State/persistence: temporary directories are created and removed when defaults are used. Output is a tar stream on stdout.

Dependencies/integration: demonstrates the public archive diff/export API and logrus debugging. It has `//go:build ignore`, so it is not part of normal builds.

Risks/test signal: it references older `ChangesDirs`/`ExportChanges` call shapes that may drift from current signatures; as an ignored sample, it can silently rot unless manually built. No direct tests target it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/example_changes.go -->
