<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/types/types.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/types/types.go

Purpose: defines the daemon's abstraction boundary over local/remote containerd implementations.

Important APIs and types: `EventType` constants, `EventInfo`, `Backend`, `Process`, `Client`, `Container`, `Task`, and `StdioCallback`.

Control flow: no executable control flow beyond interface contracts. Implementations report lifecycle events to `Backend.ProcessEvent`, expose container/task/process lifecycle methods, attach stdio through `StdioCallback`, and return platform-specific `Stats`, `Summary`, and `Resources` types from companion files.

State and persistence: none in this file; it specifies how implementations expose state.

Dependencies and integration: imported by local/remote libcontainerd clients, plugin executor, and daemon code that should not depend directly on containerd implementation details.

Risks: interface changes have wide blast radius across Linux, Windows, plugin executor, and tests. Event names are string contracts consumed by daemon event handling.

Test signals: covered indirectly by compile-time implementation satisfaction and integration paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/types/types.go -->
