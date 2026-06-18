<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/access_control_list.cc -->
# sources/distributed-fs/lizardfs/src/common/access_control_list.cc

## Purpose

This file implements string parsing and formatting for `AccessControlList`.

## Important APIs, Types, and Functions

Implemented public methods are `AccessControlList::fromString()` and `toString()`. Internal helpers are `accessMaskToChar()`, `accessMaskFromChar()`, `entryTypeFromChar()`, and `eat()`.

## Control Flow

`fromString()` requires an `A` prefix and three octal permission digits for owner, group, and other. It then parses slash-delimited extended entries of the form `u:id:mask`, `g:id:mask`, or `m::mask`, checks repeated entries and missing ids, and populates ACL entries. `toString()` emits minimal permissions, named users, named groups, and an optional mask in deterministic order.

## State and Persistence Behavior

The parser returns a new in-memory ACL. Persistence occurs only when callers serialize or store the resulting object elsewhere.

## Dependencies and Integration Points

It depends on `AccessControlList` storage methods and exception type. Metadata, ACL xattr, and CLI layers can use this compact `A...` grammar.

## Risks and Edge Cases

Numeric ids use `strtol()` and are stored in `uint32_t`; overflow and negative text are not explicitly rejected beyond malformed pointer progress. Only masks `0` through `7` are valid. Grammar is strict about delimiters, so output compatibility depends on exact formatting.

## Test Signals

`access_control_list_unittest.cc` covers round-trip formatting for minimal/extended ACLs and many malformed strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/access_control_list.cc -->
