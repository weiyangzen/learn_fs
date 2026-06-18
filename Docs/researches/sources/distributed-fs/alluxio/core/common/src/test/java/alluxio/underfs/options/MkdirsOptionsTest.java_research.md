## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/MkdirsOptionsTest.java

### Purpose
Tests defaults, security interaction, setters, and equality for `MkdirsOptions`.

### Important APIs, Types, And Functions
Uses `MkdirsOptions.defaults`, getters/setters, `ModeUtils.applyDirectoryUMask`, and Guava `EqualsTester`.

### Control Flow
Default tests verify create-parent true, null owner/group, and umask-applied directory mode. Security-enabled test configures a copied conf but calls defaults with the global configuration, still expecting null owner/group and default mode. Field test sets randomized create-parent, owner, group, and mode.

### State And Persistence
In-memory configuration and option state only.

### Dependencies And Integration Points
Protects mkdir option defaults consumed by UFS directory creation.

### Risks
The security-enabled test creates `conf` but passes `mConfiguration`, so it mostly verifies defaults rather than the configured object. No coverage for `toString` beyond equality.

### Test Signals
Confirms recursive parent creation is the default for mkdirs and security does not implicitly fill owner/group.
