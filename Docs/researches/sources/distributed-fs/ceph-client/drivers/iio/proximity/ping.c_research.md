<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/ping.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/ping.c

Purpose: platform IIO driver for Parallax PING and LaserPING single-GPIO ultrasonic/laser distance sensors. It exposes one direct-mode `IIO_DISTANCE` channel with raw millimeter distance and scale.

Important APIs, types, and functions: `struct ping_cfg` describes trigger pulse length, LaserPING error-code support, and timeout. `struct ping_data` stores the shared GPIO, mutex, timestamps, completions, IRQ number, and matched config. `ping_read()` drives the trigger pulse, switches the GPIO to input, dynamically requests both-edge IRQs, waits for rising/falling echo edges, computes pulse duration, filters timeout/error-code windows, and converts to millimeters. `ping_read_raw()` exposes raw and scale.

Control flow: probe selects match data, gets the `ping` GPIO as output-low, rejects sleepable GPIOs, and registers a direct-mode IIO device. Each read holds the mutex, toggles the output pulse, converts the GPIO to input, requests an IRQ for the measurement, waits for completions, frees the IRQ, restores output-low, and returns computed distance.

State and persistence: measurement state is transient timestamps and completions. There is no hardware register persistence. The mutex is essential because GPIO direction and the one-shot IRQ are shared mutable state.

Dependencies and integration points: depends on platform/OF matching (`parallax,ping`, `parallax,laserping`), non-sleeping GPIO descriptors, dynamic IRQ allocation, completions, and IIO direct sysfs.

Risks and test signals: test GPIO direction transitions, IRQ request/free on all error paths, rising/falling timeout behavior, LaserPING error pulse windows, out-of-range filtering, and repeated concurrent reads. Risks are per-read IRQ setup overhead, no temperature compensation, use of `gpiod_get_value()` in IRQ context, and rejecting sleepable GPIO controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/ping.c -->
