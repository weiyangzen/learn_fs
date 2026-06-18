# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_mctrl_gpio.h

## Purpose
Public helper header for serial drivers that use GPIOs as modem-control lines. It defines GPIO line indexes, the opaque `mctrl_gpios` handle, function prototypes, and no-op fallbacks when GPIOLIB is not built.

## Important APIs, Types, And Functions
`enum mctrl_gpio_idx` maps CTS, DSR, DCD, RNG/RI, RTS, and DTR. The API surface provides setters/getters, GPIO descriptor lookup, automatic and no-auto initialization, modem-status IRQ enable/disable, and IRQ wake enable/disable.

## Control Flow
Serial drivers include this header, call `mctrl_gpio_init()` or `mctrl_gpio_init_noauto()`, then delegate modem callbacks to the helper functions. With GPIOLIB disabled, inline stubs preserve buildability and return unchanged modem-control state or NULL handles.

## State And Persistence
The header owns no storage. It defines an opaque runtime handle whose real layout is private to `serial_mctrl_gpio.c`.

## Dependencies And Integration Points
Includes error, device, and GPIO consumer headers. Integrates with `struct uart_port` without exposing serial-core internals.

## Risks
Callers must tolerate NULL helper handles because absent GPIOs and disabled GPIOLIB are valid. The alias `UART_GPIO_RI = UART_GPIO_RNG` means code should treat ring naming consistently.

## Test Signals
Compile serial drivers with GPIOLIB on and off, validate NULL-safe calls, and confirm each GPIO property name maps to the expected modem-control bit through the implementation.
