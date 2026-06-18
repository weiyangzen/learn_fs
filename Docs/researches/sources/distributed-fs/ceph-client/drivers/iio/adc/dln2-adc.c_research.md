# sources/distributed-fs/ceph-client/drivers/iio/adc/dln2-adc.c

## Purpose
This driver exposes the Diolan DLN-2 USB ADC adapter as an IIO voltage device. It supports direct reads, configurable sampling frequency, and triggered buffered capture driven by DLN2 firmware events. The hardware protocol is command-based through the DLN2 MFD transport rather than local MMIO.

## Important APIs, Types, And Functions
`struct dln2_adc` stores the platform device, fixed channel specs, port number, trigger channel, IIO trigger, mutex, cached sample period, and a compact demux table. Protocol helpers include `dln2_adc_get_chan_count()`, `dln2_adc_set_port_resolution()`, `dln2_adc_set_chan_enabled()`, `dln2_adc_set_port_enabled()`, `dln2_adc_set_chan_period()`, `dln2_adc_read()`, and `dln2_adc_read_all()`. Buffer flow is handled by `dln2_update_scan_mode()`, `dln2_adc_triggered_buffer_postenable()`, `dln2_adc_trigger_h()`, `dln2_adc_triggered_buffer_predisable()`, and `dln2_adc_event()`.

## Control Flow
Probe reads platform port data, sets 10-bit resolution, queries channel count and clamps to eight, builds channel specs plus timestamp, allocates/registers an immutable IIO trigger, sets up a triggered buffer, registers a DLN2 event callback for condition-met events, and registers the IIO device. Direct raw reads claim IIO direct mode, lock, enable the channel and ADC port, read `DLN2_ADC_CHANNEL_GET_VAL` twice to work around an initial zero after enabling, then disables the port and channel. Buffered mode enables all channels selected in `update_scan_mode()`, builds a demux plan from the fixed eight-value firmware layout into the active scan layout, enables the ADC port on buffer postenable, uses the first active channel as the periodic trigger source, and on each DLN2 event reads all channel values, demuxes active values, and pushes a timestamped scan.

## State And Persistence
State is volatile but spans buffer lifetime: enabled channels in firmware, ADC port enable, trigger channel, sample period in milliseconds, and demux mapping. `sample_period` is cached as milliseconds derived from requested frequency and clamped to 65535 ms; zero frequency maps to `UINT_MAX` then clamps when applied. Remove unregisters the IIO device and DLN2 event callback.

## Dependencies And Integration Points
The driver depends on the DLN2 MFD command/event transport, platform data for port selection, IIO core, immutable IIO triggers, triggered buffers, kfifo buffer support, and firmware event `DLN2_ADC_CONDITION_MET_EV`. It advertises fixed 3.3 V / 10-bit scale as `IIO_VAL_INT_PLUS_NANO`.

## Risks And Test Signals
Risks include firmware command failures leaving channels enabled, conflict masks when ADC pins are shared with other DLN2 functions, sample-period unit conversions with low frequencies, the event callback running from URB completion context and only polling the trigger, and demux assumptions around eight fixed values. Test signals include protocol short-response `-EPROTO`, conflict mask turning into `-EBUSY`, direct reads disabling channel/port on all error paths, sparse scan masks demuxing correctly, periodic event capture at configured sample frequencies, and cleanup unregistering the event callback.
