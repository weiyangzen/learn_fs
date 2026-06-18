# sources/distributed-fs/coda/coda-src/al/pdbdb.c

Purpose: Low-level persistence layer for PDB profiles over an `rwcdb` database at `vice_config_path("db/prot_users.cdb")`.

Important APIs/functions: `PDB_db_open`, `PDB_db_reopen`, `PDB_db_nextkey`, `PDB_db_close`, `PDB_db_release`, `PDB_db_maxids`, `PDB_db_update_maxids`, `PDB_db_write`, `PDB_db_read`, `PDB_db_delete`, `PDB_db_delete_xfer`, `PDB_db_exists`, `PDB_db_compact`, and `PDB_setupdb`.

Control flow: A single static `pdb_handle` is lazily initialized. Read-only opens sync existing state; write opens upgrade the handle when needed and periodically sync every 128 mutations. Records are keyed by network-order numeric ID. Name lookup uses a secondary key composed of `"NAME"` plus the name, whose value is the numeric key. Key iteration filters to four-byte numeric keys.

State and persistence: Persists max UID/GID under a zero-length key and profile blobs under ID keys. Writes insert both ID and name index records, update max IDs, and free the packed blob passed by the caller. `PDB_db_close` is intentionally a no-op; `PDB_db_release` frees the process-global handle.

Dependencies and integration: Depends on `rwcdb`, `vice_file`, byte-order APIs, and `pdb.h`. Higher layers use this as the durable backing store for AL/PDB/auth identity data.

Risks and test signals: The global handle is not thread-safe and `PDB_db_nextkey` uses static iteration state. `PDB_db_close` doing nothing can surprise callers expecting close/flush isolation. `PDB_db_compact` is stubbed. Many error paths exit or assert. Name-key length omits an explicit NUL in the database key length, matching internal convention but needing consistency.
