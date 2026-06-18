<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-usb-phy-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-usb-phy-s3c64xx.c

### Purpose
Controls S3C64xx USB high-speed OTG PHY power/reset sequencing for the DWC2 controller.

### Important APIs, Types, And Functions
The setup code uses USB PHY register macros to enable PHY clocks, clear power-down bits, assert/deassert reset, and configure PHY mode for OTG.

### Control Flow
DWC2 platform setup or board code installs platform data; controller initialization calls the PHY setup path before USB operation and may call suspend/powerdown paths later.

### State, Persistence, And Dependencies
State is PHY register configuration and controller platform data. Dependencies include `regs-usb-hsotg-phy-s3c64xx.h`, system clock/power registers, and DWC2 platform hooks.

### Integration Points
Cragganmore attaches `dwc2_hsotg_plat` data for OTG.

### Risks
PHY sequencing is timing-sensitive. Incorrect clock or reset control causes failed enumeration or resume.

### Test Signals
USB gadget/host enumeration, disconnect/reconnect cycles, and suspend/resume with USB wake disabled/enabled validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-usb-phy-s3c64xx.c -->
