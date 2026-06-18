# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/gpio.h

## Purpose
`wm831x/gpio.h` defines bitfields for WM831x GPIO control registers. It is a small shared header for GPIO direction, pull, interrupt, power-domain, polarity, open-drain, enable/tri-state, function selection, and pull helper values.

## Important APIs, Types, and Functions
The file is macro-only. `WM831X_GPN_DIR`, `WM831X_GPN_PULL_MASK`, `WM831X_GPN_INT_MODE`, `WM831X_GPN_PWR_DOM`, `WM831X_GPN_POL`, `WM831X_GPN_OD`, `WM831X_GPN_ENA`, `WM831X_GPN_TRI`, and `WM831X_GPN_FN_MASK` describe each GPIOx control register. Convenience values `WM831X_GPIO_PULL_NONE`, `WM831X_GPIO_PULL_DOWN`, and `WM831X_GPIO_PULL_UP` encode pull selection in the shared field.

## Control Flow
There are no functions. GPIO/pinctrl drivers compute the GPIO control register address from `core.h` register constants, compose these masks based on requested GPIO direction, pull, interrupt mode, polarity, and alternate function, then update the parent regmap.

## State and Persistence Behavior
Hardware persists each GPIO pin's direction, pull mode, interrupt mode, power domain, polarity, open-drain mode, enable/tri-state state, and function selector. Software state is maintained in the parent `struct wm831x` GPIO caches rather than here.

## Dependencies and Integration Points
This header integrates with WM831x core regmap/IRQ handling, GPIO controller code, pin function configuration, and wake/interrupt policy. It relies on includers to provide the core register addresses and regmap access.

## Risks and Test Signals
Risks include interpreting `GPN_ENA` versus `GPN_TRI` incorrectly on variants, writing pull bits without preserving function bits, polarity mistakes for IRQs, and using unsupported alternate functions. Test signals are GPIO direction/value tests, pull-up/down readback, open-drain tests, interrupt polarity/mode tests, variant tests for enable/tri-state behavior, and suspend/resume retention checks.
