# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-sama5d2-isc.c

## Purpose
This file is the deprecated SAMA5D2-specific platform driver for the Atmel Image Sensor Controller. It supplies supported formats, register offsets, max dimensions, DMA burst configuration, image-pipeline callbacks, gamma tables, DT endpoint parsing, runtime PM, and platform probe/remove glue around the shared ISC base.

## Important APIs and Functions
The static format tables list controller output formats and sensor input media-bus formats, including Bayer 8/10/12-bit, GREY, YUYV, RGB565, and Y10. Pipeline callbacks include `isc_sama5d2_config_csc()`, `isc_sama5d2_config_cbc()`, `isc_sama5d2_config_cc()`, `isc_sama5d2_config_ctrls()`, `isc_sama5d2_config_dpc()`, `isc_sama5d2_config_gam()`, `isc_sama5d2_config_rlp()`, and `isc_sama5d2_adapt_pipeline()`.

`isc_sama5d2_config_rlp()` handles a SAMA5D2 quirk where YCYC is not available and interleaved YUV modes use YYCC. `isc_parse_dt()` reads graph endpoints, parses V4L2 fwnode bus flags, and converts hsync/vsync/pclk polarity and BT.656 into PFE config bits. `atmel_isc_probe()` allocates and fills `struct isc_device`, initializes regmap/IRQ/pipeline/clocks/V4L2/async notifiers/runtime PM/ISPCK, sets ISPCK rate to hclock, reads version, and registers the platform driver. Remove and runtime PM functions disable clocks and cleanup shared resources.

## Control Flow and State
Probe creates device state, maps registers, requests the common interrupt handler, fills all SoC callbacks and offsets, initializes pipeline regmap fields, enables `hclock`, registers ISC-generated clocks, registers the V4L2 device, parses sensor endpoints, registers async notifiers, enables runtime PM, enables mandatory ISPCK, and reports hardware version. Async completion and streaming are delegated to the common base.

Persistent state is stored in `isc_device`, especially `gamma_table`, `gamma_max`, max dimensions, offsets, supported formats, DMA config, and `ispck_required`. Hardware state includes clocks, pipeline registers, and sensor endpoint configuration.

## Dependencies and Integration Points
It depends on platform resources, regmap MMIO, common clock, runtime PM, OF graph/fwnode parsing, V4L2 async, and the shared Atmel ISC base exports. Compatible string is `"atmel,sama5d2-isc"`.

## Risks and Test Signals
Risks include error-path ordering around `ispck` versus generic clock cleanup, endpoint parsing returning the last loop status, mandatory ISPCK assumptions, SAMA5D2 RLP quirks, and deprecated divergence from newer ISC drivers. Test signals include DT probe with parallel/BT.656 sensors, clock provider registration, ISPCK rate setting, video node creation, capture at max SAMA5D2 dimensions, RGB/YUV/Bayer format paths, runtime suspend/resume clock toggling, and clean remove after async sensor bind.
