<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-common.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-common.h

### Purpose
Declares the shared S3C register save structure and helper APIs.

### Important APIs, Types, And Functions
`struct sleep_save` stores an MMIO register pointer and saved value. `SAVE_ITEM(x)` initializes an entry. The declared helpers are `s3c_pm_do_save()`, `s3c_pm_do_restore()`, and `s3c_pm_do_restore_core()`.

### Control Flow
No direct flow; SoC PM files build arrays and pass them to the helpers.

### State, Persistence, And Dependencies
State is carried in caller-owned arrays. It depends on `void __iomem` and unsigned long register storage.

### Integration Points
Included by S3C64xx PM and any other Samsung S3C PM implementation using the common save/restore contract.

### Risks
Register width assumptions follow `unsigned long` and raw 32-bit register behavior. The macro does not validate register addresses.

### Test Signals
Compile coverage and successful suspend/resume register restoration validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-common.h -->
