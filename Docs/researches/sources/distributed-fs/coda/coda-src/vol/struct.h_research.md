# sources/distributed-fs/coda/coda-src/vol/struct.h

Purpose: provides small structure-layout helper macros.

Important APIs: `fldsiz(type, member)` returns the size of a field, and `strbase(type, p, member)` computes the containing structure pointer from a member pointer using `coda_offsetof`.

Control flow/state: no runtime state; these macros are used while traversing embedded link nodes, especially recoverable list links inside `VnodeDiskObject` and hash/list links inside VRDB entries.

Dependencies/integration: depends on `coda_offsetof.h`. Integration is broad because Coda uses intrusive list structures. Risks include incorrect member pointer type or object lifetime causing invalid containing-object recovery. Test signals are compile-time use in `recovb`, `dumpcamstorage`, and `vrdb`, plus sanitizer-style checks when traversing lists.
