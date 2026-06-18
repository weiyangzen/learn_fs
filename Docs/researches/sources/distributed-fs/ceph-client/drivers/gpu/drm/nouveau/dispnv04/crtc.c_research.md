# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/crtc.c

## Purpose
`crtc.c` implements the legacy NV04 display CRTC path for Nouveau. It is non-atomic KMS code that programs VGA/extended CRTC/RAMDAC state, manages scanout buffer pinning, gamma, hardware cursor upload/positioning, vblank, and push-buffer-driven page flips.

## Important APIs, Types, And Functions
Key mode functions are `nv_crtc_mode_set_vga`, `nv_crtc_mode_set_regs`, `nv_crtc_calc_state_ext`, `nv_crtc_mode_set`, `nv_crtc_prepare`, `nv_crtc_commit`, and `nv04_crtc_mode_set_base`. State save/restore uses `nv_crtc_save` and `nv_crtc_restore`. Display controls include `nv_crtc_dpms`, digital vibrance, image sharpening, gamma load/set, and vblank handler setup. Cursor upload is split between `nv04_cursor_upload` for 16-bit cursor conversion and `nv11_cursor_upload` for ARGB cursor handling. Page flip machinery uses `struct nv04_page_flip_state`, `nv04_page_flip_emit`, `nv04_finish_page_flip`, `nv04_flip_complete`, and `nv04_crtc_page_flip`. `nv04_crtc_create()` allocates the primary plane, CRTC, cursor BO, NVIF head, and vblank event.

## Control Flow, State, And Integration
Mode setting pins the new framebuffer BO, unlocks VGA shadow registers, computes VGA timings, prepares extended mode registers, calculates PLL state, then commit loads the complete mode state and sets base address. Base updates refresh framebuffer format, pitch, start address, gamma if depth changed, and arbitration registers from `nouveau_calc_arb()`. Page flips pin the new BO, synchronize fences, queue flip state under `event_lock`, optionally program swap interval push commands, update display image ownership, emit a software page-flip method, and complete on the NVIF event by setting the CRTC base and arming/sending vblank events.

## State, Dependencies, Risks, And Tests
State spans `nv04_display()->mode_reg/saved_reg/image[]`, `nouveau_crtc` cursor/lut/fb fields, pinned VRAM BO references, VGA CRTC arrays, RAMDAC registers, NVIF head/vblank events, and channel fence flip lists. Dependencies include TTM/GEM BO pinning, Nouveau push/fence/channel code, BIOS PLL parsing, low-level `hw.h`, and `arb.c`. Risks include non-atomic legacy paths, manual refcount/pin lifetime, endian cursor quirks, event/vblank ownership on flip failures, PLL/chipset conditionals, and many undocumented register cargo-cult values. Test signals are legacy modeset, panning, gamma, cursor, DPMS, vblank timestamp, page-flip event, suspend/restore, and multi-head tests on NV04-NV4x cards.
