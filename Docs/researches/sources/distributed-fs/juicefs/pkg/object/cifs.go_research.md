# sources/distributed-fs/juicefs/pkg/object/cifs.go


Purpose: implements SMB/CIFS storage behind `!nocifs`, registering both `cifs` and `smb`.

Important APIs and flow: `cifsStore` stores SMB connection parameters and a channel-backed connection pool. `getConnection` reuses live connections until an idle timeout, creates new `smb2` sessions and mounts shares, and honors context cancellation while waiting. `withConn` scopes operations. `Head`, `Get`, `Put`, `Delete`, `List`, `Copy`, `Chtimes`, and `Chmod` map object operations to SMB file operations; `Get` returns a `cifsReadCloser` that releases the connection only after close. `parseEndpoint` accepts `cifs://` or `smb://host[:port]/share`.

State and persistence: persistent state is the remote SMB share. Local state is the connection pool and idle timestamps. Writes use temp paths through `TmpFilePath` unless global `PutInplace` is enabled.

Dependencies and integration: uses `github.com/cloudsoda/go-smb2`, shared `mEntry`, `SectionReaderCloser`, `bufPool`, and `FileSystem`. It reports placeholder owner/group values and marks symlinks where SMB exposes them.

Risks: `Chmod`, `Chown`, and POSIX mode semantics are limited by SMB. Some methods use `context.Background()` for filesystem metadata operations. The pool can create bursts of connections under load, noted by a FIXME. Symlink handling is best-effort. Directory delete trims trailing `/`.

Test signals: covered by environment-gated `TestCifs` and `TestCifs2`, both delegating to broad object and filesystem contract tests.
