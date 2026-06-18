# sources/distributed-fs/eos/unit_tests/mgm/AclCmdTests.cc

## Purpose
Tests user-facing ACL command helper logic for parsing ACL strings into ordered rule maps, locating/inserting rules, moving existing rules, and validating requested insertion positions.

## Important APIs, types, and functions
The tests cover `AclCmd::GenerateRuleMap`, `key_position`, `insert_or_assign`, `get_iterator`, and `AclCmd::GetRulePosition`. `RuleMap` is treated as an ordered vector-like structure of ACL keys and bitmasks.

## Control flow
The parsing test converts a compound ACL string with grant/deny modifiers into expected bitmasks. Position tests build a map, insert new keys, update existing keys, verify move semantics with lvalue/rvalue keys, and exercise repositioning when `move_existing` is true.

## State and persistence
All state is local to tests. The output bitmasks and ordering are command semantics that influence persisted ACL xattr strings when admin/user ACL commands update namespace metadata.

## Dependencies and integration points
Depends on Google Test and `mgm/proc/user/AclCmd.hh`. It is tied to MGM proc/user ACL command behavior and ACL serialization order.

## Risks and test signals
The tests catch ordering regressions that plain maps would hide. Risks include brittle binary literals, unclear move expectations, and incomplete coverage of malformed ACL tokens. Additional tests should cover duplicate group/user keys in parsed strings, invalid permission characters, empty rule maps, and position arguments from real command parsing.
