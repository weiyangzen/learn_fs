# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MockContainerMD.hh

Purpose: Test subclass of `QuarkContainerMD` that records lock registration/unregistration order for locking tests.
Important APIs/types/functions: `MockContainerMD` inherits `QuarkContainerMD` and `enable_shared_from_this`; static vectors track write/read lock and unlock sequences; overrides `getIdentifier`, `registerLock`/`unregisterLock` for `MDWriteLock` and `MDReadLock`; accessor and `clearVectors` helpers expose/reset traces.
Control flow: construction sets a fixed `ContainerIdentifier`; when EOS lock wrappers register/unregister, overrides call base behavior then append `shared_from_this()` to the appropriate trace vector.
State/persistence: process-global static vectors only; no backend persistence.
Dependencies/integration: used by `OtherTests.cc` with `BulkNsObjectLocker` and `NSObjectLocker`; depends on `ContainerMD.hh` and lock types.
Risks: static vectors are defined in a header, which can violate ODR if included in multiple translation units; shared_from_this requires instances be managed by `shared_ptr`.
Test signals: active tests validate lock/unlock counts and ordering through this mock.
