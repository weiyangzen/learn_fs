# sources/distributed-fs/eos/mgm/proc/user/AclCmd.hh

## Purpose

`AclCmd.hh` declares the protobuf command class and small ordered-map utilities used by `AclCmd.cc`. Its role is to define the ACL rule representation, preserve ACL order during mutation, and expose selected parser helpers for unit testing.

## Important APIs, Types, and Functions

`Rule` is a `std::pair<std::string, unsigned long>` where the key is an ACL principal such as `u:123`, `g:45`, `egroup:name`, or `k:key`, and the value is a permission bitmask. `RuleMap` is a `std::list<Rule>` rather than a map so insertion position is stable and duplicate keys can be replaced without losing order. Utility templates include `key_position`, three `insert_or_assign` overloads, and `get_iterator`, which converts 1-based user positions into iterators.

## Control Flow

The `AclCmd` constructor forwards the request and identity to `IProcCommand` with write-intent enabled. `ProcessRequest()` is the command entry point. Public static helpers `GenerateRuleMap()`, `GetRuleFromString()`, and `GetRulePosition()` support parser tests. `GetRuleBitmask()` and `CheckCorrectId()` expose rule and id validation. Private methods split command behavior into xattr reads, path mutation, parsing, bitmask formatting, and application of parsed rules.

## State and Persistence

The header defines no persisted state, but it shapes persisted ACL encoding by assigning bit positions to textual ACL flags. The `ACLPos` enum covers read, write, execute, management, quota, creation, archive, sys ACL, sys attr, token, write-once, and negative or propagation flags. Instance fields `mId`, `mAddRule`, `mRmRule`, and `mSet` hold one parsed modification request.

## Dependencies and Integration Points

The class inherits from `IProcCommand`, consumes `eos::console::RequestProto`, uses `VirtualIdentity`, and depends on `proto/Acl.pb.h`. It is tightly coupled to EOS ACL string syntax and the `AclCmd.cc` parser. The utility templates are generic but live in this command header, so accidental broader use would inherit the list-based semantics.

## Risks and Test Signals

The custom `insert_or_assign` overload that moves an existing key adjusts the insertion iterator after erase; off-by-one behavior here would reorder ACLs incorrectly. `get_iterator` rejects position zero and positions beyond size. The enum uses `1 << 18` in an `unsigned long` target, which is safe for current values but should be watched if flags grow. Test signals include replacement without movement, movement to earlier and later positions, invalid positions, empty maps, and round-trip bitmask-to-string behavior for every enum flag.
