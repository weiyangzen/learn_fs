<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/platformdata.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/platformdata.c

### Purpose
Provides helpers that copy platform data into Samsung legacy platform devices safely during early board setup.

### Important APIs, Types, And Functions
The main helper pattern allocates or copies board-provided platform data into a target `platform_device.dev.platform_data`, allowing board data to be declared `__initdata`.

### Control Flow
Board-specific setter functions call the helper before platform devices probe. The copied data persists after init memory is discarded.

### State, Persistence, And Dependencies
State is the copied platform data attached to platform devices. Dependencies include platform device structures, allocation helpers, and Samsung device declarations.

### Integration Points
Used by keypad, SDHCI, framebuffer, I2C, and other legacy board files that provide platform data at init time.

### Risks
Copy size must match the target structure. Embedded pointers inside platform data still need valid lifetime unless the specific setter deep-copies them.

### Test Signals
Boot with init memory freed and successful later driver probe validates that copied platform data does not reference discarded structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/platformdata.c -->
