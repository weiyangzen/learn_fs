# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_otp.cc

## Purpose
Implements the metadata handler for RGW user one-time-password/MFA device metadata. It adapts cls MFA storage to the generic metadata manager interface so OTP devices can be fetched, set, removed, listed, formatted, and completed in the metadata log.

## Important APIs, Types, And Functions
`MetadataObject` derives from `RGWMetadataObject` and stores a list of `rados::cls::otp::otp_info_t` devices, dumping them as JSON. `MetadataHandler` derives from `RGWMetadataHandler` and reports type `"otp"`. It implements JSON decoding, `get()` through `mfa.list_mfa()`, `put()` through `mfa.set_mfa()`, `remove()` through `rgw_delete_system_obj()`, `mutate()` by running a callback then completing mdlog, and listing with `RGWMetadataLister`.

The namespace exports `rgwrados::otp::get_meta_key()` and `create_metadata_handler()`.

## Control Flow
Metadata JSON input must contain a decodable `"devices"` list or `get_meta_obj()` returns null. `put()` stores the device list with version tracking and the metadata object mtime, then calls `mdlog.complete_entry("otp", entry, &objv)`. `remove()` deletes the system object from the OTP pool and also completes mdlog. `mutate()` assumes the provided callback performed the actual mutation and only completes mdlog on success.

## State And Persistence
OTP device lists are persisted in the zone OTP pool via cls MFA/system object APIs. Object version and mtime are carried through `RGWMetadataObject`. The metadata key format is `otp:user:<user_string>`.

## Dependencies And Integration Points
Depends on `RGWSI_SysObj`, `RGWSI_Cls::MFA`, `RGWSI_MDLog`, zone params, `RGWMetadataLister`, cls OTP types, and metadata manager interfaces. It integrates with metadata sync/admin paths through the handler factory and with mdlog completion for replication.

## Risks And Test Signals
`put()` always passes `true` to `set_mfa()`, so overwrite/version semantics must match cls MFA expectations. `mutate()` does not use `mtime` or `op_type` directly, relying on the callback and mdlog completion. Listing uses no prefix, so the OTP pool should contain only OTP entries or callers must tolerate every oid as a key. Tests should cover JSON decode failure, get/put/remove mdlog completion, version conflict behavior, list marker handling, and key formatting for tenants/users.
