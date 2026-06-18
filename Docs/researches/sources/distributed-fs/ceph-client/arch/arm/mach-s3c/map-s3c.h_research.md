<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s3c.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s3c.h

### Purpose
Provides S3C-family physical address constants and virtual aliases for legacy platform setup.

### Important APIs, Types, And Functions
It builds on `map-base.h` and defines address constants such as UART, timer, watchdog, and peripheral bases used by S3C platform devices.

### Control Flow
No runtime flow.

### State, Persistence, And Dependencies
No state; it preserves board-file and SoC-helper address contracts.

### Integration Points
Consumed by S3C64xx map headers, device resources, and setup helpers.

### Risks
Incorrect physical base constants produce silent MMIO access to the wrong hardware.

### Test Signals
Boot-time platform device resource registration and successful MMIO probing by UART/timer/watchdog drivers validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s3c.h -->
