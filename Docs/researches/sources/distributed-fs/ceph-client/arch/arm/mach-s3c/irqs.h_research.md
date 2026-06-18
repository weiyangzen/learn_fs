<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irqs.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irqs.h

### Purpose
Thin compatibility include that exposes `irqs-s3c64xx.h` through the local `mach-s3c` include name.

### Important APIs, Types, And Functions
It exports no new API; all IRQ constants and macros come from `irqs-s3c64xx.h`.

### Control Flow
There is no runtime behavior.

### State, Persistence, And Dependencies
No state. It depends entirely on the S3C64xx IRQ header and exists to preserve include paths used by local C files.

### Integration Points
Included by board, PM, and setup files that refer to local `"irqs.h"` rather than the SoC-specific header.

### Risks
If new S3C-family variants were added, this hard include would select S3C64xx numbering for all users.

### Test Signals
Compile coverage of all local users verifies this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irqs.h -->
