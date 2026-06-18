<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-gpio.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-gpio.h

Purpose: Minimal public header for the VIA GPIO platform driver.

Important APIs/types/functions: Declares `viafb_gpio_init()` and `viafb_gpio_exit()` for registration/unregistration from `via-core.c`.

Control flow and state: No executable flow. Runtime state lives in `via-gpio.c`'s static `viafb_gpio_config` and in hardware GPIO registers.

Dependencies and integration points: Included by `via-core.c` so the core can bring the GPIO platform driver up before registering PCI devices and tear it down on module exit. Risks are limited to keeping prototypes in sync. Test signals are build coverage and module init/exit sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-gpio.h -->
