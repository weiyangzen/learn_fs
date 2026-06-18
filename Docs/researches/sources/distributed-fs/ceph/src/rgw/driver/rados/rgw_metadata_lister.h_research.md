# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_metadata_lister.h

## Purpose
Provides a small reusable lister wrapper for metadata stored as system objects in an `RGWSI_SysObj::Pool`. It converts object listing results into metadata keys and gives handlers a common implementation for list operations.

## Important APIs And Types
`RGWMetadataLister` owns a `RGWSI_SysObj::Pool` and a `Pool::Op` listing operation. `init()` starts listing from a marker and prefix. `get_next()` fetches up to `max` object ids, handles missing pools/objects as an empty result, calls virtual `filter_transform()` to turn oids into keys, and returns truncation status. `get_marker()` is available in RADOS builds and delegates to the underlying listing operation.

## Control Flow And State
By default `filter_transform()` moves every oid into the output key list unchanged. Derived listers can override it to strip prefixes, filter internal objects, or transform object ids into metadata entry names. The only persistent state is the backing system object namespace; the lister itself keeps iteration state in `listing`.

## Dependencies And Integration Points
The class depends on `services/svc_sys_obj.h` and is used by metadata handlers such as the OTP handler to implement `list_keys_init/next/complete`. It abstracts enough of the pool listing API for metadata manager consumers to use opaque handles.

## Risks And Test Signals
Because `get_next()` clears `keys` before each listing call, callers must accumulate across calls if needed. Treating `-ENOENT` as success with `truncated=false` is useful for absent pools but can hide misconfiguration. Tests should verify marker progression, prefix filtering in subclasses, empty pool handling, and build behavior when `WITH_RADOSGW_RADOS` gates marker access.
