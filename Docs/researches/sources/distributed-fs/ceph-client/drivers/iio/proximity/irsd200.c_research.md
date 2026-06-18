<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/irsd200.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/irsd200.c

Purpose: I2C regmap IIO driver for the Murata IRS-D200 PIR proximity sensor. It exposes signed raw PIR data, sample frequency, low/high-pass filter controls, threshold events with running period/count controls, and an IRQ-backed triggered buffer for data-ready sampling.

Important APIs, types, and functions: `struct irsd200_data` stores the regmap, register fields, and device pointer. `irsd200_setup()` disables interrupts, sets active mode, clears count/status, and prepares the device. `irsd200_read_data()`, data-rate/filter/timer/count helpers, threshold helpers, `irsd200_irq_thread()`, `irsd200_trigger_handler()`, and `irsd200_set_trigger_state()` implement the IIO ABI.

Control flow: probe initializes regmap and six regmap fields, enables `vdd`, calls setup, requires a client IRQ, sets up a triggered buffer, requests a rising threaded IRQ, registers an IIO trigger, and then registers the device. Raw reads bulk-read two data bytes. Buffer enable via trigger ops toggles the data interrupt bit; IRQ thread polls the trigger for data interrupts and pushes threshold events for OR count threshold status, deriving rising/falling/either from upper/lower count fields before clearing status.

State and persistence: most state lives in device registers; the driver does not keep a mutex or software cache beyond regfield handles. Thresholds are quantized by 128, falling thresholds are represented as negative values, data rate writes sleep for 3 seconds to honor settling guidance, and count/timer constraints are enforced before writing `IRS_REG_NR_COUNT`.

Dependencies and integration points: depends on I2C regmap, regmap fields, `vdd` regulator, a mandatory IRQ, IIO events, IIO triggers, and triggered buffers. OF compatible is `murata,irsd200`.

Risks and test signals: test required IRQ failure, data interrupt buffering, threshold OR and AND-like event behavior, status clearing, data-rate settling, timer quantization, and count write rejection when timer is zero. A code risk is `irsd200_write_hp_filter()` comparing the truncated fractional digit to `irsd200_hp_filter_freq[idx][0]`, which works for 0.3/0.5 but is easy to break if the table changes. Lack of explicit locking also makes concurrent sysfs writes worth stressing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/irsd200.c -->
