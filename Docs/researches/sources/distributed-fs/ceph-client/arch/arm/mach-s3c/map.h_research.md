<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map.h

### Purpose
Compatibility wrapper that includes `map-s3c64xx.h`.

### Important APIs, Types, And Functions
No new symbols; all mappings come from the S3C64xx map header.

### Control Flow
No runtime behavior.

### State, Persistence, And Dependencies
No state; depends on `map-s3c64xx.h`.

### Integration Points
Used by local files that include `"map.h"` for the currently supported S3C64xx platform.

### Risks
It hard-selects S3C64xx mappings for generic-looking local include users.

### Test Signals
Build coverage of S3C64xx common and PM code validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map.h -->
