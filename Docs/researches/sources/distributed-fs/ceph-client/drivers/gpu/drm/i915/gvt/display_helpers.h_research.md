# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/display_helpers.h

Purpose: provides small compatibility wrappers between GVT code and i915 display-device MMIO offset helpers.

Important APIs/types/functions: macros wrap `intel_display_device_mmio_base()`, `intel_display_device_pipe_offset()`, `intel_display_device_trans_offset()`, and `intel_display_device_cursor_offset()`. `gvt_for_each_pipe(display, __p)` iterates only valid pipes according to `intel_display_device_pipe_valid()`.

Control flow and state: no persistent state. The pipe iteration macro expands to a nested `for` plus `for_each_if` filter. A documented FIXME notes that some GVT callers pass transcoders to pipe-based addressing, currently cast to `enum pipe` because `TRANSCODER_A..D` map one-to-one with `PIPE_A..D`; `TRANSCODER_EDP` remains a caveat.

Dependencies and integration points: depends on `display/intel_gvt_api.h` and is used by GVT display and command parser code that needs platform-correct display offsets.

Risks and test signals: the transcoder-to-pipe cast is a known correctness risk for eDP or future display topologies. Test signals include display emulation on platforms with varying valid pipe masks, no out-of-range virtual register accesses, and review of any new TRANSCODER_EDP usage.
