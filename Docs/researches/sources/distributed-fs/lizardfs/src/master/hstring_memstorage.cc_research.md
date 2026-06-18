# sources/distributed-fs/lizardfs/src/master/hstring_memstorage.cc

Purpose: implements in-memory `hstorage::Storage` using heap-allocated C strings encoded directly into `Handle` values with cached hashes.

Important APIs/types/functions: `compare()` uses the encoded 16-bit hash before comparing against decoded C string; `get()` returns the decoded string; `copy()` duplicates another handle's C string; `bind()` allocates and copies a null-terminated string; `encode()` packs pointer and hash; `unbind()` frees the pointer; `name()` returns `MemStorage`.

Control flow: binding allocates one C string per handle and stores pointer bits plus hash in the handle. Copy creates a deep duplicate; move is handled by `Handle`. Unbind frees the decoded pointer.

State and persistence behavior: all state is volatile heap memory. Debug builds track raw pointers in `debug_ptr_` for validation/Valgrind friendliness.

Dependencies/integration: depends on `hstring_memstorage.h`, allocation functions, and the `Storage` interface. It is the default name backend.

Risks and test signals: pointer obfuscation assumes user-space pointers fit in the low bits after reserving 16 hash bits, which is documented as 48-bit virtual address behavior. `Handle` move assignment overwrites without unbinding existing data in the destination, so callers must avoid assigning over a bound handle by move or tests should catch leaks. Tests should cover copy/deep-copy, empty strings, hash extraction, debug pointer tracking, and pointer-width assumptions.
