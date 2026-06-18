<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/usb-tusb6010.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/usb-tusb6010.h

### Purpose
`usb-tusb6010.h` declares the board setup interface for attaching a TUSB6010 controller to OMAP GPMC.

### Important APIs, Types, And Functions
It declares `tusb6010_setup_interface(struct musb_hdrc_platform_data *data, unsigned int ps_refclk, unsigned int waitpin, unsigned int async_cs, unsigned int sync_cs, unsigned int dmachan)`.

### Control Flow
There is no runtime flow in the header. It supplies the prototype used by board files that provide MUSB platform data and GPMC wiring information.

### State, Persistence, And Dependencies
The header has no state and depends on `struct musb_hdrc_platform_data` being visible to callers.

### Integration Points
It bridges board setup code and `usb-tusb6010.c`.

### Risks
Callers must pass a valid reference clock period, wait pin, chip selects, and platform data; the implementation rejects missing clock/data at runtime.

### Test Signals
Builds of board files using TUSB6010 should type-check this prototype, and runtime setup should register the MUSB device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/usb-tusb6010.h -->
