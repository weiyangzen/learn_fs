# sources/distributed-fs/ceph/src/rgw/rgw_data_access.h

## Purpose
Declares `RGWDataAccess`, a compact abstraction for bucket lookup and object PUT operations using RGW SAL.

## Important APIs, types, and functions
`RGWDataAccess` stores a `rgw::sal::Driver*`. `Bucket` stores bucket info, tenant/name/id, mtime, attrs, and ACL policy, and exposes `get_object()`. `Object` stores bucket reference, object key, mtime, etag, OLH epoch, delete-at, user data, and optional ACL buffer. It exposes `put()` plus setters for metadata and policy. Two `get_bucket()` overloads support loading by names or using existing bucket info/attrs.

## Control flow
Callers construct `RGWDataAccess`, acquire a `BucketRef`, create an `ObjectRef`, set optional metadata, and write object data. Bucket initialization decodes ACL before object writes need an owner.

## State and persistence
The header describes in-memory handles that lead to persistent writes in the implementation. Shared pointers keep bucket state alive for objects.

## Dependencies and integration points
Depends on RGW common types, SAL forward declarations, ACL policy, Ceph times, `bufferlist`, and optional yield.

## Risks and test signals
The interface relies on a non-owning driver pointer and private constructors. Tests should check lifetime assumptions, bucket ACL availability, object metadata setter propagation, and both bucket initialization paths.
