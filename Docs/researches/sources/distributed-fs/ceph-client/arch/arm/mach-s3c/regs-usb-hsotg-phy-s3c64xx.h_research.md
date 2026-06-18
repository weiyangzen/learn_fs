<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-usb-hsotg-phy-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-usb-hsotg-phy-s3c64xx.h

### Purpose
Defines S3C64xx USB high-speed OTG PHY control register offsets and bit fields.

### Important APIs, Types, And Functions
Macros name PHY control, power, clock, reset, and tune fields under `S3C_VA_USB_HSPHY`.

### Control Flow
No direct flow. USB PHY setup code toggles power, reset, clock selection, and suspend bits using these definitions.

### State, Persistence, And Dependencies
State is USB PHY hardware register content. Depends on early mapping of the USB HSPHY virtual base.

### Integration Points
Used by `setup-usb-phy-s3c64xx.c` and DWC2 OTG platform initialization.

### Risks
Incorrect sequencing can leave the PHY in reset, powered down, or clocked from the wrong source.

### Test Signals
USB gadget/host enumeration, PHY suspend/resume, and register-level debug on cable attach validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-usb-hsotg-phy-s3c64xx.h -->
