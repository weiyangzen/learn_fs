<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/Kconfig

Purpose: declares the FBTFT staging subsystem and all small SPI TFT/OLED/LCD controller driver options.

Important APIs/types/functions: `menuconfig FB_TFT` is a tristate requiring `FB`, `SPI`, `BACKLIGHT_CLASS_DEVICE`, and `GPIOLIB || COMPILE_TEST`; it selects `FB_BACKLIGHT` and `FB_SYSMEM_HELPERS_DEFERRED`. Child tristates enable individual panel/controller drivers such as AGM1264K-FL, HX/ILI/SSD/ST/UC controllers, RA8875, and tinylcd.

Control flow: when `FB_TFT` is enabled, its child symbols become visible and the matching Makefile entries compile core and panel modules.

State and persistence: configuration only; runtime state belongs to the selected driver modules.

Dependencies and integration: connects staging FBTFT to framebuffer, SPI, GPIO, and backlight kernel subsystems.

Risks: child options generally do not repeat dependencies, so the top-level gate must remain accurate. Help text is terse and does not encode panel bus-width constraints.

Test signals: Kconfig with missing SPI/FB/backlight/GPIO dependencies, all drivers as modules, and `COMPILE_TEST` coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/Kconfig -->
