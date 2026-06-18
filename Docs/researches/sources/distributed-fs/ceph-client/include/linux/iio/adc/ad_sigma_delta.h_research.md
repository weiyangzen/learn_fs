# `sources/distributed-fs/ceph-client/include/linux/iio/adc/ad_sigma_delta.h`

Purpose: common support interface for Analog Devices sigma-delta ADC drivers, covering register communication, channel/mode selection, calibration, triggered buffers, SPI offload, and sample post-processing.

Important APIs/types/functions: `enum ad_sigma_delta_mode`, `struct ad_sd_calib_data`, `struct ad_sigma_delta_info` callback table, `struct ad_sigma_delta` core state, inline callback wrappers, `ad_sd_set_comm`, register read/write, reset, single conversion, calibration helpers, init, devm buffer/trigger setup, and trigger validation.

Control flow and state: persistent `ad_sigma_delta` state stores SPI device, trigger, completion, IRQ lock/disabled flag, bus/chip-select state, communication byte, active slots/current slot, ready GPIO/IRQ, status-append state, slot mapping, SPI messages/transfers, DMA-aligned buffers, and optional SPI offload trigger. Inline wrappers call device-specific callbacks when present and otherwise no-op.

Dependencies/integration: depends on IIO core, SPI, triggers, completions, GPIO, and optional SPI offload. Individual ADC drivers fill `ad_sigma_delta_info` and call init/setup helpers.

Risks: IRQ enable/disable state is lock-protected and race-sensitive; DMA buffer alignment is required; optional callbacks must preserve core state such as `status_appended`; SPI offload support requires channel scan-type compatibility; calibration and mode switching must not run concurrently with buffered capture.

Test signals: register read/write/reset, single conversions, triggered buffer capture, IRQ completion timeouts, calibration sequences, callback absent/present paths, SPI offload path, and DMA alignment checks.
