<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/net/unix/DomainSocketWatcher.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/net/unix/DomainSocketWatcher.c

## Purpose
`DomainSocketWatcher.c` implements a small JNI-managed poll set for watching Unix-domain sockets for readability or hangup.

## Important APIs, Types, and Functions
It defines `struct fd_set_data` with allocated size, used size, and a flexible `pollfd` array. JNI exports are `anchorNative()`, `FdSet.alloc0()`, `FdSet.add()`, `FdSet.remove()`, `FdSet.getAndClearReadableFds()`, `FdSet.close()`, and `doPoll0()`.

## Control Flow
`anchorNative()` caches the Java `FdSet.data` long field. `alloc0()` allocates a minimum two-fd poll set. `add()` grows the native allocation by doubling when needed and appends a `POLLIN | POLLHUP` entry. `remove()` swaps the last entry into the removed slot. `doPoll0()` calls `poll()` and treats `EINTR` as no descriptors ready. `getAndClearReadableFds()` counts entries with `POLLIN` or `POLLHUP`, creates a Java int array, fills it, and clears returned `revents`.

## State and Persistence
The native `fd_set_data` allocation is owned by the Java `FdSet.data` field until `close()`. No process-global fd state is stored besides the cached field ID.

## Dependencies and Integration Points
It depends on `poll(2)`, JNI, and Hadoop exception helpers. Java `DomainSocketWatcher` uses it to multiplex many local sockets.

## Risks and Edge Cases
`add()` sets `nd->alloc_size = nd->alloc_size * 2` after `realloc`, using the copied old value but relying on it remaining valid. The code does not guard against adding duplicate fds. Thread safety must be provided by the Java watcher because the native set has no locking.

## Test Signals
Tests should add/remove fds, grow beyond the initial capacity, detect readable and hung-up sockets, handle EINTR, reject removing absent fds, and verify `close()` nulls native state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/net/unix/DomainSocketWatcher.c -->
