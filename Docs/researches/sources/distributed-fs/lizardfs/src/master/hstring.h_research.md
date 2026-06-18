# sources/distributed-fs/lizardfs/src/master/hstring.h

Purpose: defines `HString`, a `std::string` subclass with a cached 32-bit hash used to speed dominant name comparisons in filesystem lookup paths.

Important APIs/types/functions: constructors from C string, `std::string`, iterators, copy, and move all call `computeHash()`; assignment operators recompute hash; `hash()` exposes the cached value; equality/inequality operators compare hashes first and only compare full strings on hash match.

Control flow: instances behave like strings but keep hash synchronized after construction/assignment through the provided API.

State and persistence behavior: stores only in-memory string content and cached hash. Directory-entry persistence stores names through `hstorage::Handle`, not `HString` itself.

Dependencies/integration: used by filesystem node names, quota path output, snapshot names, and `hstorage` backends. It uses `std::hash<std::string>`.

Risks and test signals: inheriting from `std::string` means base mutating methods can be called without recomputing `hash_`, producing stale hashes. Move constructor recomputes after move rather than preserving source hash, which is safe. Tests should avoid or explicitly cover mutation through base APIs and verify hash-first comparison still handles collisions through full compare.
