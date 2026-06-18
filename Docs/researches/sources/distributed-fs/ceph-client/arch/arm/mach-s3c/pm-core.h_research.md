<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-core.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-core.h

### Purpose
Compatibility wrapper selecting `pm-core-s3c64xx.h`.

### Important APIs, Types, And Functions
No new API is defined; the included file supplies PM hooks and wake masks.

### Control Flow
No runtime behavior.

### State, Persistence, And Dependencies
No state; depends on `pm-core-s3c64xx.h`.

### Integration Points
Used by generic-looking local PM code to bind to the S3C64xx implementation.

### Risks
Hard selection would be wrong if shared with another S3C variant without updating the wrapper.

### Test Signals
S3C64xx PM build and suspend coverage validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-core.h -->
