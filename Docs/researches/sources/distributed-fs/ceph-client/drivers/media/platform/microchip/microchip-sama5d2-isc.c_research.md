# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-sama5d2-isc.c

## Purpose
`microchip-sama5d2-isc.c` is the SAMA5D2 product driver for the Microchip Image Sensor Controller. It supplies SAMA5D2 format tables, register offsets, clock policy, hardware callbacks, DT parsing, probe/remove, and runtime PM around the shared ISC base.

## Important APIs, Types, and Functions
The file defines SAMA5D2 output and input format tables, gamma tables, and callbacks `isc_sama5d2_config_csc()`, `isc_sama5d2_config_cbc()`, `isc_sama5d2_config_cc()`, `isc_sama5d2_config_ctrls()`, `isc_sama5d2_config_dpc()`, `isc_sama5d2_config_gam()`, `isc_sama5d2_config_rlp()`, and `isc_sama5d2_adapt_pipeline()`. Platform lifecycle is `microchip_isc_probe()`, `microchip_isc_remove()`, `isc_runtime_suspend()`, and `isc_runtime_resume()`.

## Control Flow
Probe allocates `isc_device`, maps MMIO through regmap, requests the IRQ using the common interrupt handler, assigns SAMA5D2 callbacks and format tables, sets 2592x1944 limits, configures 8-beat DMA bursts, marks ISPCK as mandatory, initializes pipeline fields, enables `hclock`, registers generated ISC clocks, registers V4L2, parses endpoints, registers async notifiers for remote sensors, reads hardware version, initializes media-controller/scaler support, enables runtime PM, enables and rates ISPCK to at least `hclock`, and reports the version. Removal reverses media, notifier, V4L2, clock, and PM setup.

## State and Persistence
State lives in the shared `isc_device`. SAMA5D2-specific persistent-in-driver state is static format/gamma tables and callback assignments. Hardware register state is rebuilt on stream setup and runtime resume.

## Dependencies and Integration Points
The driver binds `atmel,sama5d2-isc`, depends on common ISC exports, AT91 clock/reset resources, V4L2 fwnode endpoint parsing, and media-controller async graph binding. It integrates directly with sensors using parallel or BT.656 bus flags.

## Risks and Edge Cases
SAMA5D2 lacks DPC and special gamma configuration, so pipeline bits are masked by `ISC_SAMA5D2_PIPELINE`. Its RLP block treats planar and interleaved YUV through the YYCC mode, requiring the callback to rewrite YCYC. ISPCK setup is mandatory and error unwinding must avoid disabling an unprepared clock path incorrectly.

## Test Signals
Test probe with valid endpoints and clocks, RAW8/10/12 and YUV/GREY/RGB formats, BT.656 and polarity flags, ISPCK rate setup, runtime suspend/resume, media graph registration, and capture up to 2592x1944.
