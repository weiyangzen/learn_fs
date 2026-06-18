# sources/distributed-fs/eos/mgm/proc/user/AclCmd.cc

## Purpose

`AclCmd.cc` implements the protobuf-backed `AclCmd` command for listing and modifying EOS `sys.acl` and `user.acl` extended attributes. It converts between textual ACL rules and bitmasks, supports recursive directory updates, optional insertion positions, identifier translation, and read/write metadata locking around namespace objects.

## Important APIs, Types, and Functions

`AclCmd::ProcessRequest()` dispatches `AclProto::LIST` and `AclProto::MODIFY`. `GetAcls()` reads `sys.acl`, `user.acl`, and `sys.eval.useracl` from a `FileOrContainerMD`. `ModifyAcls()` parses the requested rule, resolves the target set, locks each metadata object, applies rule changes, and stores the new ACL xattr. Parsing helpers include `GetRuleFromString()`, `GenerateRuleMap()`, `GetRuleBitmask()`, `ParseRule()`, `CheckCorrectId()`, `ApplyRule()`, `GenerateAclString()`, `AclBitmaskToString()`, and `GetRulePosition()`.

## Control Flow

LIST prefetches the item, gets a read lock on either file or container metadata, extracts requested ACLs, converts numeric ids back to names best-effort with `Acl::ConvertIds`, and returns `ENODATA` if no ACL content is present. MODIFY validates the incoming rule first. User ACL modification additionally requires `sys.eval.useracl` for non-root users. Recursive mode calls `_find` to collect directories and skips EOS version directories; single-path mode may operate on either a file or a container. For each path, the command prefetches metadata, takes a write lock, reads current ACLs, turns them into an ordered `RuleMap`, validates requested insertion position, applies additions/removals/set semantics, serializes the map, and calls `gOFS->_attr_set` with a `FusexCastBatch`.

## State and Persistence

The persistent state is the `sys.acl` or `user.acl` xattr on target namespace entries. The in-command state is `mId`, `mAddRule`, `mRmRule`, and `mSet`, all derived from the rule string. Recursive modification can update many container ACL attributes. FUSE notifications are batched until metadata locks are released. Existing ACL order is preserved with `std::list<Rule>` and can be changed when a position is supplied.

## Dependencies and Integration Points

This command depends on `IProcCommand`, `proto/Acl.pb.h`, `mgm/acl/Acl.hh`, `gOFS->eosView`, `eos::Prefetcher`, metadata locking helpers, `gOFS->_find`, and `gOFS->_attr_get/_attr_set`. It integrates with EOS ACL identity conversion and namespace xattr semantics rather than POSIX mode bits.

## Risks and Test Signals

Parser edge cases are the highest-risk area: ACL strings use both `+` as an operation and as a permission prefix (`+d`, `+u`), `CheckCorrectId()` assumes enough characters for `id.at(1)`, and unknown permission characters in stored ACLs are ignored. Recursive updates are partially tolerant of missing directories but fail on other metadata exceptions. Test signals should cover list user/sys/both, set versus add/remove grammar, egroup and key ids, invalid ids, position insertion and moving existing entries, recursive updates over disappearing directories, user ACL rejection without `sys.eval.useracl`, and serialization order.
