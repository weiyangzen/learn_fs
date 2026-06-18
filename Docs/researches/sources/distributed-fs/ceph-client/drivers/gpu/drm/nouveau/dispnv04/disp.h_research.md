<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/disp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/disp.h

## Purpose
This header defines the shared pre-NV50 display state and declares the CRTC, encoder, TV, overlay, and helper entry points used across `dispnv04`.

## Important APIs, Types, and Functions
Key data structures are `enum nv04_fp_display_regs`, `struct nv04_crtc_reg`, `struct nv04_output_reg`, `struct nv04_mode_state`, and `struct nv04_display`. It declares creation functions such as `nv04_display_create`, `nv04_crtc_create`, `nv04_dac_create`, `nv04_dfp_create`, `nv04_tv_create`, and `nv17_tv_create`, plus helper functions for FP binding, DAC clock/load detection, overlay init, BIOS init-table execution, and flip events. Inline hardware-family helpers include `nv_two_heads`, `nv_gf4_disp_arch`, `nv_two_reg_pll`, and `nv_match_device`.

## Control Flow
The header has no standalone execution, but its inline helpers drive many hardware-condition branches. `nv_two_heads` gates dual-head paths based on PCI device and family, `nv_gf4_disp_arch` selects GF4-style register layout, `nv_two_reg_pll` selects PLL decode/programming paths, and `nouveau_bios_run_init_table` invokes `nvbios_init` with output and head context.

## State and Persistence Behavior
`struct nv04_crtc_reg` is a full save/restore snapshot of VGA, PCRTC, PRAMDAC, TV, flat-panel, dither, cursor, and CTV registers. `struct nv04_display` persists current and saved mode state, VGA font planes, DAC user accounting, image BOs, the flip event object, and the owning DRM client pointer.

## Dependencies and Integration Points
It pulls in Nouveau display core state, BIOS PLL/init helpers, NVIF events, DCB output types, and PCI device checks. Most NV04 CRTC, DAC, DFP, TV, and overlay files share this header as their state contract.

## Risks
The large register snapshots must stay aligned with save/load code in `hw.c` and encoder files; missing fields cause incomplete restore. Family predicates encode chipset exceptions and can break unusual PCI IDs. The BIOS init wrapper relies on compound-literal style macro arguments to `nvbios_init`, so signature drift is build-sensitive.

## Test Signals
Build coverage across all `dispnv04` objects is the first signal. Runtime signals include correct dual-head detection, PLL programming on NV30/NV40 families, BIOS init-table execution for all output types, suspend/resume register restore, and flip-event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/disp.h -->
