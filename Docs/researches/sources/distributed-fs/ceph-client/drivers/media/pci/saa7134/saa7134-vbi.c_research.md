# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-vbi.c

Purpose: implements VBI capture queue setup, scaler programming, DMA setup, and IRQ completion for SAA7134 vertical blanking interval data.

Important APIs, types, and functions: module parameters `vbi_debug` and `vbibufs` control tracing and default buffer count. `task_init()` programs VBI scaler/task registers for Task A and Task B from the active TV norm. The file provides `saa7134_vbi_qops`, `saa7134_vbi_init1()`, `saa7134_vbi_fini()`, and `saa7134_irq_vbi_done()` for core/video integration.

Control flow: core early init calls `saa7134_vbi_init1()`, which initializes the VBI DMA queue and timeout and clamps buffer count. Queue setup computes VBI line count from the active TV norm, clamps it to 17 lines, fixes line length at 2048 bytes, and advertises one plane sized for two fields. Buffer prepare requires page-aligned SG offset, validates plane size, sets payload, and builds DMA page-table entries. Buffer activation programs both VBI tasks, sets output format, configures DMA channels 2 and 3 with top/bottom offsets into the same buffer, enables DMA bits through core, and arms a timeout. IRQ completion records that the first field was seen, waits for the second field, finishes the buffer, and advances the queue.

State and persistence: uses `dev->vbi_q`, `dev->vbi_hlen`, `dev->vbi_vlen`, current TV norm timing, per-buffer `top_seen`, and DMA page-table contents. All state is runtime-only.

Dependencies and integration points: depends on core buffer/page-table/DMA-bit helpers, vb2 DMA-SG, TV norm metadata, scaler/register definitions, and core IRQ dispatch for `DONE_RA0` VBI status. V4L2 device registration and ioctl exposure are handled by the video/core files.

Risks: VBI capture rejects non-page-aligned buffers because DMA programming assumes page-start alignment. TV norm changes affect line counts and scaler timings, so active streaming across norm changes must be coordinated by higher layers. Completion depends on seeing both fields in order; missed IRQs rely on timeout recovery. DMA channels 2 and 3 must stay consistent with `saa7134_set_dmabits()`.

Test signals: VBI device registration, buffer queue setup for PAL/NTSC norms, page-alignment rejection, capture producing two-field payloads of expected size, IRQ completion only after both fields, timeout recovery, norm-change behavior before streaming, and clean timer deletion on remove.
