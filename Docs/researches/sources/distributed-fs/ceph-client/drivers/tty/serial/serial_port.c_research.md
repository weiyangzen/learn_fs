# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_port.c

## Purpose
Serial-base port device driver. It provides runtime PM behavior for synthetic serial port devices, routes public `uart_add_one_port()`/`uart_remove_one_port()` into the serial-base/controller/core stack, and reads common UART firmware properties.

## Important APIs, Types, And Functions
`serial_port_runtime_resume()` restarts pending TX after runtime resume when TX is enabled. `serial_port_runtime_suspend()` refuses suspend with `-EBUSY` while TX data remains. `serial_base_port_startup()` and shutdown toggle the port device `tx_enabled` flag. Public exports are `uart_add_one_port()`, `uart_remove_one_port()`, `uart_read_port_properties()`, and `uart_read_and_validate_port_properties()`. `__uart_read_properties()` handles common firmware parsing and validation.

## Control Flow
The serial-base bus init registers an internal driver named `port`. Probe enables runtime PM autosuspend with a 500 ms delay. Low-level drivers calling `uart_add_one_port()` are forwarded through controller registration to serial core. Firmware property reading can apply defaults or validate an already-initialized port: clock frequency, reg shift, IO width, reg offset, FIFO size, no-loopback-test, OF alias, IRQ, and shared-IRQ flag.

## State And Persistence
Per-port state is the synthetic `serial_port_device` and its `tx_enabled` bit. Firmware-derived values are written into `uart_port` fields. No persistent data is stored.

## Dependencies And Integration Points
Depends on device core, runtime PM, platform/PNP/fwnode IRQ APIs, OF aliases, serial core, and kfifo helpers. It is the public wrapper layer that low-level UART drivers use for add/remove.

## Risks
Runtime PM only models pending TX, so RX wake behavior remains driver-specific. Property validation must avoid mapbase/mapsize underflow when applying `reg-offset`. IRQ defaults differ between defaulting and validation modes. Resume calls low-level `start_tx()` under the port lock, so driver callbacks must obey serial-core locking expectations.

## Test Signals
Read properties from platform, PNP, and generic fwnode devices; validate bad `reg-io-width` and out-of-range `reg-offset`; verify autosuspend blocks on pending TX; confirm `uart_add_one_port()` creates serial-base and tty devices; and test remove while TX is disabled.
