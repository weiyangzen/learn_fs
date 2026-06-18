# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_parser.h

This header exposes the HFI parser and inline capability lookup helpers. It is the small public interface used by decoder, encoder, and PM paths to query per-instance firmware/platform capability bounds.

The exported function is `hfi_parser(struct venus_core *core, struct venus_inst *inst, void *buf, u32 size)`. Inline APIs include `get_cap()`, `cap_min()`, `cap_max()`, `cap_step()`, and domain-specific helpers such as `frame_width_min()`, `frame_width_max()`, `frame_height_step()`, `frate_max()`, `core_num_max()`, and `mbs_per_frame_max()`.

Control flow in the inlines is simple: `get_cap()` resolves the `hfi_plat_caps` entry for the instance codec/session via `venus_caps_by_codec()`, scans its capability array for the requested HFI capability type, and returns the requested min/max/step field. Callers use these helpers during format clamping, frame-size enumeration, PM core routing, and buffer size estimation.

The header does not own persistent state; it reads `inst->core`, `inst->hfi_codec`, `inst->session_type`, and `core->caps`. Dependencies include `core.h` and the HFI capability constants. Integration points are broad because these helpers are the main bridge from parsed capabilities to V4L2 user-visible constraints.

Risks are silent zero fallback and stale capability state. If parsing failed or the codec/domain is not found, helpers return zero, which can cause invalid clamp ranges or route decisions if callers do not validate session initialization. Test signals include sane `VIDIOC_ENUM_FRAMESIZES`, format try/set clamping, and PM routing with max video core capability on multi-core platforms.
