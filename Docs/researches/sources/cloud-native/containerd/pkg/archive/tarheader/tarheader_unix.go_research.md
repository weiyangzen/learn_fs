<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tarheader/tarheader_unix.go -->
# sources/cloud-native/containerd/pkg/archive/tarheader/tarheader_unix.go

Purpose: Unix system metadata population for lookup-free tar headers.

Important APIs and functions: `init` assigns `sysStat = statUnix`; `statUnix` copies UID/GID and special-device major/minor numbers from `syscall.Stat_t`.

Control flow and state: on Unix, every `FileInfoHeaderNoLookups` call can receive UID/GID and device metadata. FreeBSD regular-file `Rdev == -1` is intentionally ignored unless the header is block/char.

Dependencies and integration: depends on `syscall.Stat_t` and `x/sys/unix`. Used by archive diff tar generation for ownership and device entries.

Risks and test signals: incorrect major/minor extraction breaks special device layer entries. FreeBSD behavior prevents unencodable large device numbers in regular file headers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tarheader/tarheader_unix.go -->
