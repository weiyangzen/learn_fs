<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_converter.cc -->
# sources/distributed-fs/lizardfs/src/common/acl_converter.cc

## Purpose

This file converts between Linux POSIX ACL xattr binary format and LizardFS `AccessControlList`.

## Important APIs, Types, and Functions

Public functions are `aclConverter::extractAclObject()` and `aclObjectToXattr()`. Internal helpers/constants define POSIX ACL tags, permission bits, version `0x0002`, `convertTag()`, `extractEntry()`, and `storeEntry()`.

## Control Flow

Extraction checks the xattr version, scans 8-byte entries, converts little-endian tags/perms/ids, validates permission masks and undefined ids for owner/group/mask/other, rejects invalid/repeated required tags, and requires minimal user/group/other entries. Serialization writes the version, owner user, named users, owner group, named groups, optional mask, and other entry.

## State and Persistence Behavior

No global state is used. The output vector is the persistent xattr payload that can be stored by filesystem metadata layers.

## Dependencies and Integration Points

It depends on `AccessControlList`, endian helpers, and ACL converter exceptions. It is the bridge between internal ACL state and external POSIX xattr representation.

## Risks and Edge Cases

The code uses unaligned casts to `uint16_t*`/`uint32_t*`, which can be risky on strict-alignment architectures. It does not explicitly require the total buffer size after the version to be a multiple of 8; a trailing partial entry becomes invalid through `extractEntry()`. Only repeated minimal tags are rejected; named entry duplicates are normalized by `AccessControlList::setEntry()` before duplicate checking for named tags.

## Test Signals

The unit-test file contains xattr fixtures but the active tests are commented out, so this converter currently lacks active direct coverage in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_converter.cc -->
