<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm_gpio.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm_gpio.c

Purpose: platform driver wrapper that binds CPM GPIO OF nodes to the appropriate CPM1 or CPM2 gpiochip registration helper.

Important APIs/types/functions: `cpm_gpio_probe()`, OF match table `cpm_gpio_match`, `cpm_gpio_driver`, and `cpm_gpio_init()`.

Control flow: arch init registers the platform driver. Probe retrieves the function pointer stored in match data and invokes it for the device. Match entries select CPM1 16/32-bit helpers for 8xx banks and `cpm2_gpiochip_add32()` for CPM2/port-E style banks.

State and persistence: the wrapper has no runtime state beyond the registered platform driver. Per-bank state is allocated by the selected helper.

Dependencies and integration points: integrates OF platform matching, CPM GPIO helpers from `asm/cpm.h`/`asm/cpm1.h`, and gpiolib registration.

Risks: match data must remain accurate for each bank layout. A missing helper under config guards results in the compatible not being available.

Test signals: platform driver binding to CPM GPIO nodes, gpiochip registration for each bank, and working GPIO line operations through sysfs/gpiod consumers validate this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm_gpio.c -->
