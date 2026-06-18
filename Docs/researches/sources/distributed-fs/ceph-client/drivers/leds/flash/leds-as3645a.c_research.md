# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-as3645a.c

## Purpose
This I2C driver supports AS3645A, LM3555, and compatible flash controllers. It registers a flash/assist LED and an indicator LED, programs current, timeout, control, and boost registers, and exposes V4L2 flash and indicator subdevices.

## Important APIs, Types, and Functions
`struct as3645a` stores the I2C client, mutex, flash and indicator class devices, V4L2 handles, firmware nodes, configuration, cached mode, current, timeout, and strobe source. Low-level I/O is `as3645a_read()` and `as3645a_write()`. Hardware setup and detection are `as3645a_detect()` and `as3645a_setup()`. LED operations include `as3645a_set_indicator_brightness()`, `as3645a_set_assist_brightness()`, `as3645a_set_flash_brightness()`, `as3645a_set_flash_timeout()`, `as3645a_set_strobe()`, and `as3645a_get_fault()`.

## Control Flow
Probe requires firmware nodes, parses child nodes by `reg` values 0 for flash and 1 for indicator, detects the chip from design/version registers, unlocks and disables boost current, initializes the device, registers LED class devices, then registers V4L2 flash and indicator devices. Brightness paths convert user-visible brightness or microamp values to register codes, update current/timer registers, and call `as3645a_set_control()` to select indicator, assist, flash, or external torch mode.

## State and Persistence
Runtime state is protected by `flash->mutex`. Cached fields mirror hardware settings for timeout, flash current, assist current, indicator current, mode, and strobe source. Firmware node references are manually retained and released in remove/error paths. There is no persistence across device removal.

## Dependencies and Integration Points
The driver depends on I2C SMBus byte access, LED flash class, plain LED class for the indicator, firmware child properties (`flash-timeout-us`, `flash-max-microamp`, `led-max-microamp`, `voltage-reference`, `ams,input-max-microamp`), and V4L2 flash helpers. It binds `ams,as3645a` and I2C ID `as3645a`.

## Risks and Edge Cases
`AS_PEAK_mA_TO_REG()` subtracts 1250 from a clamped value, so missing or very small `ams,input-max-microamp` can underflow in unsigned arithmetic before register programming. The setup path returns `rval & ~AS_FAULT_INFO_LED_AMOUNT ? -EIO : 0`; fault interpretation should be checked when adding fault bits. Probe must release both retained child nodes on every error. The driver requires both flash and indicator child nodes; systems without indicator support are rejected.

## Test Signals
Test chip detection against real AS3645A/LM3555-compatible hardware, current and timeout sysfs attributes, indicator brightness, assist/torch mode, flash strobe, and fault mapping for timeout, thermal, short, over-voltage, and LED amount faults. V4L2 tests should confirm both flash and indicator subdevices appear and release cleanly.
