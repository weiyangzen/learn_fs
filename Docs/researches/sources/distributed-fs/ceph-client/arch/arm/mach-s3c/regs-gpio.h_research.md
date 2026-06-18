<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio.h

### Purpose
Compatibility wrapper for S3C64xx GPIO register definitions.

### Important APIs, Types, And Functions
No new API; includes `regs-gpio-s3c64xx.h`.

### Control Flow
No runtime behavior.

### State, Persistence, And Dependencies
No state; depends on S3C64xx GPIO register header.

### Integration Points
Used by local code that includes generic `"regs-gpio.h"`.

### Risks
Not suitable for another S3C variant without changing the wrapper.

### Test Signals
Compile and GPIO runtime tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio.h -->
