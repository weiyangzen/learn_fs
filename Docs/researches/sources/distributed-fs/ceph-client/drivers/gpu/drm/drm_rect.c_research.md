# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_rect.c

Purpose: provides rectangle math helpers for DRM plane clipping, scaling validation, debug printing, and coordinate transforms for rotation/reflection.

Important APIs/types/functions: `drm_rect_intersect()` clips one rectangle by another. `drm_rect_clip_scaled()` clips destination and adjusts 16.16 source coordinates while preserving scale. `drm_rect_calc_hscale()` and `drm_rect_calc_vscale()` calculate bounded source/destination scale factors through `drm_calc_scale()`. `drm_rect_debug_print()` logs integer or fixed-point rectangles. `drm_rect_rotate()` and `drm_rect_rotate_inv()` transform rectangles through DRM rotation/reflection flags.

Control flow: clipping computes side deltas, maps each destination clip delta to source shrinkage with pessimistic rounding, updates edges, and returns destination visibility. Scale calculation rejects negative dimensions, handles zero destination size, rounds down for upscaling and up for downscaling, then enforces min/max. Rotation applies reflections before rotation; inverse rotation applies inverse rotation before reflections.

State and persistence behavior: all functions are stateless and mutate only caller-provided rectangles.

Dependencies and integration points: used by plane atomic checks, helpers validating scaling limits, and debug output; depends on `drm_rect.h`, DRM mode rotation flags, and DRM debug macros.

Risks: callers must supply dimensions in the expected coordinate space and fixed-point convention. Overflow is mitigated in scaled clipping with 64-bit multiplication, but invalid large/negative rectangles can still trigger warnings or wrong caller behavior. Rotation and inverse rely on valid single rotation flag combinations.

Test signals: intersection visible/invisible cases, scaled clipping at all four edges, upscaling/downscaling rounding boundaries around 1.0, zero-size rectangles, min/max scale rejection, rotate followed by inverse returning original coordinates, and reflection combinations.
