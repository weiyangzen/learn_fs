# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_legacy.h

Purpose: `sh_css_legacy.h` preserves legacy CSS pipe identifiers and API entry points used by older AtomISP host code. It distinguishes legacy pipe roles and carries extra pipe configuration knobs that are not represented directly in the newer public pipe config.

Important APIs/types/functions: `enum ia_css_pipe_id` defines preview, copy, video, capture, YUVPP, and count values. `struct ia_css_pipe_extra_config` carries booleans for raw binning, YUV downscaling, high speed, DVS 6-axis, reduced pipe, fractional downscaling, and disabling VF post-processing. Declared functions include `ia_css_pipe_create_extra()`, `ia_css_pipe_extra_config_defaults()`, `ia_css_temp_pipe_to_pipe_id()`, deprecated `sh_css_set_black_frame()`, and ISP2400 `sh_css_enable_cont_capt()`.

Control flow and state: this header is declarative. The pipe ID enum is used as an array index and must match `IA_CSS_PIPE_ID_NUM` expectations in internal pipeline state. Extra config is passed at pipe creation to influence binary selection and pipeline construction.

Dependencies and integration: it includes CSS public frame, pipe, stream, type, and error headers. `sh_css_internal.h` depends on this enum for `NR_OF_PIPELINES`, pipeline arrays, and queue/event mask sizes. `sh_css_params.c` implements `sh_css_set_black_frame()` and uses pipe IDs for per-pipe DVS and parameter maps.

Risks: enum order is ABI-like inside this driver because arrays are indexed by pipe ID and firmware-visible structures use related constants. Legacy functions can still mutate modern stream state, especially black-frame/FPN configuration. Extra config booleans are loosely typed and can encode invalid combinations that later binary selection rejects.

Test signals: tests should cover default extra config values, mapping temporary pipes to legacy IDs, pipe creation for each mode, and deprecated black-frame behavior when FPN is enabled or disabled. Compile-time checks should keep `NR_OF_PIPELINES` aligned with `IA_CSS_PIPE_ID_NUM`.
