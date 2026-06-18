<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tarheader/tarheader.go -->
# sources/cloud-native/containerd/pkg/archive/tarheader/tarheader.go

Purpose: create tar headers from `os.FileInfo` without OS user/group lookups, making header generation safe in chrooted or restricted contexts.

Important APIs and types: `nosysFileInfo`, package variable `sysStat`, and exported `FileInfoHeaderNoLookups(fi, link)`.

Control flow and state: `nosysFileInfo.Sys` hides native `Sys` data unless it is already a `*tar.Header`. `FileInfoHeaderNoLookups` calls `tar.FileInfoHeader` with the wrapper, then optionally invokes `sysStat` to populate safe system-dependent fields.

Dependencies and integration: used by `ChangeWriter.HandleChange` in `archive/tar.go` to avoid propagating host user/group names into layer tars.

Risks and test signals: Uname/Gname are intentionally absent; callers needing atime/ctime must handle them explicitly. Unix population is installed by `tarheader_unix.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tarheader/tarheader.go -->
