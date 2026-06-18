## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_mem_input_v.c

Purpose: DCE11 underlay/video memory-input programming for UNP registers. It programs luma and chroma surface addresses, tiling metadata, plane size, rotation, pixel/video format, DVMM PTE behavior, display watermarks, and the `mem_input_funcs` vtable used by the DC plane pipeline.

Important APIs: `dce110_mem_input_v_construct`, `dce_mem_input_v_program_surface_flip_and_addr`, `dce_mem_input_v_program_surface_config`, `dce_mem_input_v_program_pte_vm`, `dce_mem_input_v_program_display_marks`, `dce_mem_input_program_chroma_display_marks`, and `dce_mem_input_v_is_surface_pending`. Helpers split luma/chroma register programming and map tiling/pixel formats to UNP/DVMM fields.

Control flow: construction installs a static function table. Surface setup enables UNP graphics, writes tiling, size/rotation, and format. Flip setup writes pending mode and high-before-low addresses, then caches `request_address`. Pending checks read `UNP_GRPH_UPDATE` and promote `request_address` to `current_address` when hardware clears the pending bit. Watermark programming writes masked A/B sets separately for luma and chroma.

State and persistence: state is mostly hardware register state plus `mem_input` cached addresses. PTE settings and watermarks persist in registers until reprogrammed. Risks include hard-coded request limits, ignored `flip_immediate`, unsupported address types triggering debug breaks, rotation-dependent PTE choices, and L/C register sequencing. Test signals are modeset/flip on video 4:2:0 and graphics planes, rotated planes, watermark changes, stutter disable debug behavior, and flip-pending convergence.
