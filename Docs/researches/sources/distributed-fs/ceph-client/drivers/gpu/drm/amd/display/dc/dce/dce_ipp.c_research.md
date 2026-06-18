# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_ipp.c

Purpose: implements DCE input pixel processor callbacks for hardware cursor programming, prescale, legacy input LUT programming, degamma mode selection, construction, and destruction.

Important APIs and functions: `dce_ipp_construct()` installs `dce_ipp_funcs`; optional `dce60_ipp_construct()` installs a SI-specific degamma function; `dce_ipp_destroy()` frees the object. Callback implementations include `dce_ipp_cursor_set_position()`, `dce_ipp_cursor_set_attributes()`, `dce_ipp_program_prescale()`, `dce_ipp_program_input_lut()`, and `dce_ipp_set_degamma()`/`dce60_ipp_set_degamma()`.

Control flow: cursor position locks update registers, toggles enable, writes position and hotspot, then unlocks. Cursor attributes locks, maps cursor format to hardware mode, writes magnification/transparent-clamp flags, programs mono colors when needed, writes width/height as size minus one, writes high address before low address, and unlocks. Prescale first bypasses, writes RGB scale/bias, then enables prescale and bypasses legacy LUT if requested. Input LUT powers LUT memory when available, enables RGB writes, selects 256-entry mode and u0.12 format, streams red/green/blue values from `struct dc_gamma`, powers memory down, bypasses prescale, and enables legacy LUT. Degamma writes graph/cursor degamma modes.

State and persistence: persistent state is register state plus object metadata (`ctx`, `inst`, `regs`, `ipp_shift`, `ipp_mask`). No filesystem persistence. Cursor register locking prevents partial visible updates. LUT programming consumes `gamma->num_entries` without local clamping, so caller-provided table size must match hardware expectations.

Dependencies and integration: depends on `dce_ipp.h`, register helpers, fixed-point rounding through gamma entries, and generic `input_pixel_processor` callbacks used by plane/cursor/color programming.

Risks and test signals: risks include cursor size underflow if width/height are zero, invalid cursor modes falling back after debugger break, address programming order requirements, LUT memory-power polarity, and gamma entry counts exceeding hardware LUT depth. Test cursor formats/positions/hotspots, 4K-aligned cursor addresses above 32 bits, prescale plus LUT interactions, sRGB/bypass degamma, SI builds, and visual gamma/cursor validation after suspend/resume.
