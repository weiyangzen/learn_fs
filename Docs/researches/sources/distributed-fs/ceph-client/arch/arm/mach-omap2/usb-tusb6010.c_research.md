<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/usb-tusb6010.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/usb-tusb6010.c

### Purpose
`usb-tusb6010.c` configures GPMC chip-select windows and timings for a TI TUSB6010 USB controller exposed as a platform MUSB device.

### Important APIs, Types, And Functions
The board-facing API is `tusb6010_setup_interface()`. Timing helpers are `tusb_set_async_mode()`, `tusb_set_sync_mode()`, and `tusb6010_platform_retime()`. Static platform state includes async/sync chip selects, reference-clock period, GPMC settings, resources, DMA mask, and `tusb_device`.

### Control Flow
Setup requests async and sync GPMC chip selects, programs wait pins and 16-bit multiplexed address/data settings, calculates conservative timings from the TUSB6010 datasheet, registers platform resources, stores MUSB platform data, and registers the `musb-tusb` platform device. Retiming can switch timing calculations between reference-clock and 60 MHz oscillator modes.

### State, Persistence, And Dependencies
Chip-select numbers and reference clock period persist in static globals after setup. The file depends on the OMAP GPMC timing API, MUSB platform data, and platform-device registration.

### Integration Points
Board files call `tusb6010_setup_interface()` during init. The `musb-tusb` driver consumes the two memory resources and can call the retime hook through platform data behavior.

### Risks
The `dmachan` argument is unused here, so DMA channel expectations must be handled elsewhere. Failed setup after the first GPMC request does not unwind all earlier reservations. Timing constants are hardware-specific and should not be generalized.

### Test Signals
Board boot should register `musb-tusb`, map both async and sync resources, and survive clock-mode changes with USB enumeration and DMA/PIO transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/usb-tusb6010.c -->
