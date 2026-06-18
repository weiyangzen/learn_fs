# sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp.h

Purpose: internal header for Samsung Sensor Platform sensorhub core and IIO integration. It defines protocol constants, firmware/download states, message instruction ids, board-info structure, main `struct ssp_data`, and function prototypes shared by SSP transport and IIO code.

Important APIs, types, and functions: constants define device id, reset time, default polling delay, packet/header sizes, AP-to-SSP instruction ids, AP status commands, factory-test commands, ACK/NAK values, and message option bits. `struct ssp_sensorhub_info` describes firmware names/revision and magnetic calibration table. `struct ssp_data` is the central runtime object: SPI device, board info, watchdog timer/work, refresh work, shutdown/debug/time-sync flags, status counters, available/enabled sensors, firmware revision, AP resume state, delay/batch buffers, positions, firmware-download state, locks, GPIOs, pending list, IIO device table, enable refcount, and DMA-aligned header buffer. Prototypes cover pending-list cleanup, commands, instruction send, IRQ message processing, chip id, magnetic matrix, sensor scanning info, firmware revision, and refresh task queueing.

Control flow: SPI/device code owns `struct ssp_data`, handles low-level messages and watchdog/reset, while IIO sensor code uses the shared state to enable sensors, adjust delays, and receive samples. Instructions encode add/remove/change-delay/library/AP-status operations to the MCU.

State and persistence: this header describes extensive volatile runtime state plus cached firmware revision and calibration/matrix data. Firmware files and MCU state persist outside the driver.

Dependencies and integration: includes GPIO consumer, IIO SSP sensor definitions, IIO core, SPI, and delay helpers. It supports objects built from `ssp_dev.c`, `ssp_spi.c`, and `ssp_iio.c`.

Risks and test signals: protocol constants must match MCU firmware. `sensor_enable`, refcounts, pending list, and GPIO reset sequencing are high-risk concurrency areas. Tests should cover command ACK/NAK handling, pending-list cleanup on reset, watchdog refresh, firmware revision/scanning queries, GPIO availability, DMA alignment of header buffer, and sensor enable/delay bookkeeping.
