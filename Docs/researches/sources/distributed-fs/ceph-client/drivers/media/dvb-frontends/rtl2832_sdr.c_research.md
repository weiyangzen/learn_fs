# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832_sdr.c

Purpose: V4L2 SDR capture driver for RTL2832U devices, sharing the RTL2832 regmap, tuner, and parent DVB USB streaming path to expose raw IQ samples.

Important APIs/types/functions: `struct rtl2832_sdr_dev` owns V4L2/vb2 state, USB URBs, coherent buffers, control handler, tuner frequencies, sample format, and power flags. Probe registers a V4L2 SDR `video_device`. vb2 callbacks are `queue_setup`, `buf_prepare`, `buf_queue`, `start_streaming`, and `stop_streaming`. `rtl2832_sdr_set_adc()` programs demod ADC/IF/sample-rate registers. V4L2 ioctls handle tuner queries, frequency bands, SDR formats, stream I/O, and controls.

Control flow: streaming powers the parent USB device, enables frontend ADC, wakes tuner, applies RF/ADC settings, allocates coherent USB buffers and URBs, then submits bulk reads on endpoint 0x81. URB completion converts CU8 to CU8 or emulated CU16LE, fills the next vb2 buffer, timestamps it, and resubmits. stop kills/free URBs, returns queued buffers with error, restores ADC/tuner, and powers down.

State and persistence: state is volatile in `rtl2832_sdr_dev`: flags `POWER_ON`/`URB_BUF`, URB lists, queue list, sequence, `udev`, frequencies, format, sample counters, and controls. No persistent storage.

Dependencies/integration: platform device data supplies regmap, DVB frontend, tuner V4L2 subdev, and DVB USB device. Uses V4L2, videobuf2-vmalloc, USB core, regmap, firmware-independent tuner ops, and parent power/frontend callbacks.

Risks: disconnect safety depends on lock ordering and `udev` checks; URB completion runs in interrupt context and resubmits unconditionally after nonfatal errors; tuner-specific ADC register sequences repeatedly overwrite `ret` without checking every write; format changes are blocked only while vb2 is busy; CU16LE is marked emulated and optional.

Test signals: `/dev/swradio*` registration, V4L2 capability/format enumeration, streaming with mmap/read/userptr, frequency/band controls, clean unplug during streaming, no leaked URBs/buffers, sample-rate debug output, and valid IQ data in GNU Radio or rtl-sdr style consumers.
