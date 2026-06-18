# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_rwpf.h

Purpose: declares the shared Read/Write Pixel Formatter model used by VSP1 RPF and WPF implementations and their video-node wrappers.

Important APIs/types: defines pad indices `RWPF_PAD_SINK`/`RWPF_PAD_SOURCE`, minimum dimensions, `struct vsp1_rwpf_memory` with up to three DMA plane addresses, and `struct vsp1_rwpf`. The RWPF structure embeds a `vsp1_entity`, V4L2 control handler, optional video node, active multi-plane format, format info, BRx input index, alpha, alpha multiplier, output format, flip/rotation state with spinlock and controls, current memory addresses, writeback flag, and WPF display-list manager.

Control flow/state: state is runtime-only and split between media-subdev state, queued video buffer memory, and controls. `flip.pending` is updated by controls; `flip.active` is latched per frame by WPF programming. `mem` is updated when VB2 queues select the next buffer.

Dependencies/integration: included by RPF/WPF/RWPF common code, video node code, VSPX, and pipeline helpers. It exposes `vsp1_rpf_create()`, `vsp1_wpf_create()`, `vsp1_wpf_stop()`, `vsp1_rwpf_init_ctrls()`, and `vsp1_rwpf_subdev_ops`.

Risks and test signals: the structure is shared across IRQ, streaming, and control paths, so locking discipline matters. Test signals include races between controls and streaming, buffer queue updates, writeback one-shot operation, and RPF/WPF cleanup through `vsp1_entity_destroy()`.
