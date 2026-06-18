# sources/distributed-fs/ceph-client/drivers/iio/adc/nxp-sar-adc.c

Purpose: this platform driver supports the NXP S32G2 SAR ADC. It provides eight 12-bit voltage channels, direct one-shot reads, configurable sample frequency, triggered buffers, software/cyclic-DMA buffering, calibration, and suspend/resume context restoration.

Important APIs, types, and functions: `struct nxp_sar_adc` stores MMIO and physical addresses, clock, completion, DMA channel and circular buffer, buffered channel list, VREF, and saved PM context. `nxp_sar_adc_set_enabled()` controls power-down state. `nxp_sar_adc_calibration()` powers the block, starts calibration, waits for completion/failure, and powers down. `nxp_sar_adc_read_channel()` enables one channel, unmasks IRQ, starts normal conversion, waits for completion, then disables everything. `nxp_sar_adc_dma_cb()` drains a cyclic DMA buffer into IIO buffers. Buffer pre/post enable functions select IRQ-triggered or software DMA behavior.

Control flow: probe maps registers, requests IRQ, enables the clock, initializes defaults instead of trusting reset values, calibrates, allocates coherent DMA memory, installs triggered-buffer callbacks, and registers IIO. Direct reads claim direct mode. Buffered reads enable active scan-mask channels, power the ADC, then either enable interrupts for trigger-driven reads or request/configure/start cyclic DMA for software buffers.

State and persistence: hardware state includes power, channel masks, interrupt masks, DMA masks, conversion timing, and NSTART/mode bits. Software tracks current direct channel, latest value, active buffered channels, DMA head/tail, and suspend-saved `inpsamp` and power state. There is no nonvolatile persistence.

Dependencies and integration points: it depends on platform resources, DMAengine cyclic slave support, IIO triggered buffers, clocks, PM sleep ops, OF compatible `nxp,s32g2-sar-adc`, and NXP register semantics.

Risks: DMA residue handling is subtle and guarded by comments about backend races. Calibration failure is logged but probe continues, so later accuracy may be degraded. Buffer mode must stop conversion before terminating DMA. Channel masks assume only group-0 channels 0-7 are usable despite timestamp index 32. Sample-frequency writes can divide by user-provided `val` without explicit zero rejection.

Test signals: direct reads, conversion timeout, calibration success and failure, sample-frequency read/write clamping, triggered-buffer scans, software DMA buffer enable/disable and residue edge cases, suspend/resume with active timing, and probe failures for missing IRQ/clock/DMA.
