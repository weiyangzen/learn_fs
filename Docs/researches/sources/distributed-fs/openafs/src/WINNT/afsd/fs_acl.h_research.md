# sources/distributed-fs/openafs/src/WINNT/afsd/fs_acl.h

## Purpose

`fs_acl.h` defines the ACL data structures, rights constants, mutation operation enum, and helper prototypes shared between `fs.c` and `fs_acl.c`.

## Important APIs, Types, and Functions

`struct Acl` stores ACL type (`dfs`), DFS default cell, plus/minus counts, and linked lists. `struct AclEntry` stores one principal name and rights mask. The header defines DFS wire-protocol rights bits, application-defined DFS user bits, `DFS_SEPARATOR`, and `enum rtype` values: `add`, `destroy`, `deny`, `reladd`, and `reldel`. Public helpers include `ParseAcl()`, `AclToString()`, `EmptyAcl()`, `CleanAcl()`, `ChangeList()`, `FindList()`, `PruneList()`, `ZapAcl()`, and `ZapList()`.

## Control Flow

There is no executable control flow, but the structures drive the ACL command lifecycle: parse text into linked lists, modify entries with an `rtype`, prune invalid zero/deleted entries, serialize text, then free all list memory.

## State and Persistence Behavior

The header defines transient in-process ACL state. Persistent ACL changes occur only when serialized text is passed to cache-manager pioctls by callers. `sec_rgy_name_t` and `ACL_MAXNAME` establish fixed limits that shape accepted ACL names and DFS cell strings.

## Dependencies and Integration Points

It relies on AFS integer types and rights constants from including files. It integrates with the Windows `fs` command ACL implementation and preserves DFS rights values that are part of the translator wire protocol.

## Risks and Edge Cases

Rights constants are protocol-sensitive and must not be renumbered. `ACL_MAXNAME` truncation or mismatch with parser `%100s` limits can affect principal names. The `dfs` field doubles as a Boolean and ACL subtype, so callers must preserve values 0 through 3 rather than treating it as arbitrary truth.

## Test Signals

Build tests should cover all include sites. Behavioral tests should verify every rights bit prints and parses correctly, `rtype` operations mutate lists as expected, and DFS object/initial-directory/initial-object ACL types survive parse and serialization.
