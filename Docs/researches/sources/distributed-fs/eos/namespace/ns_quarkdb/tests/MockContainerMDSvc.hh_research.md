# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MockContainerMDSvc.hh

Purpose: Disabled GMock service stub for container metadata tests.
Important APIs/types/functions: inside `#if 0`, `MockContainerMDSvc` derives from `QuarkContainerMDSvc` and declares mocks for lifecycle, configuration, CRUD, listener notification, lost+found, parent creation, service wiring, accounting wiring, and first-free ID lookup.
Control flow: no active control flow because the class is compiled out.
State/persistence: none active; if enabled, it would mock service interactions in memory.
Dependencies/integration: includes GMock, test namespace macros, and `ContainerMDSvc.hh`; referenced by disabled `MetadataTests.cc`.
Risks: inactive mock may drift from the real service interface; header filename comment says `.cc`; enabling it may require updating method signatures to current interfaces.
Test signals: no active tests depend on it today.
