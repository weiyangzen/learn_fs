# sources/distributed-fs/lizardfs/src/master/hstring_bdbstorage.cc

Purpose: implements Berkeley DB-backed storage for `hstorage::Handle` string names.

Important APIs/types/functions: constructor creates a DB handle, sets optional page size and cache size, and opens a truncating heap database; destructor closes DB with `DB_NOSYNC`; `compare()` checks encoded hash before retrieving; `get()` decodes record id and reads the string; `copy()` rebinds a copy; `bind()` appends a null-terminated string to DB and encodes record id plus hash; `unbind()` deletes the DB record; `encode()` and `decode()` pack/unpack `DB_HEAP_RID` and hash into a 64-bit handle.

Control flow: handle creation inserts a string into DB and stores a compact encoded reference. Comparisons avoid DB reads unless the 16-bit hash matches. Destruction deletes the corresponding heap record.

State and persistence behavior: stores transient name strings in a Berkeley DB heap file opened with `DB_CREATE | DB_TRUNCATE`; it is storage-backed but recreated on master start, not a durable metadata authority. Handle values encode a salted page number and index plus hash.

Dependencies/integration: depends on libdb C API and the `hstorage::Storage` virtual interface. Selected by `hstorage_init()` when compiled with DB support.

Risks and test signals: DB is truncated on open, so all existing handles must be loaded after initialization. `get()` returns `data.data` as a C string from DB memory, which relies on libdb allocation semantics and null termination from `bind()`. Hash is only 16 bits, so collisions must fall back to full retrieval. Tests should cover open failures, cache/page parameters, copy/delete lifecycle, hash collision behavior, and cleanup of temp DB files.
