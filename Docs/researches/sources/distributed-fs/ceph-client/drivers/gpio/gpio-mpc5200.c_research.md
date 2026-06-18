# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpc5200.c

Purpose: provides two GPIO controller drivers for Freescale MPC52xx: an 8-line wakeup GPIO block and a 32-line simple GPIO block.

Important APIs/types/functions: shared `struct mpc52xx_gpiochip` stores `gpio_chip`, mapped registers, and shadow copies of data output, GPIO enable, and direction. A global `gpio_lock` serializes register updates. Wakeup callbacks are `mpc52xx_wkup_gpio_*`; simple callbacks are `mpc52xx_simple_gpio_*`. Two platform drivers match `fsl,mpc5200-gpio-wkup` and `fsl,mpc5200-gpio`.

Control flow: each probe allocates a chip, initializes dynamic-base callbacks and `ngpio`, creates an OF-derived label, maps resource 0, registers the gpiochip, then snapshots enable/direction/output registers into shadows. Direction output writes the requested value first, sets the direction bit, and enables the pin. Direction input clears the direction bit and enables the pin. Wakeup GPIO bit numbering maps line 0 to bit 7; simple GPIO maps line 0 to bit 31.

State and persistence behavior: output, enable, and direction are tracked in software shadows to avoid losing other bits during write-only style updates. Hardware register state is read once after chip registration. There is no suspend/resume handler, so shadows are not automatically restored after power loss.

Dependencies and integration points: depends on OF platform devices, PowerPC MPC52xx register layouts from `<asm/mpc52xx.h>`, and big-endian I/O helpers for the simple block. The driver registers both platform drivers at `subsys_initcall()` so board users can acquire GPIOs early.

Risks: no IRQ support is provided despite wakeup naming. Fixed bit-number reversals are easy to break in refactors. The global lock serializes both controllers, which is conservative but can hide per-chip contention. The author string has a missing `>` in metadata but no runtime impact.

Test signals: OF probe for both compatibles, 8/32-line registration, initial shadow loading, bit-reversed get/set/direction behavior, enable-bit writes on direction changes, and early initcall availability.
