## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/MkdirsOptions.java

### Purpose
`MkdirsOptions` carries per-call directory creation options for UFS implementations.

### Important APIs, Types, And Functions
Defaults come from authorization umask. Fields are create-parent, owner, group, and mode. Fluent setters update them; equality, hash code, and `toString` cover all fields.

### Control Flow
The constructor sets create parent true, owner/group null, and directory mode to `ModeUtils.applyDirectoryUMask(Mode.defaults(), authUmask)`. `ObjectUnderFileSystem.mkdirs` uses create-parent to decide whether to recursively create parent marker objects or fail when the parent is absent.

### State And Persistence
Mutable in-memory option only. UFS implementations persist resulting directory markers and metadata if supported.

### Dependencies And Integration Points
Used by `UnderFileSystem.mkdirs` and default mkdir behavior in `BaseUnderFileSystem`.

### Risks
Default parent creation can create more UFS state than a caller expects. Owner/group are null by default even when security is enabled; callers must set explicit metadata when needed.

### Test Signals
`MkdirsOptionsTest` verifies default create-parent true, null owner/group, umask-applied mode, field setters, and equality.
