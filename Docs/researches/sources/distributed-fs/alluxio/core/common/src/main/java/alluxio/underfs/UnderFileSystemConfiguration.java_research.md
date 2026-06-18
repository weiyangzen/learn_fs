## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemConfiguration.java

### Purpose
`UnderFileSystemConfiguration` wraps an `AlluxioConfiguration` with UFS-specific behavior, mainly read-only state and mount-specific option precedence.

### Important APIs, Types, And Functions
Static constructors are `defaults(AlluxioConfiguration)` and `emptyConfig()`. Instance methods include `isReadOnly`, `createMountSpecificConf`, `getMountSpecificConf`, and `toUserPropertyMap`. The rest of the class delegates the `AlluxioConfiguration` interface to `mAlluxioConf`.

### Control Flow
`createMountSpecificConf` copies all properties, merges the provided mount map with `Source.MOUNT_OPTION`, and returns a new configuration preserving the read-only flag. `getMountSpecificConf` scans keys whose source is `MOUNT_OPTION`. `toUserPropertyMap` walks user keys and stringifies values while preserving nulls.

### State And Persistence
State is the wrapped configuration and immutable read-only flag. Creating mount-specific config copies property state but does not mutate the original.

### Dependencies And Integration Points
Used by UFS factories, root mount creation, object-store implementations, and options defaults. It depends on `AlluxioProperties`, `InstancedConfiguration`, property `Source`, and `ConfigurationValueOptions`.

### Risks
The class is `@NotThreadSafe` because the wrapped configuration may be mutable. Mount-specific maps accept `Object` values keyed by property names, so invalid key/value types fail later during configuration resolution. `EMPTY_CONFIG` is shared and should remain effectively immutable.

### Test Signals
`UnderFileSystemConfigurationTest` checks global property lookup, mount-specific override, missing property behavior, `isSet`, preservation of read-only, repeated mount-specific creation without mutating the base, and mount-specific conf extraction.
