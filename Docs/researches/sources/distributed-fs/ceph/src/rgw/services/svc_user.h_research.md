<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_user.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_user.h

Purpose: Declares the abstract RGW user metadata service interface.

Important APIs, types, and functions: Static helpers map between `rgw_user` and metadata keys. Pure virtual operations cover buckets object location, metadata listing, user info read/store/remove, lookup by email/Swift/access key, and raw email index reads.

Control flow: Higher-level RGW user/account code uses this interface independent of storage backend. Concrete implementations must maintain UID records and secondary indexes consistently.

State and persistence: The base class has no persistent state. Implementations persist user info and indexes.

Dependencies and integration points: Depends on RGW service base, SAL forward declarations, `RGWMetadataLister`, `RGWUserInfo`, `RGWUID`, `RGWObjVersionTracker`, cache info, attrs, and optional yields.

Risks and test signals: Since store/remove are multi-index operations, implementations must define ordering and failure behavior. Backend tests should verify all lookup paths after create/update/remove and metadata lister filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_user.h -->
