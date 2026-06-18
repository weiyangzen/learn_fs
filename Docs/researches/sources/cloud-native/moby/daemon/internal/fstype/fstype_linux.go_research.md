## sources/cloud-native/moby/daemon/internal/fstype/fstype_linux.go

Purpose: Linux implementation of filesystem type detection.

Important API: `getFSMagic(rootpath string) (FsMagic, error)` calls `unix.Statfs` and returns `FsMagic(buf.Type)`.

Control flow and state: One syscall-backed function. It returns `0` plus the syscall error on failure.

Dependencies and integration: Depends on `golang.org/x/sys/unix` and is reached through `GetFSMagic` in `fstype.go`.

Risks: Requires the path to exist and be statfs-readable. Callers must decide how to handle unknown magic values not present in `FsNames`.

Persistence: Reads filesystem metadata only. No tests in this subset.
