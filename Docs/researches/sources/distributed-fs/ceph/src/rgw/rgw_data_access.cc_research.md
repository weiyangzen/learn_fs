# sources/distributed-fs/ceph/src/rgw/rgw_data_access.cc

## Purpose
Implements a small SAL-backed data access helper for loading buckets and writing complete objects with ACL, compression, etag, and atomic-writer handling.

## Important APIs, types, and functions
`RGWEtag` computes hex etags, with MD5 marked non-FIPS cryptographic use. `RGWDataAccess::Bucket::init()` loads bucket info and attrs through SAL or accepts preloaded metadata. `finish_init()` decodes bucket ACL attrs. `Bucket::get_object()` creates an object wrapper. `Object::put()` creates an atomic writer, optionally wraps compression, streams data in `rgw_max_chunk_size` pieces, computes/sets etag and ACL attrs, then completes the write.

## Control flow
A caller obtains a bucket, gets an object wrapper, configures metadata setters, and calls `put()`. The write path prepares the atomic writer, pushes data through optional compression and writer filters, flushes with an empty buffer, fills missing etag/ACL attrs, and calls `complete()` with object size, mtime, attrs, delete-at, user data, no checksum, and log-op flag.

## State and persistence
Persistent effects are object data, object attrs including etag/ACL, version instance generation, bucket index/log updates through SAL writer completion, and optional compression-transformed storage.

## Dependencies and integration points
Depends on SAL driver/bucket/object/writer, RGW ACL, compression plugins, AIO throttle config, checksum API, request context, and Ceph `bufferlist`.

## Risks and test signals
Risks include modifying caller data/attrs, compression plugin load failures, etag differences when caller supplies etag, versioned instance generation, ACL defaults, and completion failure after data streaming. Tests should cover preloaded buckets, ACL decode errors, compressed/uncompressed writes, supplied etag, default ACL, versioning, delete-at/user-data fields, and writer prepare/process/complete failures.
