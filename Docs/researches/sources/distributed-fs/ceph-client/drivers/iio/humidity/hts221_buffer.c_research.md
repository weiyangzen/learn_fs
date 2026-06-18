# sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_buffer.c

Purpose: Trigger and buffered capture support for the HTS221 driver. It configures the data-ready interrupt, allocates an IIO trigger, and reads humidity/temperature samples into the shared scan buffer.

Important APIs/types/functions: `hts221_trig_set_state()` toggles DRDY enable in CTRL3-like register `0x22`. `hts221_trigger_handler_thread()` checks status register and polls the IIO trigger when humidity data-ready is set. `hts221_allocate_trigger()` configures interrupt polarity/open-drain, requests threaded IRQ, allocates/registers trigger, and attaches it to the IIO device. Buffer hooks `hts221_buffer_preenable()` and `hts221_buffer_postdisable()` call `hts221_set_enable()`. `hts221_buffer_handler_thread()` bulk reads humidity and temperature registers and pushes timestamped data. `hts221_allocate_buffers()` installs the triggered buffer.

Control flow: During probe, core calls allocation only when IRQ is present. IRQ fires into a thread, status is read, and valid humidity-ready events call `iio_trigger_poll_nested()`. The triggered buffer poll function then reads both channel registers and notifies trigger completion.

State and persistence: Uses `hw->trig`, `hw->irq`, `hw->scan`, and `hw->enabled` via core helper. Hardware DRDY configuration persists in registers. Buffer enable powers/enables the sensor; postdisable disables it.

Dependencies and integration points: Depends on regmap, IIO trigger/triggered buffer, interrupt framework, optional platform data `st_sensors_platform_data`, device property `drive-open-drain`, and symbols from `hts221_core.c`.

Risks: `iio_dev->trig = iio_trigger_get(hw->trig)` is assigned even if trigger registration returns an error; error path relies on devm cleanup. IRQ type defaults to rising when unspecified/unsupported. The interrupt status check assumes humidity-ready implies both humidity and temperature samples are ready.

Test signals: Test IRQ polarity/open-drain properties, trigger registration, buffer enable/disable sensor power state, data-ready interrupt filtering, scan data order, and no-IRQ probe path in core.
