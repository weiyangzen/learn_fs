# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar.go

Purpose: writes OCI layer tar streams from filesystem change events, ported from containerd with Nydus-specific error context.

Important APIs and flow: `ChangeWriter` wraps `tar.Writer`, source root, inode hardlink tracking, parent-directory tracking, and timestamp options. `NewChangeWriter` initializes it. `HandleChange` converts delete events to OCI whiteout files, skips sockets, handles symlinks, creates PAX headers, normalizes paths to slash form, sets special device headers via Unix helper, tracks hardlinks, skips unmodified entries, records `security.capability` xattrs, includes parent directories, writes file headers and regular file contents, and emits additional hardlink entries. `Close` closes the tar writer. `includeParents` recursively ensures parent directory entries exist. `copyBuffered` copies with pooled buffers and context cancellation checks.

State and persistence: streams tar output only; reads source filesystem metadata, file contents, symlinks, and xattrs.

Dependencies and integration: consumed by overlay diff `writeUpperdir` to produce the tar stream that snapshotter-converter packs into a Nydus blob. Relies on containerd continuity change kinds and Unix-specific helpers.

Risks and test signals: correctness is security-sensitive because ownership, devices, hardlinks, xattrs, and whiteouts define image layer behavior. Parent inclusion uses `os.Stat`, so missing parents fail the diff. Context in file copy uses `context.TODO` from `HandleChange`, so caller cancellation only reaches the outer writer path, not copy internals.
