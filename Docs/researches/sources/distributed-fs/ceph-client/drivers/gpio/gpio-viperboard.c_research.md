# sources/distributed-fs/ceph-client/drivers/gpio/gpio-viperboard.c

## Purpose
Implements the gpiolib child driver for Nano River Technologies Viperboard MFD devices. It exposes the board's two 16-line GPIO blocks, GPIO A and GPIO B, as separate sleepable `gpio_chip` instances backed by USB control messages through the parent `struct vprbrd`.

## Important APIs, Types, And Functions
- `struct vprbrd_gpioa_msg` and `struct vprbrd_gpiob_msg` define packed USB payloads for GPIO A and B commands.
- `struct vprbrd_gpio` stores both `gpio_chip` objects, cached output-direction/value bitmaps, and the parent Viperboard pointer.
- `vprbrd_gpioa_get`, `vprbrd_gpioa_set`, `vprbrd_gpioa_direction_input`, and `vprbrd_gpioa_direction_output` implement GPIO A using `VPRBRD_USB_REQUEST_GPIOA`.
- `vprbrd_gpiob_setdir`, `vprbrd_gpiob_get`, `vprbrd_gpiob_set`, `vprbrd_gpiob_direction_input`, and `vprbrd_gpiob_direction_output` implement GPIO B using `VPRBRD_USB_REQUEST_GPIOB`.
- `vprbrd_gpio_probe` allocates private state and registers both chips with dynamic GPIO bases.
- `vprbrd_gpio_init` validates the `gpioa_freq` module parameter and maps it to the firmware sampling-clock code.

## Control Flow
Probe receives the parent MFD's `struct vprbrd`, allocates `struct vprbrd_gpio`, fills GPIO A callbacks and registers it, then fills and registers GPIO B callbacks. GPIO A input reads send a GETIN command and then issue an IN transfer to retrieve the answer bit. GPIO A output setup and value changes send SETOUT messages. GPIO B uses 16-bit big-endian `val` and `mask` fields: direction changes call `vprbrd_gpiob_setdir`, reads fetch the whole input register, and writes update only the addressed masked bit. Output reads are served from cached state for both blocks.

## State And Persistence
The driver keeps runtime-only shadow state in `gpioa_out`, `gpioa_val`, `gpiob_out`, and `gpiob_val`; it does not persist values across unbind or disconnect. USB transfers share the parent `vb->buf` and are serialized by `vb->lock`. GPIO A sampling frequency is module-global, fixed during init, and used when GPIO A pins are switched to input.

## Dependencies And Integration Points
Depends on the Viperboard MFD core for `struct vprbrd`, USB device access, request constants, buffer storage, and locking. Integrates with gpiolib through two sleepable chips and with the platform bus as `viperboard-gpio`. USB endianness helpers are used for GPIO B payload fields.

## Risks And Edge Cases
Shadow state is updated before USB completion in several paths, so failed direction/value transfers can leave software cache ahead of hardware. `vprbrd_gpiob_get` returns the raw short USB return value instead of normalizing to `-EREMOTEIO` on short reads. GPIO A `set` silently ignores writes to pins not marked as outputs. All operations reuse a parent shared transfer buffer, making the parent mutex essential. Invalid `gpioa_freq` only warns and falls back to 1 kHz.

## Test Signals
Exercise both GPIO blocks independently, including input reads through USB, output readback from cached values, direction changes, invalid sampling frequency fallback, short USB transfers, and simultaneous GPIO A/B operations to confirm parent-buffer serialization.
