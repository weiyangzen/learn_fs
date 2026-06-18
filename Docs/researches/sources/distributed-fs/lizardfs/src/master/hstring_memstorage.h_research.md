# sources/distributed-fs/lizardfs/src/master/hstring_memstorage.h

Purpose: declares the in-memory implementation of `hstorage::Storage`.

Important APIs/types/functions: `MemStorage` overrides storage operations; static `hash()` extracts cached hash from a handle; static `c_str()` decodes const and mutable pointers; private `encode()` packs pointer and hash; debug builds keep a static set of unobfuscated pointers.

Control flow: used through `Storage::instance()` and installed by `hstorage_init()` or tests.

State and persistence behavior: stores per-handle heap allocations only; no disk persistence.

Dependencies/integration: depends on `hstring_storage.h` and `<set>` for debug tracking.

Risks and test signals: `static_assert(sizeof(void *) <= 8)` is necessary but not sufficient for every 64-bit address layout. Tests should run under sanitizers/Valgrind with pointer obfuscation enabled when possible.
