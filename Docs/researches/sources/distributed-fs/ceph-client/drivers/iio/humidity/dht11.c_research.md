# sources/distributed-fs/ceph-client/drivers/iio/humidity/dht11.c

Purpose: Platform/IIO driver for DHT11, DHT22, and compatible single-wire GPIO humidity/temperature sensors. It bit-decodes pulse widths captured by GPIO edge interrupts and exposes processed temperature and relative humidity.

Important APIs/types/functions: `struct dht11` stores GPIO, IRQ, completion, mutex, cached values, timestamp, edge count, and edge timing buffer. `dht11_handle_irq()` records edge timestamp/value pairs. `dht11_decode()` converts 40 data bits into humidity, temperature, and checksum, supporting DHT22 and DHT11 formats. `dht11_read_raw()` controls acquisition, caching, IRQ request/free, timeout, decode attempts, and returns processed values. `dht11_probe()` obtains the GPIO, maps IRQ, initializes IIO channels, and registers the device.

Control flow: A read uses cached data if it is younger than two seconds. Otherwise it checks clock resolution, pulls the GPIO low for 18-20 ms to start a transaction, switches to input, requests both-edge IRQs, waits up to one second for enough edges, frees the IRQ, optionally dumps dynamic debug edge timings, then tries decode offsets to account for extra/missing preamble edges.

State and persistence: Cached processed temperature/humidity and timestamp persist in `struct dht11`. `num_edges == -1` marks idle/no capture. The driver dynamically requests the IRQ only during reads and serializes sysfs reads with a mutex.

Dependencies and integration points: Uses GPIOD, platform device/OF compatible `dht11`, completions, kernel timekeeping, IIO direct mode, and dynamic debug for timing traces.

Risks: Correctness depends on system timer resolution; ambiguous 23-30 us resolution is warned and >34 us fails. Long cables or scheduling latency can distort pulse widths. IRQ allocation per read adds latency and failure opportunities. Processed units differ by sensor family: DHT22 uses centi-derived conversion, DHT11 milli units.

Test signals: Probe with interrupt-capable GPIO, verify first read and two-second cache behavior, exercise timeout with disconnected sensor, validate checksum rejection, inspect dynamic debug edge timings, and test under different timer resolutions or CPU load.
