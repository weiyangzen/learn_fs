<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/access_control_list.h -->
# sources/distributed-fs/lizardfs/src/common/access_control_list.h

## Purpose

This header defines LizardFS's compact POSIX-like ACL object, including storage, serialization, permission evaluation, and string conversion API.

## Important APIs, Types, and Functions

Key type is `AccessControlList::Entry`, packed as id plus 4-bit type and 4-bit access mask. Entry types include named user/group, owner user, owner group, other, mask, and invalid. Public APIs include `toString()`, `fromString()`, `getMode()`, `setMode()`, `setEntry()`, `removeEntry()`, `getEntry()`, `getEffectiveRights()`, `minimalAcl()`, `applyMask()`, iterators, comparisons, and generated serialization methods.

## Control Flow

Basic permissions are stored in four nibbles inside `basic_permissions_`: other, group, owner, and mask. Named entries are kept in a compact sorted `flat_set`. Permission evaluation checks owner first, then named user with mask, then owning/named groups ORed together with mask, and finally other.

## State and Persistence Behavior

The object is value-type state. Serialization includes `basic_permissions_` and the named-entry set. `kMaskUnset` (`0xF`) marks absent mask state.

## Dependencies and Integration Points

It depends on compact containers, exceptions, and serialization macros. It is used by ACL converters, metadata, and permission checks.

## Risks and Edge Cases

Many invalid-type paths are assert-only. `setEntry()` silently drops named entries if the compact vector reaches max size. Effective rights require the group container to be searchable by linear `std::find`, so caller container semantics matter. Packed bitfields are serialized manually to avoid ABI layout dependence.

## Test Signals

String grammar tests are present. Additional signals should include serialization round trips, effective-rights cases with masks and multiple groups, maximum named-entry capacity, and mode changes on extended ACLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/access_control_list.h -->
