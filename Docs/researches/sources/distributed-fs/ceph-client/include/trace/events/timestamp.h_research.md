# sources/distributed-fs/ceph-client/include/trace/events/timestamp.h

Purpose: Defines timestamp tracepoints for ctime/mtime change tracking and multigrain timestamp fill/exchange behavior.

Important APIs/types/functions: Provides `ctime`, `ctime_ns_xchg`, and `fill_mg_cmtime` event definitions/classes that capture inode pointers, device/inode identifiers, current and updated timestamp seconds/nanoseconds, and exchange results.

Control flow: VFS timestamp update paths emit events when inode change times are set, exchanged, or filled with multigrain cmtime data. Assignment copies inode and time fields into the raw event entry.

State/persistence: No inode state is changed by this header; trace buffers persist timestamp observations.

Dependencies/integration: Integrates with VFS inode timestamp code, tracepoint infrastructure, and user-space trace consumers debugging ctime granularity.

Risks: Timestamp semantics are subtle across filesystems. Incorrect field naming or seconds/nanoseconds pairing can mislead filesystem ordering and cache-coherency investigations.

Test signals: Run timestamp/VFS tests with tracing enabled; validate ctime and multigrain events during file update, stat, and concurrent timestamp exchange workloads.
