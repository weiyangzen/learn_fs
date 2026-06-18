## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/FileLocationOptionsTest.java

### Purpose
Tests `FileLocationOptions` offset behavior.

### Important APIs, Types, And Functions
Uses `FileLocationOptions.defaults`, `getOffset`, `setOffset`, and equality helper.

### Control Flow
Default offset is asserted as zero. The fields test iterates several positive offsets and checks each value.

### State And Persistence
In-memory only.

### Dependencies And Integration Points
Protects option behavior used by UFS file-location APIs.

### Risks
Does not test negative or very large offsets.

### Test Signals
Confirms offset defaults and mutation.
