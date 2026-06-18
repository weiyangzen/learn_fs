<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio_keys.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio_keys.h

Purpose: This header defines platform data for the GPIO keys and GPIO keys polled input drivers.

Important APIs/types/functions: `struct gpio_keys_button` describes each button or switch: input code, optional legacy GPIO number, active-low polarity, descriptor label, event type, wakeup settings, debounce interval, user-disable permission, ABS value, IRQ, and optional wake IRQ. `struct gpio_keys_platform_data` supplies the button array, count, poll interval, autorepeat flag, platform enable/disable hooks, and input device name.

Control flow, state, and persistence: The platform data is consumed by the gpio-keys driver at probe time. The driver requests GPIOs/IRQs, configures debounce and wake behavior, reports input events, and may call platform enable/disable hooks across suspend/resume or open/close.

Dependencies/integration: It integrates with the input subsystem, gpiolib, IRQ wake handling, and legacy board/platform data paths.

Risks and test signals: Mixing `gpio`, `irq`, and `wakeirq` fields incorrectly can double-request or miss wake events. Active-low and wakeup action must match hardware. Tests should cover key and switch events, debounce, poll mode, suspend wake, sysfs disable for `can_disable`, enable/disable hook errors, and legacy GPIO-less IRQ buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio_keys.h -->
