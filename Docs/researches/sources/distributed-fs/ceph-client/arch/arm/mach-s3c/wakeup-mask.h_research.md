<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/wakeup-mask.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/wakeup-mask.h

### Purpose
Declares the wake-mask mapping structure and synchronization helper for Samsung suspend code.

### Important APIs, Types, And Functions
`NO_WAKEUP_IRQ` marks wake-mask bits without a Linux IRQ. `struct samsung_wakeup_mask` pairs an IRQ number with a wake-disable bit. `samsung_sync_wakemask()` applies the mapping.

### Control Flow
No direct flow; SoC PM code builds arrays and calls the helper.

### State, Persistence, And Dependencies
The mapping table is caller-owned static data. Depends on Linux IRQ numbers and SoC wake register bit definitions.

### Integration Points
Used by S3C64xx PM preparation.

### Risks
Incorrect IRQ-to-bit mapping directly affects suspend wake behavior.

### Test Signals
Wake source tests for each mapped IRQ validate the table and helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/wakeup-mask.h -->
