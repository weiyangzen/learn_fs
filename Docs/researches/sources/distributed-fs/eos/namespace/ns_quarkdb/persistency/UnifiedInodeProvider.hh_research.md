# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/UnifiedInodeProvider.hh

Purpose: Declares the combined inode provider interface for file and container metadata services.
Important APIs/types/functions: public methods reserve, blacklist, and peek first-free IDs for file and container namespaces; private fields track shared-inode mode, metadata hash, and per-kind `NextInodeProvider` instances.
Control flow: services use one facade regardless of whether deployment metadata says file/container IDs are shared or separate.
State/persistence: state is minimal in-memory routing plus provider objects; durable state is delegated to QDB hash fields.
Dependencies/integration: includes `NextInodeProvider.hh` and qclient `QHash`; constants are used in the implementation.
Risks: the header exposes no explicit initialized check, so dereferencing null providers is possible if used before `configure()`; behavior after reconfigure is not documented.
Test signals: covered through service creation and custom-ID integration tests rather than direct unit tests.
