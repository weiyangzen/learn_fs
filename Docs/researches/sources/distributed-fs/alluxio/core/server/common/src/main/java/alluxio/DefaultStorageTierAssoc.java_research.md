## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/DefaultStorageTierAssoc.java

### Purpose
`DefaultStorageTierAssoc` implements `StorageTierAssoc` by mapping storage tier aliases to ordinal positions and back.

### Important APIs, Types, And Functions
Constructors build an immutable bidirectional map either from configuration level/template keys or an explicit ordered alias list. `interpretOrdinal` clamps positive ordinals to the last tier and negative ordinals relative to the bottom tier. Public methods are `getAlias`, `getOrdinal`, `size`, `getOrderedStorageAliases`, and `intersectionList`.

### Control Flow
Config construction reads the number of levels and each alias from `Configuration`. Alias lookup interprets the ordinal then uses the inverse bimap. `intersectionList` creates adjacent tier pairs from top to bottom using `BlockStoreLocation.anyDirInTier`.

### State And Persistence
State is an immutable bimap; no persistence. Thread-safety relies on immutability.

### Dependencies And Integration Points
Used by worker/master storage-tier logic to reason about tier hierarchy and move intersections. Depends on `Configuration`, `PropertyKey.Template`, Guava `ImmutableBiMap`, and `BlockStoreLocation`.

### Risks
Duplicate aliases cause bimap build failures. `getOrdinal` will unbox a null value if alias is unknown, causing a null pointer exception. Empty alias lists would make ordinal interpretation invalid.

### Test Signals
No direct test in this subset, but storage tier scheduling and movement tests should cover ordered aliases and intersections.
