# sources/distributed-fs/ceph-client/drivers/input/keyboard/gpio_keys.c

## Purpose

`gpio_keys.c` is the interrupt-driven GPIO/IRQ button and switch driver. It supports GPIO-backed stateful keys, IRQ-only momentary keys, debounce, wakeup handling, optional separate wake IRQs, platform-data and firmware-node configuration, and sysfs disabling of eligible keys/switches.

## Important APIs, Types, and Functions

- `struct gpio_button_data` stores per-button platform data, input, GPIO, code pointer, debounce/release timers, work item, IRQ/wakeirq, wake trigger, lock, disabled/key/suspend flags, and debounce mode.
- `struct gpio_keys_drvdata` stores platform data, input device, disable mutex, keymap, and flexible button array.
- Sysfs helpers expose `keys`, `switches`, `disabled_keys`, and `disabled_switches`.
- `gpio_keys_setup_key()` configures GPIO/IRQ resources, debounce, wake triggers, input capabilities, cleanup actions, and interrupt handlers per button.
- `gpio_keys_gpio_isr()` handles GPIO-backed edge interrupts; `gpio_keys_irq_isr()` handles IRQ-only keys with synthetic release timers.
- PM helpers enable/disable wakeup and call platform enable/disable hooks.

## Control Flow

Probe obtains platform data or builds it from child firmware nodes, allocates state/input/keymap, loops over buttons to configure GPIOs or IRQ-only inputs, requests main and optional wake IRQs, registers input, and initializes device wakeup. Input open calls optional platform enable and reports current GPIO states; close calls optional disable. GPIO IRQs schedule debounce work/hrtimer, which reads the GPIO and emits current state. IRQ-only handlers emit press and either immediate or delayed release. Sysfs writes validate requested disabled codes and mask/unmask non-shared IRQs. Suspend either enables wake IRQ behavior or closes the input device; resume restores IRQs and reports current state.

## State and Persistence Behavior

Per-button state persists disabled status, key pressed state for IRQ-only buttons, debounce/release timers, software debounce mode, wake trigger type, and suspended flag. Driver-level keymap and platform data persist for the device lifetime. No nonvolatile state is used, but sysfs disabled masks persist until changed or driver removal.

## Dependencies and Integration Points

It integrates with platform bus, GPIO descriptor and legacy GPIO APIs, IRQ core, hrtimers/workqueues, input core, PM wakeup, OF/fwnode child properties, `linux/gpio_keys.h`, and `dt-bindings/input/gpio-keys.h`. It registers late via `late_initcall`.

## Risks and Edge Cases

Shared IRQ buttons cannot be disabled through sysfs. GPIO-backed wake trigger reconfiguration must be restored correctly on resume. IRQ-only buttons only support `EV_KEY` and synthesize releases, so debounce interval semantics differ from GPIO keys. Hrtimer debounce is used only for non-sleeping GPIOs. Platform enable/disable hooks and wake IRQ swapping can race with input open/close or suspend if ordering changes.

## Test Signals

Test GPIO and IRQ-only buttons, EV_KEY/EV_SW/EV_ABS types, debounce via hardware and software paths, sysfs disable/enable validation, shared IRQ behavior, wake-source and separate wakeirq suspend/resume, asserted/deasserted wake trigger actions, platform-data and fwnode parsing, initial state reporting, shutdown path, and remove with pending timers/work.
