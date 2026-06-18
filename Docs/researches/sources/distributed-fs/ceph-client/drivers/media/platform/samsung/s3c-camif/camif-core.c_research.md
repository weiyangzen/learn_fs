# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-core.c

Purpose: platform-driver and shared core for the S3C CAMIF driver. It defines supported pixel formats, scaler factor calculation, sensor/media registration, clocks, IRQ registration, probe/remove, runtime PM, and per-SoC variant data.

Important APIs and functions: `s3c_camif_find_format()` filters `camif_formats[]` by fourcc/index and per-path SoC flags. `s3c_camif_get_scaler_config()` computes prescaler/main-scaler ratios and scale-up bits from frontend crop and output frame. `s3c_camif_probe()` allocates `camif_dev`, validates platform data, maps registers, requests both path IRQs, initializes subdev/video/media entities, registers the sensor, and enables PM. Runtime PM is implemented by `s3c_camif_runtime_resume()` and `s3c_camif_runtime_suspend()`.

Control flow: probe copies platform data, selects `s3c244x_camif_variant` or `s3c6410_camif_variant` from the platform id, maps MMIO, registers IRQs via `s3c_camif_irq_handler()`, acquires platform GPIOs, creates the CAMIF subdev, prepares clocks, sets the external sensor clock rate, initializes default formats, resumes the hardware, registers the media device and sensor, creates links, registers both video nodes, then drops runtime PM. Remove unwinds media/video/sensor registrations, disables runtime PM, releases clocks, unregisters the subdev, and returns GPIOs.

State and persistence: `camif_dev` is device-private in platform drvdata. Format catalog and SoC variant tables are static read-only state. `stream_count` and path state are owned by capture/register code but initialized here. Runtime PM state is in kernel PM core; no durable persistence exists.

Dependencies and integration: depends on platform data for GPIO hooks and sensor I2C board info, `clk_get()` names `camif` and `camera`, `platform_get_irq()` for two path IRQs, V4L2/media device registration, and helper entry points implemented in `camif-capture.c`.

Risks: the driver is platform-data based rather than DT-first, so missing or stale board data fails probe. Error unwind order is subtle because media device cleanup, V4L2 unregister, sensor unregister, clock release, and GPIO release interact. Scaler math rejects ratios at or above 64:1 and relies on crop/output values being sanitized before streaming.

Test signals: probe/remove on both platform IDs, clock and GPIO error injection, sensor absent/deferred probe, media graph inspection, scaler ratio boundary tests, runtime PM resume/suspend balancing, and capture tests that verify variant-specific output width/height limits.
