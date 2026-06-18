# sources/distributed-fs/ceph-client/drivers/hwmon/lochnagar-hwmon.c

## Purpose
`lochnagar-hwmon.c` is a platform hwmon driver for Cirrus Logic Lochnagar2 board monitoring. It exposes one board temperature input plus voltage, current, and average power readings for eight named supply channels, with a writable power averaging interval per channel.

## APIs, Flow, State, And Risks
`struct lochnagar_hwmon` stores the parent MFD regmap and per-channel power sample counts. `float_to_long` converts hardware floating-point measurements into integer units. `do_measurement` programs IMON control registers, waits for configure and measurement completion, and clears control state. `request_data` fetches the 32-bit result. `read_sensor` and `read_power` implement the measurement paths; hwmon callbacks provide reads, labels, visibility, and average interval writes.

Probe gets the parent regmap, initializes all power sample counts to 96, and registers the hwmon device. Reads perform live measurements; power reads multiply voltage and current, with SYSVDD using a fixed 5 V multiplier and hidden voltage input. Average interval writes clamp milliseconds, convert to sample count, and store it in driver memory.

The only software state is `power_nsamples[]`; hardware measurement registers are transient and cleared. Dependencies are the Lochnagar MFD, Lochnagar2 register definitions, regmap, hwmon, OF platform binding, polling helpers, sleep timing, and 64-bit math. Risks include no explicit mutex around shared IMON sequences, expensive polling/sleep under frequent reads, IEEE conversion assumptions, and SYSVDD special-casing by channel-name order. Test parent regmap probe, visibility/labels, interval clamping, mocked measurement success/timeouts, float conversion, and concurrent reads.
