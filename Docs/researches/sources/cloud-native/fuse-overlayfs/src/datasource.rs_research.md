<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/datasource.rs -->
# sources/cloud-native/fuse-overlayfs/src/datasource.rs

Purpose: trait abstraction for accessing overlay layer data sources.

Important APIs: constants define stat override xattrs; `StatOverrideMode` records none/user/privileged/containers modes; `DirIterator` and `DirEntry` abstract directory scanning; `DataSource` defines initialization, existence/stat/open/readlink/xattr operations, NFS file handle hashing, root fd/device reporting, stat override reporting, and NFS handle support reporting.

State and integration: trait has no state itself; implementations such as `DirectAccess` hold file descriptors and device metadata. It is consumed by layers, overlay operations, and copy-up code. Risks include every implementation needing safe path resolution internally, trait object overhead, and mode/xattr semantics needing to match the C implementation. Test signal is through direct datasource behavior and overlay integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/datasource.rs -->
