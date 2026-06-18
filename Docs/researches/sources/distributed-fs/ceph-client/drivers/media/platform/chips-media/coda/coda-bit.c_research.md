# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-bit.c

`coda-bit.c` is the BIT-processor command implementation for CODA encode/decode contexts. It owns firmware command submission, hardware reset, per-context register restore, bitstream FIFO synchronization, internal framebuffer/work/parameter buffer allocation, IRAM partitioning, encoder sequence setup, decoder sequence setup, picture run preparation/completion, timeout handling, sequence end, and the BIT IRQ completion path.

Important functions include `coda_command_async()`, `coda_command_sync()`, `coda_hw_reset()`, `coda_fill_bitstream()`, `coda_bit_stream_end_flag()`, `coda_check_firmware()`, `coda_start_encoding()`, `coda_prepare_encode()`, `coda_finish_encode()`, `__coda_decoder_seq_init()`, `coda_prepare_decode()`, `coda_finish_decode()`, and `coda_irq_handler()`. The exported operation tables are `coda_bit_encode_ops` and `coda_bit_decode_ops`, consumed by `coda-common.c`.

Control flow is command-oriented. Encoders run sequence initialization, allocate/register reference buffers, cache H.264/MPEG4 headers, then submit one `PIC_RUN` per source/destination pair. Decoders copy vmalloc source buffers into a DMA bitstream ring, store timestamp metadata in `buffer_meta_list`, run sequence initialization when enough headers are available, then decode into internal frames and return display frames in presentation order, optionally through VDOA. IRQ completion wakes the mem2mem work item via `ctx->completion`.

State is per `struct coda_ctx`: `initialized`, `bit_stream_param`, FIFO positions, metadata list, internal frames, sequence counters, frame memory control, IRAM allocations, VDOA/tiled state, and cached stream headers. Device state includes firmware and hardware registers but no filesystem persistence.

Dependencies are V4L2 mem2mem/vb2, dma-contig/vmalloc memory, CODA registers, tracepoints, `coda-h264.c`, MPEG helpers, JPEG helpers, optional VDOA, clocks, reset, and IRQ completions.

Risks include firmware workarounds, hardware timeouts, fragile FIFO/metadata synchronization, H.264 counter roll-over, stream-end read-pointer overshoot, and CODA960 reset/GDI quirks. Good tests are firmware validation, encode/decode stream-on/off, EOS events, source-change events, H.264 SPS crop fixups, reordered decode timestamps, VDOA output, MB error counts, timeout reset, and release after abort.
