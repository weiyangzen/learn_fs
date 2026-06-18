# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/gpio.h

## Purpose

`gpio.h` defines the generic GPIO object wrapper used by Display Core for DDC, HPD, generic, sync, GSL, and other display-related pins. The active function table is disabled in this header, leaving the shared object shape and hardware-container union.

## Important APIs, Types, And Functions

`union gpio_hw_container` can point to DDC, generic, or HPD hardware pin wrappers. `struct gpio` stores the GPIO service, hardware pin, ID, enable/index value, hardware container, mode, and firmware-defined output state. A historical `gpio_funcs` block is present under `#if 0`, documenting creation and offset/ID translation operations.

## Control Flow

GPIO service code creates and manages typed hardware pin objects, then uses `struct gpio` to associate a logical GPIO ID and mode with the underlying pin. VBIOS-sourced GPIOs may carry an initial output state.

## State And Persistence Behavior

`gpio` persists while the service owns the pin. It tracks current logical mode and output state metadata, while hardware pin state persists in registers. No disk persistence exists.

## Dependencies And Integration Points

It includes `gpio_types.h` and integrates with GPIO service, DDC/I2C, HPD detection, generic panel/link controls, VBIOS GPIO translation, and AUX/DDC services.

## Risks And Edge Cases

The union requires consumers to know which hardware wrapper is active. Mode and output state can desynchronize from hardware after reset or external firmware actions. The disabled function table indicates creation/translation logic lives elsewhere; duplication can drift.

## Test Signals

Tests should cover DDC clock/data pins, HPD pins, generic GPIO mode transitions, VBIOS-defined output states, suspend/resume, and hotplug. EDID/HPD failures are the practical integration signals.
