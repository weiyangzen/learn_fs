<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uoutp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uoutp.c

## Purpose

`uoutp.c` exposes display output paths to NVIF clients. It implements methods for acquire/release/inherit, detection/EDID/load detect, backlight, LVDS state, HDMI/SCDC/infoframes/audio, HDA ELD, and DisplayPort AUX/link training/MST programming.

## Important APIs, Types, And Functions

DP methods include `nvkm_uoutp_mthd_dp_aux_pwr()`, `_aux_xfer()`, `_rates()`, `_train()`, `_drive()`, `_sst()`, `_mst_id_get()`, `_mst_id_put()`, and `_mst_vcpi()`. HDMI/audio methods include `nvkm_uoutp_mthd_hdmi()`, `_infoframe()`, and `_hda_eld()`. Output ownership methods include `nvkm_uoutp_mthd_acquire()`, `_release()`, `_inherit()`, and `_acquired()`. Detection helpers include `_detect()`, `_edid_get()`, and `_load_detect()`. `nvkm_uoutp_new()` maps requested output id to an output object and returns capabilities.

## Control Flow

Userspace opens an output, optionally inherits a firmware route or acquires an IOR, then issues protocol-specific methods. Many methods require `outp->ior` and validate the target head. DP training stores DPCD/LTTPR/link parameters into `outp->dp.lt` before invoking the backend train hook. HDMI disable clears infoframes and control before returning. HDA ELD toggles DP or HDMI audio and HDA HPD/ELD state. Release calls the output function's release hook and updates routing.

## State And Persistence Behavior

The file mutates `outp->acquired`, `outp->ior`, `outp->asy.head`, LVDS dual/bpc flags, cached DP DPCD/rates/LT state, MST IDs, AUX power, and audio/ELD hardware state through IOR hooks. The user object is embedded and single-open like other display child objects.

## Dependencies And Integration Points

It depends on output generic functions, DP helpers, head lookup, I2C/AUX backends, IOR HDMI/DP/HDA hooks, and NVIF output ABI structures. It is the main bridge between DRM userspace display management and nvkm display backend functions.

## Risks And Edge Cases

Most methods trust that acquire/inherit established `outp->ior`; callers must not issue acquired-only methods first. ABI size/version checks prevent struct drift. HDA ELD payload is capped at 0x60 bytes. DP rates are capped to the fixed output array. Infoframe sizes derive from `argc - sizeof(*args)` and must only be passed to generation hooks that support the requested type.

## Test Signals

Useful tests cover acquire/release on DAC/SOR/PIOR, inherit from firmware modes, EDID and load detection, backlight get/set, LVDS dual-link flags, HDMI enable/disable/infoframes/SCDC, HDA ELD hotplug, DP AUX transfers, training retries, SST timing, MST ID allocation, and VCPI programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uoutp.c -->
