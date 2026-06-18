# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec.h

Purpose: central internal header for the Rockchip RKVDEC driver. It defines device/context structures, coded/decoded format descriptors, codec operation interfaces, variant operation interfaces, decoded buffer metadata, allocation records, and exported helpers shared by core and codec backends.

Important APIs and types: `struct rkvdec_dev`, `struct rkvdec_ctx`, `struct rkvdec_variant`, `struct rkvdec_variant_ops`, `struct rkvdec_coded_fmt_ops`, `struct rkvdec_coded_fmt_desc`, `struct rkvdec_decoded_fmt_desc`, `struct rkvdec_run`, `struct rkvdec_decoded_buffer`, `enum rkvdec_image_fmt`, `enum rkvdec_alloc_type`, and `struct rkvdec_aux_buf`. It declares codec ops for legacy, VDPU381, VDPU383, and VP9 backends.

Control flow: core code creates `rkvdec_ctx`, selects a `coded_fmt_desc`, invokes codec ops through `rkvdec_coded_fmt_ops`, and exposes helper functions for backends to acquire buffers, copy registers, schedule watchdogs, and apply quirks.

State and persistence: no state is allocated by the header, but it defines all major in-memory state contracts. Device state persists for the platform-device lifetime; context state persists for file-handle lifetime; codec-private and RCB state persists for streaming lifetime.

Dependencies and integration points: includes Linux platform/video/clock/wait headers, V4L2 controls/device/ioctl/mem2mem, and vb2 DMA-contig. It integrates every file in the RKVDEC driver directory.

Risks: this header is a broad coupling point; changes to context, variant, or ops structures affect multiple codec implementations. `ctx->priv` is untyped and requires correct start/stop pairing. Bitfield flags `has_sps_st_rps` and `has_sps_lt_rps` are set by control changes and consumed by HEVC backends.

Test signals: full RKVDEC build coverage, sparse/compiler warnings for structure changes, and runtime coverage of every codec ops table.
