## sources/distributed-fs/alluxio/underfs/kodo/pom.xml

### Purpose
This Maven module builds the Qiniu Kodo UFS extension.

### Important APIs, Types, And Functions
The artifact is `alluxio-underfs-kodo`. Dependencies include Qiniu Java SDK `7.2.17`, OkHttp `3.10.0`, and Alluxio core common as provided plus test jar. Build plugins shade and copy/rename the extension artifact.

### Control Flow
The module inherits from `alluxio-underfs` and has no feature profiles. It packages external object-store dependencies into the extension as configured by parent/plugin behavior.

### State, Persistence, And Dependencies
Build output is the Kodo extension jar. Runtime dependencies are Qiniu SDK, OkHttp, and Alluxio common UFS abstractions.

### Integration Points
The module supplies `KodoUnderFileSystemFactory`, client wrappers, streams, and tests for the Kodo scheme.

### Risks
The external SDK versions are fixed and relatively old; compatibility with current Kodo endpoints and OkHttp TLS defaults should be validated separately.

### Test Signals
The module includes unit tests for factory registration, output stream local buffering, and failure handling on listing-backed operations.
