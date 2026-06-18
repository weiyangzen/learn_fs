# sources/distributed-fs/ceph-client/drivers/gpio/gpio-vx855.c

## Purpose
Exposes the VIA VX855 southbridge GPIO, GPI, and GPO pins through gpiolib using legacy x86 I/O port registers supplied by the VX855 MFD platform device.

## Important APIs, Types, And Functions
- `struct vx855_gpio` stores the `gpio_chip`, spinlock, and input/output I/O port addresses.
- Bit mapping helpers `gpi_i_bit`, `gpo_o_bit`, `gpio_i_bit`, and `gpio_o_bit` translate logical line offsets to sparse southbridge register bits.
- `vx855gpio_direction_input`, `vx855gpio_direction_output`, `vx855gpio_get`, and `vx855gpio_set` implement line operations with special handling for GPI-only, GPO-only, and open-drain GPIO ranges.
- `vx855gpio_set_config` reports push-pull support for GPOs and open-drain support for bidirectional GPIOs.
- `vx855gpio_probe` receives two I/O resources, optionally reserves them, initializes chip metadata and line names, and registers the chip.

## Control Flow
Logical GPIO offsets 0-13 are input-only GPI pins, 14-26 are output-only GPO pins, and 27-41 are open-drain bidirectional GPIO pins. Reads choose either the input register or output register depending on line class. Setting a true GPI fails, setting a GPO or GPIO updates the output port under spinlock, and input direction for open-drain GPIOs writes a high output state.

## State And Persistence
The driver has no shadow state; hardware I/O port registers are the source of truth. Resource reservations are devm-managed and may be skipped if ACPI already owns the region.

## Dependencies And Integration Points
Depends on platform resources from the VX855 MFD driver, legacy `inl`/`outl` I/O port access, gpiolib, pinconf drive-mode constants, and static line names for the 42 logical pins.

## Risks And Edge Cases
The chip uses sparse and nonuniform bit mappings, making off-by-one errors likely. The probe tolerates busy I/O regions due to ACPI overlap, so simultaneous firmware/driver access is possible. `gpio_chip.base` is fixed at 0, which can collide on systems with other static GPIO bases. Input/output restrictions differ by logical range and must remain consistent across direction, set, and config callbacks.

## Test Signals
Check all range boundaries: GPI13/GPO0, GPO12/GPIO0, GPIO14, GPI output rejection, GPO input rejection, open-drain input-as-high behavior, set_config return codes, and operation when request_region fails due to ACPI reservation.
