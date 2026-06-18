# sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25_core.c

## Purpose
`st_uvis25_core.c` is the common IIO implementation for the ST UVIS25 UV index sensor. It validates device identity, exposes a processed UV index channel, supports one-shot direct reads, optional IRQ-triggered buffering, and sleep PM.

## Important APIs, types, and functions
- `st_uvis25_channels` defines one `IIO_UVINDEX` processed channel backed by the output register and a soft timestamp.
- `st_uvis25_check_whoami()` validates register `0x0f` against expected value `0xca`.
- `st_uvis25_set_enable()` toggles the ODR enable bit in `CTRL1` and mirrors it in `hw->enabled`.
- `st_uvis25_read_oneshot()` enables the device, waits 1.5 seconds, disables it, then reads the output register.
- `st_uvis25_read_raw()` claims direct mode and masks the IRQ line around one-shot reads to avoid stale data-ready interrupts.
- `st_uvis25_allocate_trigger()` configures interrupt polarity from `irq_get_trigger_type()`, requests the IRQ, allocates an IIO trigger, and registers it.
- `st_uvis25_buffer_preenable()`, `st_uvis25_buffer_postdisable()`, and `st_uvis25_buffer_handler_thread()` implement triggered buffered acquisition.
- `st_uvis25_probe()` is exported to bus drivers and performs common allocation, WHOAMI, boot/BDU initialization, optional buffer/trigger setup, and IIO registration.

## Control flow
Bus glue creates a regmap and calls `st_uvis25_probe()`. The core allocates an IIO device, stores it as driver data, fills `struct st_uvis25_hw`, checks WHOAMI, initializes IIO metadata, boots the sensor through `CTRL2`, waits two seconds, enables block-data-update, and, if an IRQ is present, sets up a triggered buffer and a trigger. Finally it registers the IIO device.

Direct reads disable the IRQ line when present, enable the sensor, wait for a conversion, disable the sensor, and read the UV output. IRQ-triggered operation leaves the sensor enabled while the buffer is active; the IRQ thread checks the status data-available bit and polls the trigger, and the buffer handler reads the one-byte UV output into an aligned scan structure.

## State and persistence
The `enabled` flag mirrors whether the sensor should be re-enabled after resume. Hardware configuration includes ODR enable, BDU, boot, and interrupt polarity. The driver does not persist calibration or thresholds. Suspend clears ODR unconditionally; resume restores ODR only if `hw->enabled` was true.

## Dependencies and integration points
The core uses regmap, IIO direct mode, IIO triggers, triggered buffers, IRQ trigger-type metadata, sleep PM, and the exported `IIO_UVIS25` namespace. It is transport-agnostic and relies on I2C/SPI glue for register access flags.

## Risks
- One-shot reads sleep for 1.5 seconds and block the IIO read path.
- IRQ masking around direct reads is required because the data-ready line cannot be disabled in the sensor map; removing it can leave a stuck active interrupt.
- `st_uvis25_allocate_trigger()` rejects unsupported IRQ trigger types, so firmware IRQ flags must be correct.
- The trigger stores `iio_dev` as drvdata but the IRQ request passes `hw`; both conventions must remain consistent with handlers.
- Resume only restores ODR, not a full sensor reinitialization; register retention assumptions matter.

## Test signals
- Probe tests should cover WHOAMI mismatch, boot/BDU write failures, no-IRQ direct-only mode, and unsupported IRQ polarity.
- Direct-read tests should verify `-EBUSY` while buffered, IRQ disable/enable balance, conversion delay behavior, and processed value format.
- Buffer tests should validate status-bit filtering, scan timestamp alignment, enable/disable hooks, and trigger notification completion.
- Suspend/resume tests should cover active and inactive sensor states.
