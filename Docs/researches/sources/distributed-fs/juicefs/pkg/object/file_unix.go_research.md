# sources/distributed-fs/juicefs/pkg/object/file_unix.go


Purpose: supplies Unix-only owner/group extraction and mtime changes for `filestore`.

Important APIs and flow: `getOwnerGroup` inspects `info.Sys()` as either `*syscall.Stat_t` or `*sftp.FileStat`, converting UID/GID to names through `utils.UserName` and `utils.GroupName`. `(*filestore).Chtimes` maps an object key to a path and calls platform-specific `lchtimes` to change mtime without following symlinks.

State and persistence: no standalone persistent state, but `Chtimes` changes local filesystem metadata.

Dependencies and integration: compiled for `!windows`; bridges local filesystem and SFTP stat representations to the common `File` metadata interface. Requires `file_linux.go` or `file_darwin.go` to provide `lchtimes` and `getAtime` on supported Unix targets.

Risks: owner/group lookup depends on host user/group databases and may return empty names. SFTP metadata support depends on the remote server and SFTP library stat values. The actual atime behavior is delegated to OS-specific files.

Test signals: `file_unix_test.go` tests the timestamp path. Broader owner/group behavior is indirectly covered in filesystem contract tests where metadata is compared after chmod/chown on capable backends.
