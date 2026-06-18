# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-common.c

`coda-common.c` is the platform/V4L2/vb2 layer for the CODA mem2mem codec. It defines supported codecs and video nodes per SoC, registers the platform driver, loads firmware asynchronously, initializes hardware, creates V4L2 mem2mem devices, implements ioctl handling, manages controls, and dispatches work to BIT or direct JPEG context operations.

Important functions include `coda_write()`, `coda_read()`, `coda_write_base()`, `coda_find_codec()`, format try/set helpers, `coda_encoder_cmd()`, `coda_decoder_cmd()`, `coda_device_run()`, `coda_pic_run_work()`, `coda_job_ready()`, `coda_queue_setup()`, `coda_buf_queue()`, `coda_start_streaming()`, `coda_stop_streaming()`, `coda_s_ctrl()`, `coda_ctrls_setup()`, `coda_open()`, `coda_release()`, `coda_hw_init()`, `coda_fw_callback()`, `coda_probe()`, and `coda_remove()`.

Probe obtains clocks/MMIO/IRQs/reset/IRAM/VDOA, registers `v4l2_device`, creates debugfs and workqueue state, enables runtime PM, and requests firmware. The callback copies/reorders firmware, starts the BIT processor, checks firmware, initializes V4L2 mem2mem, and registers encoder/decoder/JPEG nodes. Open allocates `struct coda_ctx`, powers/clocks the hardware, creates queues, default formats, controls, and synchronization primitives.

Streaming starts independently per queue; when both queues are active, common code validates dimensions, initializes decoder bitstream state as needed, resets counters, and calls context `start_streaming`. Mem2mem work locks buffer and hardware mutexes, calls `prepare_run`, waits for IRQ completion, handles timeout/reset, calls `finish_run`, and completes the job.

State is split between `struct coda_dev` and `struct coda_ctx`, with DMA buffers optionally visible via debugfs. No driver data is written to the filesystem beyond firmware reads. Integration points include OF compatibles, clocks, reset, gen_pool IRAM, runtime PM, firmware loader, V4L2 events/controls/ioctls, vb2, and optional VDOA.

Risks include asynchronous firmware failure paths, non-obvious direct JPEG queue choice, format changes while queues are busy, timeperframe approximation, module parameters changing memory layout, and careful buffer return semantics on partial stream-on errors. Test with v4l2-compliance, firmware fallback, per-SoC node registration, EOS/source-change events, VDOA/YUYV gating, runtime PM resume, and clean open/release/remove.
