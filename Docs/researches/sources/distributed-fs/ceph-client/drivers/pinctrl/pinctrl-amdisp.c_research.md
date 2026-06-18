# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amdisp.c

Purpose: Implements a small AMD ISP display/sensor-control pinctrl and GPIO driver exposing three output-only GPIO-style controls. It registers pinctrl groups from `pinctrl-amdisp.h` and a gpiochip that toggles a fixed control bit in three MMIO registers.

Important APIs and functions: Pinctrl callbacks are `amdisp_get_groups_count()`, `amdisp_get_group_name()`, and `amdisp_get_group_pins()`. GPIO callbacks are `amdisp_gpio_get_direction()`, `amdisp_gpio_direction_input()`, `amdisp_gpio_direction_output()`, `amdisp_gpio_get()`, and `amdisp_gpio_set()`. Setup paths are `amdisp_gpiochip_add()` and `amdisp_pinctrl_probe()`.

Control flow: Probe allocates `struct amdisp_pinctrl`, sets the platform device init name, maps the single MMIO resource, registers and enables pinctrl, then registers a gpiochip and a pinctrl GPIO range. GPIO get/set chooses an offset from `gpio_offset[]` indexed by GPIO number, reads or writes bit `GPIO_CONTROL_PIN`, and protects the read-modify-write with a raw spinlock.

State and persistence: Runtime state is held in `struct amdisp_pinctrl`: device, pinctrl descriptor/device, gpio range/chip, static data pointer, MMIO base, and raw spinlock. Hardware state is only the output bit in registers at offsets `0x0`, `0x4`, and `0x50`; no suspend/resume or software shadow is maintained.

Dependencies and integration points: Integrates with platform-device probing by name `amdisp-pinctrl`, gpiolib, pinctrl core, and static pin/group/function data in `pinctrl-amdisp.h`.

Risks: The driver reports output-only operation; input direction is unsupported and direction output is a no-op, so consumers must set values explicitly. There is no bounds check in `amdisp_gpio_get()`/`set()` beyond gpiolib's `ngpio` validation. `pdev->dev.init_name` is changed during probe, which is unusual and may affect device naming assumptions.

Test signals: Platform probe with one MEM resource, pinctrl group enumeration for gpio0-2, gpiochip registration with named lines, get/set of all three GPIOs, rejection of input direction, and concurrent set operations validate behavior.
