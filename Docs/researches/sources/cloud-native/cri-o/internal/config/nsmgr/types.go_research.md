# sources/cloud-native/cri-o/internal/config/nsmgr/types.go

Purpose: defines the platform-independent namespace type names and public namespace interface.

Important APIs/types/functions: `NSType` string alias; constants `NETNS`, `IPCNS`, `UTSNS`, `USERNS`, `PIDNS`, and `ManagedNamespacesNum`; interface `Namespace` with `Path`, `Type`, and `Remove`.

Control flow: no executable logic; this is the shared contract consumed by platform-specific namespace managers and container factory code.

State and persistence behavior: none.

Dependencies/integration points: imported by `nsmgr` platform files and by container factory code that tracks PID namespaces.

Risks: `ManagedNamespacesNum` must remain synchronized with the namespace constants supported by platform implementations.

Test signals: no direct tests; implementations and consumers exercise the interface.
