<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/corgi_lcd.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/corgi_lcd.h

Purpose: This header defines platform data and a helper for the SPI-attached Corgi LCD/backlight controller.

Important APIs/types/functions: It defines QVGA/VGA mode constants, `corgi_lcd_platform_data` with initial mode, max/default intensity, limit mask, and optional `notify()`/`kick_battery()` callbacks, plus `corgi_lcd_limit_intensity()`.

Control flow: Board data configures probe-time display/backlight behavior. The driver may notify intensity changes, kick battery handling, and apply external intensity limits through the exported helper.

State and persistence: Static board data persists in platform data; runtime intensity limits are maintained by the driver.

Dependencies/integration: Integrates with SPI, LCD/backlight subsystems, board battery logic, and legacy Sharp device support.

Risks and test signals: Risks include intensity outside supported range, incorrect mode, callback lifetime issues, and limit mask misapplication. Test display mode, brightness transitions, battery callbacks, and external limit updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/corgi_lcd.h -->
