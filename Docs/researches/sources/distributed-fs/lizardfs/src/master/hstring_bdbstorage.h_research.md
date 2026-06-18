# sources/distributed-fs/lizardfs/src/master/hstring_bdbstorage.h

Purpose: declares the Berkeley DB implementation of the name-string storage interface.

Important APIs/types/functions: `BDBStorage` overrides `compare()`, `get()`, `copy()`, `bind()`, `unbind()`, and `name()`; static `hash()` extracts the top 16 bits from a handle; private `encode()`, `decode()`, and overload `bind()` handle DB record IDs and cached hashes.

Control flow: callers interact through the `Storage` base; implementation manages a `DB *` and heap record ids.

State and persistence behavior: owns a DB handle and path string. The encoded handle stores DB heap record coordinates plus hash.

Dependencies/integration: depends on `<db.h>`, `hstring_storage.h`, and compile-time checks for expected DB record-id field sizes.

Risks and test signals: compile-time static assertions constrain supported libdb ABI. Tests should validate behavior only when `LIZARDFS_HAVE_DB` is enabled and should ensure handle salt prevents a valid record with hash zero from looking empty.
