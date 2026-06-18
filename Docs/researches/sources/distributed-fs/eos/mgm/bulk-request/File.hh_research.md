## sources/distributed-fs/eos/mgm/bulk-request/File.hh

Purpose: declares the per-file domain value stored inside bulk requests. A `File` carries a path and optional error text.

Important APIs: default/path constructors, `setPath()`, `setError(string)`, `setError(optional<string>)`, `setErrorIfNotAlreadySet()`, `getPath()`, `getError()`, equality by path, and strict ordering by path. Empty string errors are ignored by the string overload.

State/integration: used by `FileCollection`, prepare validation, DAO serialization, query response error accumulation, and proc reconstruction. Risks include path-only identity meaning duplicate failed/success records for the same path compare equal in sets, errors not affecting ordering/equality, and getters returning copies. Tests should cover empty-error handling, first-error preservation, path ordering, and behavior when collected into `std::set<File>`.
