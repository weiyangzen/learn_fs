# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_render_cl.c

Purpose: Generates kernel-owned VC4 render command lists (RCLs). Instead of accepting userspace RCLs, it validates submitted render surfaces and emits the small set of legal tile load, bin-list branch, and store packets needed for rendering.

Important APIs/types/functions: `struct vc4_rcl_setup` tracks surface BOs, the allocated RCL BO, and write offset. `rcl_u8/u16/u32()` append packet data. `emit_tile()` emits per-tile load(s), tile coordinates, optional semaphore wait/sub-list branch, and stores. `vc4_create_rcl_bo()` sizes/allocates the RCL BO and fills it. `vc4_full_res_bounds_check()`, `vc4_rcl_msaa_surface_setup()`, `vc4_rcl_surface_setup()`, and `vc4_rcl_render_config_surface_setup()` validate surface descriptors. `vc4_get_rcl()` is the public entry point.

Control flow: `vc4_get_rcl()` rejects gen>4, validates tile ranges and binning bounds, resolves and validates color/Z/MSAA read/write surfaces, requires at least one write target, then calls `vc4_create_rcl_bo()`. RCL creation computes exact packet size, emits clear colors if requested, emits `TILE_RENDERING_MODE_CONFIG`, iterates tiles in requested order, and records CT1 start/end addresses in `exec`.

State and persistence: Allocates a `VC4_BO_TYPE_RCL` BO added to `exec->unref_list` for job lifetime. Records write BOs in `exec->rcl_write_bo[]`, CT1 addresses in `exec->ct1ca/ct1ea`, and surface pointers only in stack setup. No global state.

Dependencies and integration points: Uses UAPI submit structs, BO lookup via `vc4_use_bo()`, texture/render-size validation via `vc4_check_tex_size()`, packet constants from `vc4_packet.h`, and V3D submit scheduling that later runs CT1. Coupled to binner output through `exec->tile_alloc_offset` and bin tile dimensions.

Risks: Packet size accounting must match emitted bytes; `BUG_ON(setup->next_offset != size)` catches mismatches but would be fatal. Full-res tile bounds math and tile ordering are security-sensitive because they generate DMA addresses. Misordered tile coordinates/load/store packets can violate hardware sequencing. The code is gen4-only.

Test signals: Submit tests should validate bad tile ranges, missing write surfaces, invalid tiling/format bits, unaligned offsets, out-of-bounds full-res/MSAA buffers, and legal color/Z/MSAA combinations. Rendering tests should exercise clears, partial tile ranges, fixed RCL order flags, binned and binless submits, and EOF placement on the last store.
