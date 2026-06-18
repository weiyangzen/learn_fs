<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resforce.cc -->
# sources/distributed-fs/coda/coda-src/resolution/resforce.cc

Purpose: repairs runt directory replicas by extracting directory-create/link operations from a non-runt replica and forcing them onto runt replicas.

Important APIs/control flow: `UpdateRunts` identifies runt VVs with `RuntExists`, fetches a serialized op list and ACL/status via `Res_GetForceDirOps`, temporarily removes non-runt hosts from the group, multicasts `DoForceDirOps` to runt sites, updates successful VV slots, and restores non-runt members. `RS_GetForceDirOps` enumerates a directory into `diroplink` records, serializes them in network order, returns status and ACL, and ships the op file. `RS_DoForceDirOps` validates coordinator lock and runt status, receives/parses the op file, checks semantics/disk usage, installs ACL/status, calls `ForceDir`, sets the top-level VV, and spools a null resolve record. `ForceDir` allocates vnodes and performs mkdir/create/link/symlink operations.

State/persistence: mutates runt directory replicas, ACLs, vnode metadata, directory entries, disk usage, and resolution logs. `diroplink` op files are temporary transfer artifacts.

Dependencies/integration: uses `rescomm`, `resutil`, `ops`, `operations`, `inodeops`, ACL conversion, volume locks, and SMARTFTP.

Risks/test signals: `CreateL` semantics checks currently reject an existing object even though links need an earlier `CreateF` in the same force list; ordering assumptions are important. Temporary removal of non-runt members affects group state. Test directories with files, symlinks, subdirs, hard links, insufficient space, non-runt absence, and lock-owner mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resforce.cc -->
