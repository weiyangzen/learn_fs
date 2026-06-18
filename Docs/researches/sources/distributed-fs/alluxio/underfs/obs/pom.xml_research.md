## sources/distributed-fs/alluxio/underfs/obs/pom.xml

### Purpose
This Maven module builds the Huawei OBS UFS extension.

### Important APIs, Types, And Functions
The artifact is `alluxio-underfs-obs`. Properties define `obs.version` and `hamcrest.version`. Dependencies include Huawei `esdk-obs-java`, Alluxio core common, Hamcrest for tests, and Alluxio test jar. Build plugins shade and copy/rename the extension artifact.

### Control Flow
There are no feature profiles. The module inherits common UFS build behavior from the parent.

### State, Persistence, And Dependencies
Build output is the OBS extension jar. Runtime state is provided by the OBS SDK and Alluxio common abstractions.

### Integration Points
The module provides OBS object-store implementation classes, including normal and streaming output streams.

### Risks
SDK version pinning can affect compatibility with OBS bucket types and PFS-specific APIs. The POM includes test dependencies but this subset does not include OBS tests.

### Test Signals
No OBS-specific tests are listed in this work item, so coverage should be added for stream and PFS behavior.
