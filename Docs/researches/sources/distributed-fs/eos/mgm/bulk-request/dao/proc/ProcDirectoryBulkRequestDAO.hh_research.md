## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestDAO.hh

Purpose: declares the proc-directory DAO implementation and documents its storage model: one directory per bulk request under type-specific proc paths, with request/file data stored as directory xattrs.

Important APIs: implements all `IBulkRequestDAO` methods. Private helpers cover cancellation, directory creation/deletion/existence, path generation, save cleanup, xattr generation/persistence/fetching, stage initialization from xattrs, reconstruction of file lists from xattrs, metadata future initiation, and last-access updates.

State/integration: members include non-owning `XrdMgmOfs*`, proc locations reference, root virtual identity, xattr names (`last_accessed_time`, `issuer_uid`, `creation_time`, `fid.` prefix). Integration is deep with MGM namespace and proc command APIs. Risks include broad private surface, raw pointer lifetime, root identity for all proc operations, and storage schema compatibility. Tests should use fake `XrdMgmOfs`/namespace services or integration fixtures to validate xattr-level persistence and retrieval.
