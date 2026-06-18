## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UnderFileSystemConfigurationTest.java

### Purpose
Tests UFS configuration precedence, read-only preservation, and mount-specific configuration isolation.

### Important APIs, Types, And Functions
Exercises `UnderFileSystemConfiguration.defaults`, constructor, `createMountSpecificConf`, `getMountSpecificConf`, `get`, `getInt`, `isSet`, and `isReadOnly`.

### Control Flow
Tests set and unset S3 keys and listing length in copied/modifiable configurations. They verify global values are visible, mount-specific values override globals or fill missing keys, read-only survives cloning, repeated mount-specific creation does not accumulate prior mount options, and the base configuration remains without mount-specific values.

### State And Persistence
Uses `ConfigurationRule` and copied global configuration in memory. No persistence.

### Dependencies And Integration Points
Provides regression coverage for mount table option propagation into UFS factories and implementations.

### Risks
The first test constructs a config from `Configuration.global()` while setting `mConfiguration`, which relies on global/test configuration behavior. It does not test `toUserPropertyMap`, source labeling for multiple properties, or validation.

### Test Signals
Strong signal that mount options have higher precedence than global config and that option merging is non-mutating.
