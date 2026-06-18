# sources/distributed-fs/ceph-client/drivers/iio/light/lm3533-als.c

## Purpose
`lm3533-als.c` is the ALS child driver for the TI LM3533 MFD. It exposes ambient-light ADC readings, current-output mapper values for three output channels across five zones, zone threshold attributes, and threshold events through IIO.

## Important APIs, types, and functions
`struct lm3533_als` stores the parent `struct lm3533`, platform device, IRQ, interrupt-enabled flag, cached zone, and threshold mutex. `lm3533_als_get_adc()`, `_lm3533_als_get_zone()`, `lm3533_als_get_current()`, and `lm3533_als_read_raw()` implement raw/average ALS and current channel reads. Target-current helpers calculate `LM3533_REG_ALS_TARGET_BASE + 5 * channel + zone`. Threshold helpers read/write boundary registers, enforce falling <= raising with `thresh_mutex`, and expose hysteresis. `lm3533_als_isr()` clears the interrupt by reading zone info, updates the cached zone, and pushes an IIO threshold event. Probe configures platform-data input mode/resistor, optionally requests IRQ, enables ALS, and registers the IIO device.

## Control flow
The platform driver is created by the LM3533 MFD. Probe requires parent drvdata and `lm3533_als_platform_data`, builds the IIO channels, sets the parent device, initializes the zone cache, optionally disables and requests the shared IRQ, applies analog/PWM input setup, enables the ALS block, and registers IIO. Runtime raw reads use parent MFD read/update helpers. Sysfs event and extended attributes are backed by custom `device_attribute` wrappers rather than only standard event callbacks. Remove disables interrupt mode, unregisters IIO, disables ALS, and frees the IRQ.

## State and persistence
The LM3533 register map is the persistent hardware state. The driver caches only zone when interrupt mode is active and keeps threshold writes serialized. Current targets, thresholds, input mode, resistor selection, and ALS enable state are written directly to the parent device and remain until changed or reset. `LM3533_ALS_FLAG_INT_ENABLED` decides whether zone reads use the cached interrupt-updated value or poll hardware.

## Dependencies and integration points
This driver depends on the LM3533 MFD API (`lm3533_read`, `lm3533_write`, `lm3533_update`), platform data, platform-driver binding, IRQ support, IIO events, and legacy custom IIO sysfs attributes. It integrates the ALS mapper with backlight/current outputs through output current channels.

## Risks
Probe is platform-data-only and returns `-EINVAL` without it, limiting firmware-description flexibility. Interrupt enable changes update the local flag before the hardware write; error recovery clears the flag only for some cases. Threshold writes must preserve non-negative hysteresis, so tests need boundary-order coverage. IRQ handling always returns handled even if zone read failed. The custom attribute matrix is large and easy to regress during IIO ABI cleanups.

## Test signals
Build with LM3533 MFD and IIO event support. Probe tests should cover missing parent data, missing platform data, IRQ and no-IRQ paths, PWM versus analog setup, invalid resistor values, and enable failure cleanup. Runtime tests should cover raw/average ADC, output current per channel/zone, zone reads with and without interrupt mode, threshold ordering rejection, event enable toggling, and remove cleanup.
