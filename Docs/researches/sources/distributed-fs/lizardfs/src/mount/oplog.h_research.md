## sources/distributed-fs/lizardfs/src/mount/oplog.h

Purpose: declares the operation-log formatting and handle API used by special inode files and mount operation tracing.

Important APIs: `oplog_printf` overloads carry GCC printf-format attributes when available; `oplog_newhandle`, `oplog_releasehandle`, `oplog_getdata`, and `oplog_releasedata` implement streaming reads.

Integration and state: header exposes unsigned long file handles that map to internal `fhentry` records. Consumers must respect the get/release pairing and buffer lifetime.

Risks and tests: the API does not express that `oplog_getdata` holds a mutex until release, so misuse can deadlock or expose stale ring memory. Compile-time format checking is a positive test signal for log calls.
