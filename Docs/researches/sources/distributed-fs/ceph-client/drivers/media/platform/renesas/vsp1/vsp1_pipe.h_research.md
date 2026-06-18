# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_pipe.h

Purpose: declares the shared VSP1 pipeline data model and exported helpers used by VSP1 entities and video nodes. It defines video format metadata, pipeline state values, partition rectangles, and the main `struct vsp1_pipeline`.

Important APIs/types: `struct vsp1_format_info` carries the contract between V4L2 fourccs, media-bus codes, VI6 hardware formats, swap flags, plane counts, bpp, Y/C and U/V swaps, subsampling, and alpha-channel presence. `enum vsp1_pipeline_state` describes stopped/running/stopping. `struct vsp1_partition` stores per-slice rectangles for RPFs, UDS sink/source, SRU, and WPF. `struct vsp1_pipeline` embeds a `media_pipeline`, IRQ lock, waitqueue, kref, stream and buffer readiness counters, entity pointers, ordered entity list, cached stream display-list body, interlace flag, partition table, and underrun count.

Control flow/state: the header expresses two locking domains: `irqlock` for state and buffer readiness in IRQ-sensitive paths, and `lock` for use count/stream count. The `frame_end` callback lets `vsp1_video.c` and `vsp1_vspx.c` install different completion behavior over the same pipeline primitive.

Dependencies/integration: included by nearly all VSP1 blocks. It forward-declares display-list and RWPF types while depending on Linux list/kref/wait/spinlock and media entity types. The debug macro wraps dynamic debug when configured and compiles away otherwise.

Risks and test signals: changes to `struct vsp1_pipeline` affect many files and IRQ paths. Partition fields must stay synchronized with entity callbacks. Test by compiling all VSP1 configurations, running media graph setup/teardown, and exercising multi-input, UDS/SRU, LIF, interlaced, and VSPX paths.
