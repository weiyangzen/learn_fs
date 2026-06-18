# sources/distributed-fs/ceph-client/drivers/iio/adc/ti_am335x_adc.c

Purpose: platform IIO driver for the ADC block inside TI AM335x/AM437x TSCADC MFD, supporting direct reads, kfifo buffered reads via FIFO1 IRQ, optional cyclic DMA, shared step-engine coordination with touchscreen, and suspend/resume.

Important APIs/types/functions: `struct tiadc_device` stores MFD pointer, FIFO lock, channel-to-step mapping, DT delay/averaging arrays, DMA state, and sample buffers. `tiadc_step_config()` programs sequencer steps. `tiadc_read_raw()` performs single-channel conversions. Buffer ops (`tiadc_buffer_preenable/postenable/predisable/postdisable`) manage FIFO, step engine, DMA, and IRQs. `tiadc_irq_h()`, `tiadc_worker_h()`, and `tiadc_dma_rx_complete()` feed buffers.

Control flow: probe obtains the MFD device, parses `ti,adc-channels` and optional per-channel averaging/open/sample delays, configures steps, sets FIFO threshold, builds dynamic IIO channels, registers a kfifo buffer and shared IRQ, registers IIO, then tries to acquire DMA channel `fifo1`. Direct reads reject operation while buffer is enabled, wait for idle, flush FIFO1, trigger exactly the mapped step, poll FIFO count until data arrives, scan all FIFO entries for the requested step id, and mark ADC done. Buffered enable flushes FIFO, configures continuous steps for active scan channels, enables DMA or FIFO threshold IRQs, and caches step bits in the MFD sequencer.

State and persistence: channel mapping, delays, averages, active buffered step mask, total enabled channels, and DMA period metadata are in memory. Hardware sequencer/FIFO/DMA registers hold runtime state; no persistent storage.

Dependencies and integration: platform device from `ti_am335x_tscadc` MFD, MMIO registers, shared IRQ, DMA engine, IIO kfifo, OF properties, and PM sleep callbacks.

Risks: ADC and touchscreen share hardware and IRQs, so step-engine cache coordination is critical; DMA is requested after IIO registration and failure unregisters IIO only for non-ENODEV; `total_ch_enabled` is incremented during postenable and must be reset during predisable. Test signals include direct read timeout/no matching step, FIFO overrun recovery, DMA and non-DMA buffer paths, DT truncation warnings, and suspend/resume restoring buffered steps.
