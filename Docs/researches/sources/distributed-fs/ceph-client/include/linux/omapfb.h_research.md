<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omapfb.h -->
# sources/distributed-fs/ceph-client/include/linux/omapfb.h

## Purpose
This header declares OMAP framebuffer platform data for LCD panel/controller selection and a board-init helper for setting LCD configuration.

## Important APIs, types, and functions
`struct omap_lcd_config` holds panel name, controller name, reset GPIO, and data line count. `struct omapfb_platform_data` wraps the LCD config. `omapfb_set_lcd_config()` stores early board LCD configuration. It also includes the UAPI OMAP framebuffer header.

## Control flow
Architecture/board setup calls `omapfb_set_lcd_config()` during init, and the OMAP framebuffer driver consumes the platform data to select panel/controller wiring.

## State and persistence
LCD configuration persists as platform data for the framebuffer driver lifetime. The header itself stores no state.

## Dependencies and integration points
It depends on UAPI `linux/omapfb.h`, init annotations, and legacy OMAP framebuffer/platform setup.

## Risks and test signals
Risks include fixed 16-byte name truncation, invalid reset GPIO, incorrect data-line count, and legacy platform data conflicting with DT display descriptions. Test board init, panel/controller name matching, reset GPIO behavior, and OMAP framebuffer probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omapfb.h -->
