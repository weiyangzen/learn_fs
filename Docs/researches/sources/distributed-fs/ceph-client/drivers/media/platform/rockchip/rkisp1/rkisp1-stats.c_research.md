# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-stats.c

## Purpose

`rkisp1-stats.c` implements the RKISP1 statistics metadata capture video node. It lets userspace queue buffers that are filled from ISP 3A measurement registers when statistics-related interrupts fire. The file reports AWB, AEC, AFM, histogram, and BLS measurements in `V4L2_META_FMT_RK_ISP1_STAT_3A` buffers.

## Important APIs, Types, And Functions

The V4L2 metadata surface is implemented by `rkisp1_stats_enum_fmt_meta_cap()`, `rkisp1_stats_g_fmt_meta_cap()`, `rkisp1_stats_querycap()`, `rkisp1_stats_ioctl`, and `rkisp1_stats_fops`. Buffer management is implemented by `rkisp1_stats_vb2_queue_setup()`, `rkisp1_stats_vb2_buf_queue()`, `rkisp1_stats_vb2_buf_prepare()`, `rkisp1_stats_vb2_stop_streaming()`, and `rkisp1_stats_init_vb2_queue()`.

Measurement readers include `rkisp1_stats_get_awb_meas_v10/v12()`, `rkisp1_stats_get_aec_meas_v10/v12()`, `rkisp1_stats_get_afc_meas()`, `rkisp1_stats_get_hst_meas_v10/v12()`, and `rkisp1_stats_get_bls_meas()`. `rkisp1_v10_stats_ops` and `rkisp1_v12_stats_ops` select version-specific readers. `rkisp1_stats_send_measurement()` fills a queued buffer, while `rkisp1_stats_isr()` is the interrupt entry point.

## Control Flow

Registration initializes a metadata capture queue, sets the only format to `V4L2_META_FMT_RK_ISP1_STAT_3A`, initializes the ops table according to `isp_ver`, creates one sink media pad, and registers the video device. Userspace allocates two to eight vmalloc-backed buffers, prepares them with enough space for `struct rkisp1_stat_buffer`, and queues them to `stats->stat`.

When the ISP interrupt handler calls `rkisp1_stats_isr(stats, isp_ris)`, this file clears measurement interrupts by writing `RKISP1_STATS_MEAS_MASK` to `RKISP1_CIF_ISP_ICR`, checks whether measurement MIS bits remain set and increments `debug.stats_error` if so, then fills one queued buffer if `isp_ris` contains measurement bits. Each interrupt bit gates a specific reader: AWB done reads AWB registers, AFM finish reads focus sums and luma, exposure end reads AEC means and BLS measured values, and histogram ready reads histogram bins. The completed buffer gets payload size, frame sequence, timestamp, and `VB2_BUF_STATE_DONE`.

## State And Persistence

Runtime state lives in `struct rkisp1_stats`: the queued buffer list, spinlock, selected stats ops, video node, and RKISP1 device pointer. The data delivered to userspace is transient and tied to the ISP frame sequence and interrupt status. There is no persistence outside queued buffers and hardware measurement registers. Stop streaming drains queued buffers with `VB2_BUF_STATE_ERROR`.

## Dependencies And Integration Points

This file depends on V4L2 metadata capture, videobuf2 vmalloc memory, media entity registration, RKISP1 register helpers, `rkisp1-regs.h` measurement register definitions, and `rkisp1_bls_swap_regs()` for Bayer-order-aware BLS value mapping. It integrates with params configuration because params determine AWB/AEC/HST/AFM windows and enable bits, and it integrates with the top-level ISP ISR through `rkisp1_stats_isr()`.

## Risks

The ISR silently drops statistics if no userspace buffer is queued. Packed v12 AEC and histogram reads depend on exact field extraction macros. `rkisp1_stats_get_bls_meas()` relies on the current ISP sink format and Bayer pattern to swap measured channels correctly. The code contains comments questioning concurrent register access from ISR context, so changes that read or write the same measurement registers elsewhere need locking scrutiny. The current stop-streaming loop is bounded by the maximum buffer count; that matches queue setup but should remain aligned if buffer limits change.

## Test Signals

Good signals include metadata format enumeration, buffer size validation, streaming with and without queued buffers, interrupt-driven completion for each measurement bit, v10 and v12 histogram/AEC packing checks, BLS channel ordering across Bayer patterns, timestamp and sequence correctness, `stats_error` behavior when MIS bits remain set, and stop-streaming buffer error completion.
