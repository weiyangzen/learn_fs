# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MockFileMDSvc.hh

Purpose: Disabled GMock file metadata service stub intended for metadata object unit tests.
Important APIs/types/functions: inside `#if 0`, `MockFileMDSvc` derives from `IFileMDSvc` and mocks lifecycle/configuration, future and synchronous lookup, existence checks, create/update/remove, counts, listener notification, quota/container service wiring, visitor traversal, first-free ID, and cache statistics.
Control flow: none active because the mock class is compiled out.
State/persistence: none active; if enabled, behavior would be controlled by GMock expectations.
Dependencies/integration: includes GMock, test namespace macros, and file service interface; referenced by disabled serialization tests.
Risks: likely stale relative to current `IFileMDSvc`; inactive code provides no compile-time signal for interface changes.
Test signals: no active test coverage uses this file.
