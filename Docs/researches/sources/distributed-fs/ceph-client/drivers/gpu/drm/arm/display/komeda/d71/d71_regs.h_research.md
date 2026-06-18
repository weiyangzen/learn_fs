# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_regs.h

Purpose: central D71 register map and hardware bit definitions for GCU, LPU, CU, DOU, layers, writeback, scaler, merger, splitter, backend timing, image processing, and coefficient blocks.

Important APIs/types/functions: macro groups define common block offsets, field extractors, IRQ/status bits, control bits, size/offset/crop packers, opmodes, AFBC controls, scaler coefficient addressing, block types, D71 limits/defaults, and `struct block_header`. `get_block_type()` extracts the D71 block type.

Control flow: no executable control flow. D71 code reads headers with these offsets, maps block types during probing, programs registers during component updates, and decodes events during IRQ handling.

State and persistence: describes hardware state layout. Persistent effects occur through callers writing register values generated with these macros.

Dependencies/integration: consumed by `d71_dev.c`, `d71_component.c`, and `d71_dev.h`. It must match hardware documentation for D71/D32/D6-family register compatibility.

Risks: any wrong offset, bit mask, or packing width directly corrupts hardware programming. Some defaults encode policy (`D71_DEFAULT_PREPRETCH_LINE`, cache bits, bus width). `HV_SIZE`/`HV_OFFSET` silently truncate to 12/13-bit fields. Test signals: register dump comparison with vendor docs, mode timing readback, scaler/layer programming traces, IRQ status injection, and static compile checks for macro users.
