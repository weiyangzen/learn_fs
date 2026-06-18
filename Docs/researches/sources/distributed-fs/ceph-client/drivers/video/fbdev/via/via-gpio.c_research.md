<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-gpio.c

Purpose: Platform GPIO driver exposing selected VIA display GPIO pins through gpiolib. It maps VIA sequencer-register GPIO pairs into a dynamic `gpio_chip`, provides camera GPIO lookup entries, and restores/enables GPIO ports across PM resume.

Important APIs/types/functions: Local data structures include `struct viafb_gpio` describing register/index/mask-shift and `struct viafb_gpio_cfg` holding the `gpio_chip`, active GPIO mapping, names, and `viafb_dev`. GPIO operations are `via_gpio_set()`, `via_gpio_dir_out()`, `via_gpio_dir_input()`, and `via_gpio_get()`. Platform hooks are `viafb_gpio_probe()` and `viafb_gpio_remove()`, with public module helpers `viafb_gpio_init()` and `viafb_gpio_exit()`.

Control flow and state: Probe receives `viafb_dev` from `via-core.c`, scans `vdev->port_cfg` for ports configured as `VIA_MODE_GPIO`, adds both GPIOs for matching register indices, enables each pair under `reg_lock`, registers a dynamic gpiochip labelled `via-gpio`, adds a lookup table for `viafb-camera`, and registers PM hooks. Set/get/direction operations take `reg_lock` and manipulate output-enable, output-value, and input bits in the backing SR registers. Remove unregisters PM, gpiochip, disables active pairs, and clears `ngpio`.

Dependencies and integration points: Depends on gpiolib, `linux/via-core.h`, platform devices created by `via-core.c`, and register helpers `via_read_reg`, `via_write_reg`, `via_write_reg_mask`. Risks include global singleton `viafb_gpio_config`, assumptions that GPIOs come in pairs, a comment noting input direction may be wrong, lookup table installed even when gpiochip add fails, and shared register bits with I2C mode on some ports. Test signals are gpiochip enumeration, direction/value toggles on ports 25/2c/3d, camera lookup resolution, suspend/resume re-enable, and mixed I2C/GPIO port configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-gpio.c -->
