# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-ts.c

Purpose: implements the shared MPEG transport-stream DMA queue and hardware programming for SAA7134 cards. DVB, Empress, and generic MPEG paths use it to capture TS packets through DMA channel 5.

Important APIs, types, and functions: module parameters `tsbufs` and `ts_nr_packets` configure buffer count and packets per buffer. Exported vb2 callbacks include `saa7134_ts_buffer_init()`, `saa7134_ts_buffer_prepare()`, `saa7134_ts_queue_setup()`, `saa7134_ts_start_streaming()`, `saa7134_ts_stop_streaming()`, and `saa7134_ts_qops`. Hardware functions `saa7134_ts_init_hw()`, `saa7134_ts_init1()`, `saa7134_ts_start()`, `saa7134_ts_stop()`, `saa7134_ts_fini()`, and IRQ handler `saa7134_irq_ts_done()` are used by core and MPEG modules.

Control flow: core early init calls `saa7134_ts_init1()` on MPEG-capable cards, which clamps module parameters, initializes `dev->ts_q`, marks the queue as needing two buffers, allocates a DMA page table, and initializes TS registers. Queue setup computes one-plane buffer size as `TS_PACKET_SIZE * dev->ts.nr_packets`. Buffer prepare validates plane size, sets payload, and builds the page table entries. Buffer activation alternates top/bottom field targeting between current and next buffers, writes `RS_BA1/BA2(5)`, enables DMA bits, arms a timeout, and starts TS hardware on the first buffer. IRQ completion waits for the expected top/bottom status bit before finishing a buffer and advancing the queue. Stop disables TS hardware and drains queued/current buffers through core stop helpers.

State and persistence: `dev->ts`, `dev->ts_q`, `dev->ts_field`, `dev->ts_started`, DMA page table contents, and TS MMIO registers are runtime-only. No persistent state exists.

Dependencies and integration points: depends on core buffer/page-table helpers, `saa7134_set_dmabits()`, vb2 DMA-SG, board metadata for TS serial/parallel type and forced valid bit, and core IRQ dispatch from `DONE_RA2`. Empress wraps these qops; DVB uses them directly; GO7007 overrides IRQ/start behavior for its encoder.

Risks: TS DMA channel 5 conflicts with planar video capture, so `saa7134_ts_start_streaming()` rejects TS when planar video is busy and requeues buffers. Queue activation needs a next buffer for ping-pong DMA; underflow or field mismatch can stall until timeout. Board `ts_type` and `ts_force_val` must match hardware wiring. Page-table lifetime must cover all queued buffers.

Test signals: TS buffer allocation with clamped sizes, DVB/Empress streamon and read/mmap paths, `-EBUSY` when planar video is active, top/bottom IRQ ordering, timeout recovery, serial and parallel TS board coverage, module unload freeing page tables, and absence of packet-size/payload mismatches.
