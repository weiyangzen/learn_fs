<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/hw.c

## Purpose
This file implements low-level NV04-NV4x display register access, PLL reading, clock derivation, VGA font preservation, and full display mode state save/load for legacy VGA, CRTC, RAMDAC, palette, flat-panel, TV, cursor, and overlay-related registers.

## Important APIs, Types, and Functions
Public helpers include `NVWriteVgaSeq`, `NVReadVgaSeq`, `NVWriteVgaGr`, `NVReadVgaGr`, `NVSetOwner`, `NVBlankScreen`, `nouveau_hw_get_pllvals`, `nouveau_hw_pllvals_to_clk`, `nouveau_hw_get_clock`, `nouveau_hw_save_vga_fonts`, `nouveau_hw_save_state`, `nouveau_hw_load_state`, and `nouveau_hw_load_state_palette`. Internal helpers decode PLLs, save/load RAMDAC/VGA/extended/palette state, and work around bad unused-head VPLL values.

## Control Flow
Register access wrappers program VGA index/data pairs through PRMVIO. `NVSetOwner` writes CR44 and special NV11 dummy registers to select the active VGA owner. PLL queries parse VBIOS PLL limits, read the appropriate one- or two-register coefficients, handle Celsius single-stage VPLL state, and decode coefficients into `nvkm_pll_vals`. Clock reads special-case nForce memory clocks through PCI config space. VGA font save/restore maps the first 64 KiB of VRAM, blanks displays, programs VGA planes, copies four 16 KiB font planes, and restores VGA control registers.

Mode save calls RAMDAC, VGA, palette, and extended-save routines after fixing bad NV11 VPLLs. Mode load protects VGA output, programs PLL/RAMDAC state, resets PVIDEO and limits, restores extended CRTC, palette, and VGA registers, waits for retrace before some GF4 register writes, then unprotects VGA.

## State and Persistence Behavior
The file serializes hardware state into `struct nv04_mode_state` and `struct nv04_crtc_reg`, including PLL coefficients, palette bytes, cursor config, TV timings, FP timings, CTV registers, and saved framebuffer start offsets. It mutates hardware registers directly and persists VGA fonts in `nv04_display.saved_vga_font`.

## Dependencies and Integration Points
It depends on `nvif_rd/wr` MMIO helpers, NVIF timer waits, VBIOS PLL parsing, Nouveau clock PLL programming, `nv04_display` state, PCI config access, and register constants from `nvreg.h`. CRTC, DFP, TV, cursor, and display lifecycle code call these helpers during modeset, save/restore, suspend, and unload.

## Risks
This code touches many undocumented registers and contains chipset-specific ordering requirements; wrong ordering can lock hardware. Palette and font access require VGA attribute flip-flop handling and correct head ownership. PLL decode can return zero clocks if called before coefficients are valid. VGA font mapping assumes BAR/resource layout and text mode. PVIDEO reset during state load can disrupt overlay state if sequencing changes.

## Test Signals
Signals include register save/load round trips, text-console font preservation, dual-head owner switching, suspend/resume on NV11/NV30/NV40, PLL clock reporting versus expected VBIOS limits, palette restore, overlay disable after modeset, and stress around GF4 retrace waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/hw.c -->
