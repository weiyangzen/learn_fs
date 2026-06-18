<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resforce.h -->
# sources/distributed-fs/coda/coda-src/resolution/resforce.h

Purpose: public declarations for runt-directory forcing.

Important APIs/types: `dirop_t` enumerates serialized directory operations: create directory, file, symlink, or hard link. `diroplink` carries operation type, vnode/unique, and fixed-size name buffer with host/network byte-order conversion and `write`. `getdiropParm` packages a volume and operation list for directory enumeration. Exports `UpdateRunts` and `RuntExists`.

State/persistence: header declares transient operation records; persistence happens in `resforce.cc` via vnode allocation, directory operations, and log spooling.

Dependencies/integration: includes Coda `olist`; uses `DIROPNAMESIZE` from resolution utilities in practice and Coda volume/vnode types through including files.

Risks/test signals: fixed `name[DIROPNAMESIZE]` requires enforced length checks during enumeration. Serialized struct layout is compiler/ABI-dependent despite byte-order conversion. Test cross-platform compatibility if heterogeneous servers are supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resforce.h -->
