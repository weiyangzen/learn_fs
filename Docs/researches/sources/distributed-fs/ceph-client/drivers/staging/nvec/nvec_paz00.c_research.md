# sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_paz00.c

## Purpose
OEM LED class driver for Compal PAZ00/Toshiba AC100 style devices controlled through NVEC OEM commands.

## Important APIs, Types, And Functions
`struct nvec_led` embeds `led_classdev` and stores the NVEC parent pointer. `nvec_led_brightness_set()` sends the OEM LED command, and `nvec_paz00_probe()` registers the LED class device.

## Control Flow
Probe allocates `nvec_led`, sets max brightness to 8, names the LED `paz00-led`, enables suspend/resume handling, stores the parent NVEC pointer, and registers with the LED class. Brightness changes copy `NVEC_LED_REQ`, place the requested value in byte 4, send it asynchronously, and update cached brightness.

## State And Persistence
Runtime state is only the allocated LED object and cached brightness. No persistent LED state is saved across driver reloads or power cycles.

## Dependencies And Integration Points
Depends on the NVEC MFD child device, NVEC async command API, platform bus, and LED class framework.

## Risks
Brightness values are passed directly to firmware without validation beyond LED core max brightness. Async command failure is ignored by the LED callback. Device coverage is OEM-specific.

## Test Signals
LED class registration, sysfs brightness writes from 0 through 8, suspend/resume restoration by LED core, command bytes observed on NVEC, and removal cleanup through devm.
