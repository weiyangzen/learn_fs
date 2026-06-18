# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-sdr-cap.c

Purpose: implements Vivid software-defined-radio capture. It exposes SDR formats, ADC/RF tuner/frequency ioctls, a vb2 capture queue, a sample-rate-driven kthread, and a synthetic FM-modulated complex sample generator.

Important APIs and functions: exported symbols are `vivid_sdr_cap_qops`, `vivid_sdr_enum_freq_bands`, `vivid_sdr_g_frequency`, `vivid_sdr_s_frequency`, `vivid_sdr_g_tuner`, `vivid_sdr_s_tuner`, `vidioc_enum_fmt_sdr_cap`, `vidioc_g_fmt_sdr_cap`, `vidioc_s_fmt_sdr_cap`, `vidioc_try_fmt_sdr_cap`, and `vivid_sdr_cap_process`. Internal functions include `vivid_thread_sdr_cap_tick`, `vivid_thread_sdr_cap`, and vb2 queue callbacks.

Control flow: queue setup/prepare validates a single plane sized for `SDR_CAP_SAMPLES_PER_BUF * 2`. Start streaming initializes sequence start, launches `vivid_thread_sdr_cap`, or returns injected errors. The kthread computes elapsed buffers from `jiffies` and `sdr_adc_freq`, handles resync after ADC frequency changes, updates sequence counters, ticks one queued buffer, then sleeps until the next sample-buffer deadline. `vivid_sdr_cap_process` generates I/Q samples for CU8 or CS8 from fixed-point sine/cosine phases, a 1 kHz source tone, and the FM deviation control.

State and persistence: volatile state in `struct vivid_dev` includes SDR active list, kthread pointer, ADC/RF frequencies, pixel format, buffer size, sequence counters, timestamp wrap offset, fixed-point phases, and FM deviation. Frequency and format settings persist for the device until changed.

Dependencies and integration points: depends on V4L2 SDR/tuner/frequency APIs, videobuf2, kthreads/freezer/jiffies, Linux fixed-point trig helpers, Vivid controls, and streaming error injection shared from `vivid-ctrls.c`.

Risks: the generated samples are synthetic and not tied to `sdr_fm_freq`, so RF frequency is only control-plane state. Fixed-point math and modulo behavior can produce artifacts but is adequate for test data. ADC frequency changes while streaming rely on `sdr_cap_seq_resync`. The queue always sizes buffers for the largest 8-bit complex sample representation.

Test signals: SDR format enum/try/set/get, ADC/RF frequency clamp boundaries, streaming cadence at each ADC band, CU8 and CS8 sample value ranges, FM deviation effects, nonblocking streamoff cleanup, and v4l2-compliance SDR tests are useful.
