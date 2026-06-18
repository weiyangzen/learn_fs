# sources/distributed-fs/juicefs/pkg/object/sftp.go

Purpose: implements an SFTP-backed object store, mapping object keys to remote files/directories under a configured root.

Important APIs and types: `conn` wraps SSH/SFTP clients with close detection. `sftpStore` owns host, port, root, SSH config, and a connection pool. It implements file metadata, range reads, atomic-ish writes, chmod/chown/chtimes, symlink/readlink, delete, delimiter-only list, and authentication setup in `newSftp`.

Control flow and state: operations borrow a pooled connection and return or close it depending on error health. `Put` creates parent directories, writes either in place or to a temp path followed by rename, and treats directory keys as `MkdirAll`. `Head` follows symlinks for metadata but records symlink status. `List` only supports `/` delimiter, lists one remote directory, sorts entries, optionally follows symlinks, filters non-regular files, and emits `file` objects with owner/group/mode.

Persistence and integration: persistence is the remote filesystem. Authentication supports password, private key path, local SSH keys, SSH agent, keyboard interactive, known hosts via `SSH_KNOWN_HOSTS`, or insecure host-key ignore. It implements filesystem and symlink optional interfaces used by prefix wrappers and VFS tooling.

Risks and test signals: context parameters do not cancel SFTP calls. Default host-key behavior is insecure unless configured. Connection pool is unbounded. Path/root parsing depends on the last colon and can be tricky for unusual endpoints. No SFTP-specific tests are included.
