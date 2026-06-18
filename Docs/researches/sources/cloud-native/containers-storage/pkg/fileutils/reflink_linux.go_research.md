## sources/cloud-native/containers-storage/pkg/fileutils/reflink_linux.go

Purpose: Linux helper to clone file contents with CoW reflink when possible, falling back to byte copy.

Important APIs/types/functions: `ReflinkOrCopy`.

Control flow: calls `unix.IoctlFileClone(dst, src)`; on success returns nil, otherwise runs `io.Copy(dst, src)` and returns copy error.

State and persistence: mutates destination file contents/extent references.

Dependencies and integration points: used where fast copy or CoW clone is beneficial. Depends on Linux clone ioctl support and current file offsets.

Risks: fallback starts copying from the current source offset and destination offset; callers must position files correctly. It ignores the reflink error cause by design.

Test signals: no direct selected tests.
