# sources/distributed-fs/ceph-client/drivers/iio/adc/ad_sigma_delta.c

## Purpose
`ad_sigma_delta.c` is a shared support library for Analog Devices sigma-delta ADC drivers. It provides exported register access, reset, calibration, single-conversion, data-ready trigger, triggered-buffer, scan-mask validation, and optional SPI offload/DMA setup. Leaf drivers provide `struct ad_sigma_delta_info` callbacks and mode/channel operations while this file centralizes SPI sequencing and IIO integration.

## Important APIs, Types, and Functions
Exported APIs include `ad_sd_set_comm()`, `ad_sd_write_reg()`, `ad_sd_read_reg()`, `ad_sd_reset()`, `ad_sd_calibrate()`, `ad_sd_calibrate_all()`, `ad_sigma_delta_single_conversion()`, `ad_sd_validate_trigger()`, `devm_ad_sd_setup_buffer_and_trigger()`, and `ad_sd_init()`. Important internal helpers are `ad_sigma_delta_clear_pending_event()`, `ad_sd_disable_irq()`, `ad_sd_enable_irq()`, `ad_sd_buffer_postenable()`, `ad_sd_buffer_predisable()`, `ad_sd_trigger_handler()`, and `ad_sd_data_rdy_trig_poll()`.

The code relies on `struct ad_sigma_delta`, `struct ad_sigma_delta_info`, and `struct ad_sd_calib_data` from the public IIO ADC header. It uses DMA-aligned TX/RX buffers owned by the sigma-delta state, completion objects for conversion completion, a spinlock-protected IRQ-disable flag, and optional SPI offload handles.

## Control Flow
`ad_sd_init()` stores SPI/info pointers, derives slot count, validates that multi-slot devices provide `update_scan_mode()` and `disable_all()`, resolves the RDY IRQ or GPIO, optionally acquires SPI offload, and binds state to the IIO device. Register reads and writes build SPI messages with optional communications-register channel bits and optional register addressing.

Single conversion claims direct mode, selects the channel, locks the SPI bus, keeps CS asserted, clears stale pending events, starts single mode, enables RDY IRQ, waits for completion, reads the data register, disables IRQ, idles the converter, disables the channel, unlocks the bus, extracts sample bits, and runs postprocess. Buffered mode similarly locks the bus, builds an optimized sample message, configures slots, optionally appends status bytes for multi-channel sequencing, clears pending data, starts continuous mode, and either enables SPI-offload data-ready triggering or the software RDY IRQ. The trigger handler reads one conversion, validates appended channel status for multi-slot devices, assembles complete scans, pushes timestamps, and reenables RDY IRQ.

## State, Persistence, and Dependencies
State is runtime-only: bus lock flags, CS assertion, active slots, current slot, status-appended state, optimized SPI message, sample buffer, completion, IRQ disable flag, trigger, and optional offload trigger/DMA. Dependencies include SPI, SPI offload, IIO triggered buffers, DMAengine IIO buffers, GPIO RDY, IRQ handling, completions, spinlocks, and device-managed resource APIs.

## Integration Points
Leaf drivers call `ad_sd_init()` and `devm_ad_sd_setup_buffer_and_trigger()` and reuse `ad_sigma_delta_single_conversion()` for direct reads. The helper exports namespace `IIO_AD_SIGMA_DELTA` and imports `IIO_DMAENGINE_BUFFER`.

## Risks and Test Signals
Risks include stale RDY events before mode changes, shared RDY/MISO lines causing false interrupts, missing multi-slot callbacks, deadlocks around bus locking, status-channel desynchronization, and offload/non-offload divergence. Test signals include single conversion timeouts, calibration completion, multi-channel scans dropping desynced samples, scan-mask validation against slot count, RDY GPIO filtering, offload DMA setup, and correct cleanup on buffer disable.
