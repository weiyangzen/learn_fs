<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/system/System.cpp -->
## sources/distributed-fs/beegfs/common/source/common/system/System.cpp

Purpose: Implements Linux/system utility functions used across BeeGFS common code.

Important APIs/functions: Provides errno string formatting, hostname, CPU/NUMA discovery and binding, thread ID, FD limit raising, memory info, mountpoint device lookup, user/group name-ID mapping, user/group enumeration, and filesystem UID/GID changes.

Control flow/state/persistence: Most functions query `/proc`, `/sys`, libc, or kernel syscalls. Static `strerrorMutex` serializes `strerror`. Static saved effective UID/GID are captured at process startup for later FS-ID elevation. NUMA error logging suppresses repeated warnings.

Dependencies/integration: Uses `StorageTk`, `StringTk`, `LogContext`, POSIX APIs, `/proc/self/mountinfo`, `/proc/meminfo`, passwd/group databases, and Linux `setfsuid`/`setfsgid`.

Risks/test signals: Several passwd/group functions are explicitly non-reentrant. `getDevicePathFromMountpoint` depends on mountinfo parsing. Tests should cover NUMA absence, mountpoint lookup failures, FD limits, memory parsing, privilege drop/elevation, and concurrent error-string use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/system/System.cpp -->
