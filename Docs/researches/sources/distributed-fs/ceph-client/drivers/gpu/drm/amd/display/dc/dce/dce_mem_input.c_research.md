# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_mem_input.c

## Purpose
This file implements the DCE memory input block for scanout planes. It programs tiling, pixel format, plane dimensions, rotation, graphics addresses, flip locking, PTE/VM fetch parameters, DMIF buffer allocation, and display watermarks for urgency, stutter, and NB/P-state changes.

## Important APIs and Functions
The implementation exposes `dce_mem_input_construct()`, optional `dce60_mem_input_construct()`, `dce112_mem_input_construct()`, and `dce120_mem_input_construct()`. The vtables wire `mem_input_program_display_marks`, `allocate_mem_input`, `free_mem_input`, `mem_input_program_surface_flip_and_addr`, `mem_input_program_pte_vm`, `mem_input_program_surface_config`, `mem_input_is_flip_pending`, and `mem_input_clear_tiling`. Internal helpers include `get_mi_bpp()`, `get_mi_tiling()`, `dce_mi_program_pte_vm()`, watermark programmers, `program_tiling()`, `program_size_and_rotation()`, `program_grph_pixel_format()`, DMIF allocation/free, and primary/secondary address writers.

## Control Flow
Surface setup enables graphics, writes tiling fields based on available GFX6/GFX8/GFX9 masks, programs dimensions/pitch and optional rotation, then programs graphics pixel format for non-video formats. Flip programming locks `GRPH_UPDATE`, configures immediate versus H-retrace update behavior, writes high address registers before low address registers, records request/current addresses, then unlocks. PTE setup maps format and tiling to static page-width/page-height/min-PTE settings and programs outstanding request limits and PTE arbitration. Watermark setup writes multiple watermark sets depending on generation: base DCE writes A/D, DCE112 and DCE120 write A/B/C/D, and DCE120 additionally writes urgent-level and stutter-entry fields.

## State and Persistence
The base `mem_input` stores context, instance, function table, current address, and requested address. `struct dce_mem_input` stores register metadata and a workaround byte for `single_head_rdreq_dmif_limit`. Hardware state persists in DCP graphics control/address/update registers and DMIF/MC/DCHUB arbitration and watermark registers. Flip pending state is read from `GRPH_SURFACE_UPDATE_PENDING`; when no pending update remains, the software current address is synchronized to the requested address.

## Dependencies and Integration Points
Dependencies include `dce_mem_input.h`, `reg_helper.h`, `basics/conversion.h`, DC tiling/plane/address types, display watermark structures, and DC debug flags such as `disable_stutter`. It integrates with plane programming, display mode bandwidth/watermark calculation, VM/PTE fetch behavior, and DMIF buffer allocation in the DCE display pipe.

## Risks and Test Signals
`get_dmif_switch_time_us()` contains a suspicious guard `if (!h_total || v_total || !pix_clk_khz)`, which returns the fallback whenever `v_total` is nonzero and likely should have been `!v_total`. DMIF allocation/free waits may be too long or poorly calculated as a result. Pixel-format support logs unsupported formats but continues, so invalid format paths may leave stale register values. Address programming silently skips zero addresses but still returns true. Tiling code selects paths based on mask presence and can double-program if masks overlap unexpectedly. Test signals include page-flip tests for immediate and vblank flips, stereo address programming, rotation tests, GFX6/GFX8/GFX9 tiling, PTE settings for bpp/tiling combinations, stutter/P-state watermark validation, and DMIF allocation timeout tests.
