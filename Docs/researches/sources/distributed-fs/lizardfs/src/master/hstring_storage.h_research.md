# sources/distributed-fs/lizardfs/src/master/hstring_storage.h

Purpose: defines the abstract storage interface for filesystem name strings and the RAII `Handle` wrapper used in directory entries and trash/reserved path containers.

Important APIs/types/functions: `Storage::instance()`, `reset()`, and virtual `compare()`, `get()`, `copy()`, `bind()`, `unbind()`, `name()` define backend operations. `Handle` stores a 64-bit backend-defined value, copies by deep storage copy, moves by stealing data, binds from `HString`/`std::string`, unbinds in destructor, converts to string/HString, exposes `hash()`, and supports comparison operators with `HString`.

Control flow: a backend must be installed before any non-empty `Handle` construction/destruction. Copy assignment unbinds current data then copies; `set()` replaces current binding. Equality uses backend hash/full comparison, while ordering converts to `std::string`.

State and persistence behavior: global storage backend is a static unique pointer hidden behind `Storage::static_wrapper<0>`. Handles themselves are persisted only indirectly by serializing string values from storage, not by saving raw handle data.

Dependencies/integration: used by filesystem directory maps, metadata store edge serialization, hstorage init, and tests.

Risks and test signals: `Storage::instance()` dereferences without null checks; initialization and teardown ordering are critical. Move assignment does not unbind an already-bound destination before overwriting `data_`, creating a potential leak. `unlink()` intentionally drops ownership without unbinding and must be used carefully. Tests should cover lifecycle order, copy/move assignment over bound handles, comparison semantics, and reset behavior after handles are destroyed.
