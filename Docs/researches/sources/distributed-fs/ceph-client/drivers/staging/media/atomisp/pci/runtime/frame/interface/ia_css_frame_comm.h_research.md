# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/frame/interface/ia_css_frame_comm.h

Purpose: defines the compact frame structures shared with SP-side code.

Important types: SP plane structs for raw/binary/YUV/NV/RGB/six-plane layouts, `ia_css_sp_resolution`, `ia_css_frame_sp_info`, `ia_css_buffer_sp`, and `ia_css_frame_sp`. Conversion APIs map host `ia_css_frame_info` and `ia_css_resolution` to the SP representations.

Control flow/state: no owned state; the structs are ABI payloads that carry offsets, padded widths, format, raw depth/order, and buffer source metadata for SP queues or xmem addresses.

Dependencies/integration: includes buffer queue communication definitions and `system_local.h` for `ia_css_ptr`. `frame.c` implements the conversion functions; SP pipeline setup and buffer queue code consume the structures.

Risks: fields are narrowed to `u16`/`u8`, so callers must avoid silently truncating large dimensions or enum values. Struct layout is a cross-processor contract and should not be changed without SP firmware compatibility checks.

Test signals: host-to-SP conversion for max supported dimensions, raw metadata propagation, queue-id vs xmem buffer source selection, and ABI size/layout checks when compiler packing changes.
