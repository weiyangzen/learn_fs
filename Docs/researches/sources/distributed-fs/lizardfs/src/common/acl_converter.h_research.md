<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_converter.h -->
# sources/distributed-fs/lizardfs/src/common/acl_converter.h

## Purpose

The header declares ACL conversion APIs between raw xattr bytes and `AccessControlList`.

## Important APIs, Types, and Functions

Namespace `aclConverter` defines exceptions `AclConversionException` and `PosixExtractionException`, plus `extractAclObject(const uint8_t*, uint32_t)` and `aclObjectToXattr(const AccessControlList&)`.

## Control Flow

The header is declarative. Callers pass raw xattr storage into extraction or an ACL object into serialization and handle conversion exceptions on malformed data.

## State and Persistence Behavior

No state is declared. The returned vector from `aclObjectToXattr()` is intended for persistent xattr storage.

## Dependencies and Integration Points

It depends on `AccessControlList` and common exception macros. Metadata/xattr handlers use this layer to cross the POSIX ACL boundary.

## Risks and Edge Cases

Callers must distinguish ACL conversion errors from missing xattrs or unsupported ACL types outside this API. `PosixExtractionException` is declared but not used by the implementation in this subset.

## Test Signals

Expected signals are binary xattr round trips, malformed version/tag/id/mask rejection, and compatibility with Linux POSIX ACL xattr ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_converter.h -->
