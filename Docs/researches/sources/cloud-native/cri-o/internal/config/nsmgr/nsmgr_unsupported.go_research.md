# sources/cloud-native/cri-o/internal/config/nsmgr/nsmgr_unsupported.go

Purpose: provides namespace manager stubs for platforms other than Linux and FreeBSD.

Important APIs/types/functions: empty `NamespaceManager`; `New`, `Initialize`, `GetNamespace`, `NamespacePathFromProc`, and `NamespaceFromProcEntry`.

Control flow: construction succeeds, initialization returns nil, but namespace retrieval and proc-entry pinning return unsupported errors or empty paths.

State and persistence behavior: no state, directories, or mounts are created.

Dependencies/integration points: compile-time compatibility shim for shared CRI-O namespace management call sites.

Risks: callers must handle unsupported errors where namespace lifecycle management is required.

Test signals: no tests.
