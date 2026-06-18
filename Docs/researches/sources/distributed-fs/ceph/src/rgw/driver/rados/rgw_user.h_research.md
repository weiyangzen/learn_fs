# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_user.h

## Purpose
Declares RGW user administration types and RADOS/SAL-facing helper APIs. The header defines request-state carriers, user/key/subuser/cap pools, admin operation wrappers, and user-control service wrappers used by `rgw_user.cc` and the broader RGW admin and metadata stack.

## Important APIs, types, and functions
- Constants define key lengths, default anonymous id, random subuser length, and S3 XML namespace.
- Free functions declare secret/access key generation, stats sync, anonymous user setup, permission conversion, and tenant validation.
- `RGWUID` is an encodable UID wrapper with formatter and test instances.
- `bucket_meta_entry` models bucket usage summaries.
- Enums `ObjectKeyType`, `RGWKeyPoolOp`, and `RGWUserId` identify key/admin operation modes.
- `RGWUserAdminOpState` is the central mutable request object. It stores requested user fields, key/subuser/cap operations, quotas, rate limits, temp URL keys, MFA ids, placement, flags indicating which fields were explicitly specified, lookup result flags, and methods that set and query that state.
- `RGWAccessKeyPool`, `RGWSubUserPool`, and `RGWUserCapPool` expose public `add()`, `remove()`, and `modify()` contracts while hiding validation and persistence sequencing.
- `RGWUser` declares lifecycle and admin operations plus helper-pool members.
- `RGWUserAdminOp_User`, `_Subuser`, `_Key`, and `_Caps` declare static admin entry points that write formatter output.
- `RGWUserCtl` provides typed `GetParams`, `PutParams`, and `RemoveParams` option builders around `RGWSI_User`.

## Control flow
Callers build `RGWUserAdminOpState`, set requested fields using setters that also mark specification flags, initialize `RGWUser` with a SAL driver, then call an operation. Helper pools are initialized from the `RGWUserAdminOpState` after user lookup or user-info construction, so their maps point directly into `RGWUserInfo` owned by the state. Admin wrappers hide this setup for common REST operations.

## State and persistence behavior
The header itself does not persist, but it defines the state that drives persistence: object version trackers, old/new user ids, user attrs, quotas, rate limits, key maps, subusers, flags for generated credentials, purge behavior, and secondary lookup result flags. `RGWUserCtl` method signatures expose how user info and attrs are read, stored, and removed through `RGWSI_User`, optionally with version and mtime parameters.

## Dependencies and integration points
Includes Ceph encoding/types, RGW common/tool/string/format SAL forward declarations, formatter support, quotas/rate limits via included RGW common types, and metadata handler factory declarations. It is consumed by admin REST code, RADOS SAL services, metadata sync, and bucket/user stats helpers.

## Risks and edge cases
The state object contains many boolean flags that must stay consistent with values; callers can set conflicting combinations such as explicit key type plus subuser context. Getters expose mutable `RGWUserInfo` maps, making helper pools sensitive to initialization order. Several setters silently ignore empty input, which can make explicit clearing require separate `*_specified` flags. `get_attrs()` returns by value, while `set_attrs()` copies into the SAL user attrs.

## Test signals
Compile and unit coverage should verify flag-setting semantics, generated-key/subuser defaults, helper-pool initialization failures for anonymous/uninitialized users, `RGWUserCtl` parameter builders, and ABI/encoding compatibility for `RGWUID`.
