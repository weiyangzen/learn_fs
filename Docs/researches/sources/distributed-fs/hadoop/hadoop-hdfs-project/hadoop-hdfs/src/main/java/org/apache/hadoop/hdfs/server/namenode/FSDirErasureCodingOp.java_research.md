# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirErasureCodingOp.java

## Purpose
`FSDirErasureCodingOp` manages erasure-coding policy lookup, directory policy XAttr mutation, system policy add/remove/enable/disable, and effective policy resolution for paths and files.

## Important APIs, Types, And Functions
- Policy lookup: `getEnabledErasureCodingPolicyByName`, `getErasureCodingPolicyByName`, `getErasureCodingPolicy`, `unprotectedGetErasureCodingPolicy`, `getErasureCodingPolicies`, and `getErasureCodingCodecs`.
- Policy mutation: `setErasureCodingPolicy`, `unsetErasureCodingPolicy`, `addErasureCodingPolicy`, `removeErasureCodingPolicy`, `enableErasureCodingPolicy`, and `disableErasureCodingPolicy`.
- Internal helpers serialize policy names into `XATTR_ERASURECODING_POLICY` using `WritableUtils` and apply/remove XAttrs through `FSDirXAttrOp`.

## Control Flow
Setting a policy requires the FS write lock, validates the named policy is enabled, resolves the path with `WRITE_LINK`, checks write access, requires the target inode to be a directory, serializes the policy name into an XAttr, and creates or replaces the XAttr depending on whether one exists. Unset follows the same path and removes only a directly set directory EC XAttr, throwing `NoECPolicySetException` when absent. Effective lookup walks from the target toward root, returning a file's encoded EC policy ID first, then directory XAttrs, and stopping at symlinks.

## State And Persistence Behavior
Directory EC policies persist as XAttrs, while system-wide policy state is managed by `ErasureCodingPolicyManager` and logged with dedicated edit-log records. Set/unset directory operations log `logSetXAttrs` or `logRemoveXAttrs`. Effective file layout is also stored on `INodeFile` as an EC policy ID used by write/block code.

## Dependencies And Integration Points
The operation depends on `FSNamesystem` read/write lock assertions, `FSDirectory` path checks, `ErasureCodingPolicyManager`, `FSDirXAttrOp`, `CodecRegistry`, `WritableUtils`, and `XAttrHelper`. It feeds `FSDirWriteFileOp` for striped file creation and `FSDirStatAndListingOp` for status/block location metadata.

## Risks And Edge Cases
Only enabled policies can be set through the user API, but valid disabled/removed policies matter for admin state transitions and replay. Symlink traversal is not supported for inherited EC policy resolution. Returning `null` for REPLICATION policy is intentional in the external `getErasureCodingPolicy(String)` path. XAttr serialization must remain compatible with edit logs.

## Test Signals
Tests should cover invalid/disabled policy errors, set/replace on directory, unset absent policy, file target rejection, symlink inheritance stop, inherited parent policy lookup, file policy ID lookup, REPLICATION suppression in API results, admin add/remove/enable/disable edit logging, and codec registry exposure.
