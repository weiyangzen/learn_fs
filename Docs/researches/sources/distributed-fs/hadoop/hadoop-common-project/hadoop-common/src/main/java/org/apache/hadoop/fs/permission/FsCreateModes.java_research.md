<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsCreateModes.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsCreateModes.java

## Purpose
Wraps a masked create permission together with its original unmasked mode so create APIs can preserve both values.

## Important APIs, Types, And Functions
`applyUMask(FsPermission, FsPermission)` returns an existing create-mode wrapper or creates one. `create(masked, unmasked)` constructs the wrapper. Overrides `getMasked`, `getUnmasked`, and `toString`.

## Control Flow
If a mode already has an unmasked value, `applyUMask` returns it unchanged. Otherwise it applies the umask, then stores masked state in the superclass and unmasked state in a final field.

## State And Persistence
State is the inherited masked `FsPermission` plus final `unmasked`. Serialization follows `FsPermission` behavior unless callers inspect the extra getter.

## Dependencies And Integration Points
Used by create/mkdir flows that need to pass both requested and effective permissions through filesystem layers.

## Risks
Uses Java `assert` for invariant checks, so production does not enforce them. Subclassing `FsPermission` means code that copies or serializes only base fields can lose unmasked information.

## Test Signals
Verify idempotent wrapping, masked/unmasked getters, string format, and behavior when passed through APIs typed as `FsPermission`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsCreateModes.java -->
