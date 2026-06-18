# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_gpio.h

Purpose: Declares the common GPIO pin object model for AMD display core. It defines the base `hw_gpio_pin`, the virtual function table, register-address containers, and the concrete `hw_gpio` storage used by common GPIO operations.

Important APIs and types: `struct hw_gpio_pin` is the public base with function pointers, GPIO id, enable index, current mode, opened flag, and DC context. `struct hw_gpio_pin_funcs` defines destroy/open/get/set/config/change/close operations. `struct hw_gpio` embeds the base pin, saved register fields, mux capability flag, and `gpio_registers`. `FROM_HW_GPIO_PIN` and `HW_GPIO_FROM_BASE` are container conversions. Public functions mirror the implementation in `hw_gpio.c`.

Control flow: factory or specialized constructors allocate a larger object, embed `hw_gpio`, assign the function table, and then generic callers interact only through `hw_gpio_pin_funcs`. Register members are populated by derived classes so common code can run the same sequences over different physical GPIO banks.

State and persistence: the header exposes `mode` and `opened` as mutable lifecycle state and `store` as temporary register save space. There is no locking in this API; callers must provide ordering through higher-level GPIO/resource management.

Dependencies and integration: includes `gpio_regs.h` and relies on enums/types from GPIO/DC headers included before it by translation units. It integrates with HPD, DDC, generic GPIO classes, and ASIC-specific hardware factories that bind register tables.

Risks and test signals: ABI risk centers on struct layout and function table compatibility across derived classes. Tests should verify every subclass initializes `funcs`, `regs`, context, and open state before use, and that new mux-aware hardware also extends save/restore behavior.
