<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/system/System.h -->
## sources/distributed-fs/beegfs/common/source/common/system/System.h

Purpose: Declares the common system utility interface.

Important APIs/types: `System` exposes static helpers for errors, host/system topology, memory, device/machine UUIDs, user/group lookup, process/thread IDs, FD limits, and filesystem identity changes. Private static state stores a mutex for error formatting and saved effective IDs.

Control flow/state/persistence: This is a stateless static utility facade except for saved process credentials and the errno mutex.

Dependencies/integration: Includes common type aliases, invalid-config exceptions, CPU sets, pthread, and time/syscall headers. `UUID.h` provides definitions for UUID-specific methods.

Risks/test signals: The header exposes broad platform-specific behavior, so portability is Linux-bound. Tests should mock or isolate `/proc`, `/sys`, passwd/group DB, and privilege-sensitive helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/system/System.h -->
