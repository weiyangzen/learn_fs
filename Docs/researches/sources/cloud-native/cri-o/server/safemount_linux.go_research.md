# sources/cloud-native/cri-o/server/safemount_linux.go

Purpose: securely bind-mounts a subpath inside a volume while preventing path traversal or symlink escape.

Important APIs and functions: `safeMountInfo.Close` unmounts and closes the held file; `safeMountSubPath(mountPoint, subpath, runDir)` opens the subpath inside the mount root via `pathrs.OpenInRoot`, binds `/proc/self/fd/<fd>` to a temporary directory or file, and returns cleanup state.

Control flow: after secure open, the function stats the fd path, rejects symlinks, creates a temp mount target matching directory/file type, then performs `MS_BIND|MS_REC`.

State and persistence: opens a file descriptor that pins the resolved path, creates a temp file/directory under `runDir`, creates a bind mount, and cleans both mount and fd on `Close`.

Dependencies and integration: uses pathrs secure join/open primitives and Linux mount syscalls. Intended for Kubernetes subPath-style volume mount handling.

Risks: if bind mount succeeds but later caller forgets `Close`, temp mounts and fds can leak. If temp file creation succeeds and mount fails, the temp path is not removed here. Symlink rejection is explicit for the final target, complementing root-constrained open.

Test signals: no direct tests in this subset.
