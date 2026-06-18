# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpdma_priv.h

Purpose: private VPDMA register and descriptor layout header. It defines MMIO offsets, interrupt register layout, client CSTAT fields, hardware data type values, raw channel numbers, and inline pack/unpack helpers for data transfer, configuration, and control descriptors.

Important APIs/types: top-level register macros cover `VPDMA_LIST_ADDR`, `VPDMA_LIST_ATTR`, list status, background colors, max size registers, channel/client/list interrupt status/mask, and VPE/VIP client CSTAT offsets. Hardware data type macros encode YUV, RGB, raw-reused, and motion-vector formats. `struct vpdma_dtd`, `struct vpdma_cfd`, and `struct vpdma_ctd` model data transfer, configuration, and control descriptors. Inline helpers such as `dtd_type_ctl_stride()`, `dtd_pkt_ctl()`, `dtd_desc_write_addr()`, `cfd_pkt_payload_len()`, and `ctd_type_source_ctl()` compose descriptor words; paired getters support debug dumps.

Control flow: `vpdma.c` uses this header to translate high-level helper calls into descriptor words and register fields. `vpe.c` and `vip.c` include it indirectly/directly where they need private VPDMA constants such as max-size registers and raw channel numbers.

State and persistence: no dynamic software state is stored here. The file describes persistent hardware state in VPDMA registers and the in-memory descriptor ABI consumed by the VPDMA list parser.

Dependencies and integration: used by the VPDMA helper implementation and by TI VPE/VIP clients. It integrates the driver with documented VPDMA descriptor packet types, control descriptor operations, data type mappings, and hardware channel numbering.

Risks: any bitfield or channel-number drift from the hardware TRM/errata silently corrupts DMA programming. Some getter helpers reuse masks in ways that should be reviewed, such as `ctd_get_fid0_ctl()` masking with `CTD_FID2_MASK`. Several fields are packed by shifts without explicit masking in setter helpers, relying on callers to pass bounded values. Descriptor structs assume the compiler layout matches the hardware 32-bit word sequence.

Test signals: compile coverage plus dynamic debug descriptor dumps; VPDMA register traces for max size, list attr, CSTAT, and interrupt masks; DMA transfers for every supported YUV/RGB/raw/motion-vector data type; and hardware tests that exercise sync-on-channel and abort-channel CTDs.
