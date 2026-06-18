<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/usb-phy.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/usb-phy.h

### Purpose
Declares USB PHY setup interfaces for S3C64xx board and controller code.

### Important APIs, Types, And Functions
The header exposes architecture USB PHY initialization or control hooks used by the DWC2/S3C USB setup code.

### Control Flow
No direct flow; controller/platform code calls the declared hooks during probe, suspend, or resume.

### State, Persistence, And Dependencies
State lives in PHY hardware registers and platform data. Depends on S3C64xx USB PHY register definitions.

### Integration Points
Used with `setup-usb-phy-s3c64xx.c` and Cragganmore OTG platform data.

### Risks
Missing declarations or config mismatches can leave USB setup unhooked.

### Test Signals
Build coverage and DWC2 PHY initialization validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/usb-phy.h -->
