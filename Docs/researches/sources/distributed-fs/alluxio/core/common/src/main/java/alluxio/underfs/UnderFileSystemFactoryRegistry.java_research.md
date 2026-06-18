## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemFactoryRegistry.java

### Purpose
`UnderFileSystemFactoryRegistry` centralizes discovery, registration, version filtering, and lookup of UFS factories.

### Important APIs, Types, And Functions
Static methods include `available`, `find`, `findAllWithRecorder`, `getSupportedVersions`, `register`, `unregister`, and `reset`. The static registry is an `ExtensionFactoryRegistry<UnderFileSystemFactory, UnderFileSystemConfiguration>` configured with jar pattern `alluxio-underfs-*.jar`.

### Control Flow
Initialization happens in a synchronized `init`. `find` calls `findAllWithRecorder` and returns the first eligible factory or null with a warning. `findAllWithRecorder` asks the extension registry for candidates, warns/records supported versions when a configured `UNDERFS_VERSION` has no eligible factories, and optionally filters by exact `getVersion()` when strict version matching is enabled. `getSupportedVersions` unsets the requested version on a copy and gathers non-empty version strings from otherwise supporting factories.

### State And Persistence
State is the static registry instance and the service-loaded/manual factory list. No persistent storage is touched.

### Dependencies And Integration Points
Integrates Java `ServiceLoader`, Alluxio extension discovery, `Recorder`, and UFS version configuration keys. It is the first selection point used by `UnderFileSystem.Factory`.

### Risks
The class is marked `@NotThreadSafe`; static mutation through register/unregister/reset can affect concurrent tests or runtime factory lookup. Shaded jars can drop service metadata unless Maven service resource transformers are used. Strict version matching can filter out all factories even when path support exists.

### Test Signals
`UnderFileSystemTest` uses `find` to verify no unwanted core factory claims local or external-module schemes in a core-only classpath.
