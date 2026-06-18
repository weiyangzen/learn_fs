<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/access_control_list_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/access_control_list_unittest.cc

## Purpose

This file tests ACL string parsing and formatting.

## Important APIs, Types, and Functions

Macros `EXPECT_GOOD_ACL` and `EXPECT_WRONG_ACL` wrap `AccessControlList::fromString()` and `toString()`. Tests are `ToStringMimial`, `ToStringExtended`, and `ToStringErrors`.

## Control Flow

Good cases parse a string and require the serialized string to match exactly. Bad cases assert `IncorrectStringRepresentationException`.

## State and Persistence Behavior

Only local ACL values are created. No persistent state is used.

## Dependencies and Integration Points

The tests use GoogleTest and the ACL string API.

## Risks and Edge Cases

The test name has a typo (`Mimial`). Coverage is centered on string grammar; it does not cover effective rights, binary serialization, mode setters, or ACL converter xattrs.

## Test Signals

Passing tests signal stable canonical string output and robust rejection of malformed ACL strings, duplicate entries, missing ids, and invalid masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/access_control_list_unittest.cc -->
