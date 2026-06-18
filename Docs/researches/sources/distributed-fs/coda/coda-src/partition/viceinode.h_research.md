# sources/distributed-fs/coda/coda-src/partition/viceinode.h

Purpose: defines inode metadata records shared by partition backends, inode scans, and volume/salvage code.

Important types: `i_header` is the backend resource-header format with link count, volume, vnode, unique, data version, and magic. `ViceInodeInfo` is the scan output record with inode number, byte count, link count, volume/vnode/unique/version, and magic. `INODESPECIAL` reserves an impossible vnode number.

State/integration: persisted by simple sidecar files and ftree `FTREEDB`; emitted by list operations. Risks include native struct layout/endian assumptions in persisted headers and scan files. Tests are backend create/header/list paths.
