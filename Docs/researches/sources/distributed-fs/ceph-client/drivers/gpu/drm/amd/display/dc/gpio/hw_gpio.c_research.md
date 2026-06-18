# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_gpio.c

Purpose: Implements the common hardware GPIO pin behavior used by AMD display core GPIO-derived pin classes. It owns open/close state preservation, mode programming, and simple value reads/writes through register helper macros bound to the pin's `gpio_registers`.

Important APIs and functions: `dal_hw_gpio_open` snapshots `MASK`, `A`, and `EN`, programs the requested mode, and sets `hw_gpio_pin.opened`. `dal_hw_gpio_close` restores those saved registers and resets mode/open state. `dal_hw_gpio_get_value` reads `Y` for input/output/hardware/fast-output modes. `dal_hw_gpio_set_value` writes `A` for normal output and toggles `EN` inverted for fast output. `dal_hw_gpio_config_mode` is the central mode switch for input, output, fast output, hardware, and interrupt. `dal_hw_gpio_construct` and `dal_hw_gpio_destruct` initialize and assert lifecycle invariants.

Control flow: callers receive a `hw_gpio_pin` interface from a factory or subclass, call `open(mode)`, then issue value/config/mode operations through function pointers, and finally `close()`. The implementation converts the base pointer with `FROM_HW_GPIO_PIN`, then performs direct register updates. The interrupt mode is deliberately only a GPIO mask setup here; HPD subclasses provide interrupt-specific semantics.

State and persistence: state is volatile hardware register state, with a small in-memory `store` shadow used only between open and close. No persistent storage is used. A risk is that `GPIO_MUX_CONTROL` is not saved/restored despite a TODO, so future mux users could leak mux state across open/close.

Dependencies and integration: depends on `dm_services.h`, `gpio_types.h`, `gpio_regs.h`, and `reg_helper.h`. It is integrated by derived GPIO types such as HPD/DDC/generic pins and by hardware factory code that fills `regs`.

Risks and test signals: test via register trace or mocked `REG_*` helpers for each mode, including restoration on close and inverted fast-output `EN` behavior. Hardware tests should cover DDC fast output rise-time behavior and confirm interrupt-mode callers do not expect value semantics from this base file.
