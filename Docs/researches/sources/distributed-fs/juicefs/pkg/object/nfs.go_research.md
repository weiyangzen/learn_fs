# sources/distributed-fs/juicefs/pkg/object/nfs.go


Purpose: implements NFSv3-backed object storage behind `!nonfs`, registering `nfs`.

Important APIs and flow: `nfsStore` wraps a mounted `nfs.Target`, user identity, root, and default file/directory modes. `Head` follows symlinks by reading the link target and recursively heading it, marking the result symlink. `Get`, `Put`, `Delete`, `List`, `Chtimes`, `Chmod`, `Chown`, `Symlink`, and `Readlink` map object operations to NFS calls. `mkdirAll` recursively creates directories. `List` uses `ReadDirPlus`, symlink following rules, sorting, and delimiter-only listing.

State and persistence: persistent data is in the mounted NFS export. Writes use temp object names unless `PutInplace`, then rename. Owner/group and mode changes call NFS setattr.

Dependencies and integration: uses `github.com/vmware/go-nfs-client/nfs`, RPC auth from current UID/GID, shared `FileSystem`, `SupportSymlink`, `mEntry`-like behavior, and `utils` user/group lookups.

Risks: `ListAll` is explicitly unsupported, so generic list-all must use delimiter traversal. Context arguments are mostly not used by NFS calls. Symlink resolution uses path joins and may behave differently from POSIX for edge cases. `newNFSStore` requires `host:path` format and sets large read-dir counts. Empty root delete is a no-op.

Test signals: `TestNFS` and `TestNFS2` are environment-gated and run shared object/filesystem contracts.
