<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max3191x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max3191x.c

## Purpose
`gpio-max3191x.c` exposes Maxim MAX3191x industrial digital-input serializers as input-only GPIOs over SPI. It supports daisy-chains, optional status-byte diagnostics with CRC, fault GPIOs, and debounce control GPIOs.

## Important APIs, types, and functions
`struct max3191x_chip` stores the gpiochip, mutex, chip count, mode, optional GPIO descriptor arrays, SPI message/transfer, diagnostic bitmaps, and undervoltage policy. Core functions are `max3191x_readout_locked()`, `max3191x_chip_is_faulting()`, get/get_multiple, `max3191x_set_config()` for debounce, optional GPIO array acquisition, probe, and remove.

## Control flow
Probe reads daisy-chain count and mode properties, allocates diagnostic bitmaps and RX buffer, gets optional modesel/fault/db0/db1 GPIO arrays with either one shared descriptor or per-chip descriptors, drives modesel, validates debounce arrays, prepares the SPI transfer length, registers an input-only can-sleep gpiochip, and initializes the CRC table before driver registration. Reads serialize a full-chain SPI transfer, update diagnostics, reject faulting chips, and return requested bits.

## State and persistence behavior
Input values are sampled on each SPI read and not cached for later get. Diagnostic bitmaps persist between reads and are overwritten each readout. Debounce and mode pins are external GPIO state driven by this driver.

## Dependencies and integration points
It binds to `maxim,max31910/11/12/13/53/63`, depends on SPI, GPIO consumer descriptors for optional sideband pins, crc8, gpiolib get_multiple, and pinconf input debounce.

## Risks and edge cases
Status-byte mode rejects data on CRC, overtemperature, undervoltage, or fault conditions, but `maxim,ignore-undervoltage` suppresses undervoltage/fault handling. Optional GPIO array count mismatch is logged and ignored, possibly leaving hardware strapped incorrectly. A faulting chip makes only its eight lines return `-EIO`.

## Test signals
Test 8-bit and 16-bit modes, CRC error detection, undervoltage ignore policy, shared vs per-chip fault/debounce/modesel GPIOs, get_multiple across chip boundaries, invalid debounce values, and SPI error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max3191x.c -->
