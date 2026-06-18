# sources/distributed-fs/lizardfs/src/master/hstorage_init.h

Purpose: declares `hstorage_init()`, the startup hook for global name storage.

Important APIs/types/functions: `hstorage_init()` returns an integer status for the master run table.

Control flow: called early from `RunTab` before metadata structures that create `hstorage::Handle` values.

State and persistence behavior: no direct state in the header; implementation installs the storage backend.

Dependencies/integration: included by `init.h` and linked with the name storage implementations.

Risks and test signals: no term/reload declarations are exposed, so lifecycle is event-loop registered internally. Tests should verify the run table calls this before filesystem initialization.
