# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_types.h

## Purpose
`dc_types.h` is the broad public type surface for AMD DC. It aggregates EDID/audio/timing/power/scaling/color/writeback/PSR/Replay/panel/USB4/backlight/validation/color-management types used by display manager and DC internals. It is a contract header rather than an implementation unit.

## Important APIs, Types, And Data Contracts
Environment and status enums include `enum dce_environment`, `enum dc_edid_status`, `enum act_return_status`, power states, connection types, validation modes, endpoint types, panel types, and backlight control types.

EDID/audio contracts include `struct dc_edid`, `struct dc_edid_caps`, `struct dc_cea_audio_mode`, `struct audio_mode`, `struct audio_info`, audio sample/speaker flags, info packet structs, and EDID read policy. Timing/mode contracts include `struct dc_mode_info`, `struct dc_mode_flags`, timing source enums, scaling transformations, 3D/stereo formats, content type, and writeback parameters.

PSR and Replay contracts include `struct psr_config`, `union dmcu_psr_level`, `struct psr_context`, `struct psr_settings`, Replay config/settings enums/unions, and panel config sections for power sequencing, brightness, PSR/Replay, ABM, eDP DSC, ILR, adaptive VariBright, and RIO.

Link and platform contracts include `struct dc_context`, ASIC IDs, clock config, DPCD-decoded DSC caps, golden table, GPU memory allocation type, link encoding format, endpoint id, link status, HDCP caps, MST stream allocation tables, DPIA bandwidth allocation, HPD enable selection, backlight params, validation DPIA set, and create/commit params.

Color-management contracts include CM2 GPU memory formats/layouts/sizes, transfer function sources, 3DLUT/shaper config, component settings, and legacy CM LUT enums.

## Control Flow And State
This header has no executable flow. Its structures are stored across DC context, stream state, link state, panel config, validation inputs, and display-manager-owned objects. Several fields are persistent knobs or status caches, such as `dc_context`, `psr_settings`, `replay_settings`, and `dc_panel_config`.

## Dependencies And Integration Points
It includes core low-level headers such as `os_types.h`, `fixed31_32.h`, `irq_types.h`, DDC/DP/HDMI/HW type headers, DAL graphics object definitions, and PSP content-protection types. It is included across DC, DM, link, resource, color, audio, writeback, PSR, Replay, and validation code.

## Risks
Because this is a wide shared contract, enum renumbering or struct layout changes can have broad compile and runtime impact. Many fields have implicit units: millinits, 100 Hz pixel clock precision, fixed-point formats, microhertz refresh, x16 DSC bpp, and bandwidth in kbps/Mbps/PBN. Some comments mark deprecated or temporary fields, such as stream `sink` use in other headers. Global context fields expose service pointers whose lifetime is owned elsewhere.

## Test Signals
Broad build coverage is essential. Runtime signals include EDID/audio parsing, timing validation, color and gamut updates, PSR/Replay state transitions, USB4 DPIA bandwidth allocation, backlight control by PWM/AUX, MST allocation, HDCP capability reads, validation mode variants, CM2 LUT programming, and power-source-dependent commits.
