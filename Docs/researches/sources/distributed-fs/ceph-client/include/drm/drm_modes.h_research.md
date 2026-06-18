# sources/distributed-fs/ceph-client/include/drm/drm_modes.h

Purpose: declares DRM display mode representation, mode status codes, mode construction macros, timing conversion helpers, mode validation/comparison APIs, command-line mode parsing, and OF videomode conversion hooks.

Important APIs and types: `enum drm_mode_status` enumerates reasons a mode is unsupported, including sync limits, timing errors, memory limits, interlace/doublescan restrictions, YCbCr 4:2:0 restrictions, stale/bad/error states. `struct drm_display_mode` stores logical timings, adjusted CRTC timings, sync/3D flags, physical size, type flags, exposure flag, list node, name, validation status, and HDMI picture aspect ratio. Macros include `DRM_MODE`, `DRM_MODE_INIT`, `DRM_SIMPLE_MODE`, CRTC adjustment flags, match flags, `DRM_MODE_FMT`, and `DRM_MODE_ARG`. APIs allocate/destroy/duplicate/copy modes, convert to/from UAPI and `videomode`, add probed modes, create CVT/GTF/analog TV modes, set names, compute refresh and hv timing, set CRTC info, compare modes, validate modes, prune/sort mode lists, update connector lists, and parse command-line modes.

Control flow: drivers and helpers create modes from EDID, firmware, OF data, command line, or fixed panels, validate them through device/CRTC/encoder/connector constraints, set adjusted CRTC timings, expose accepted modes to userspace, and later convert selected modes to UAPI or hardware state.

State and persistence behavior: mode objects are list-managed and normally owned by connectors or temporary atomic state. The `status` field records validation result; `expose_to_userspace` is used while preparing GETCONNECTOR output. Hardware-adjusted fields are derived from logical timings and adjustment flags.

Dependencies and integration points: includes HDMI aspect definitions, mode objects, connectors/display info, OF display timings, and videomode conversion. It is central to probe helpers, atomic checks, panel drivers, bridge drivers, and command-line mode handling.

Risks: logical and CRTC-adjusted timings can diverge for interlace, doublescan, stereo, or clock-doubling; drivers must program the right copy. Mode comparison flags determine whether clocks, flags, 3D layout, and aspect ratio matter. Command-line or user-defined modes can bypass connector probed lists, so source hardware limits must be enforced elsewhere.

Test signals: EDID/probed mode creation, CVT/GTF generation, analog TV helpers, OF videomode parsing, mode name/refresh calculations, CRTC timing adjustment flags, YCbCr 4:2:0 validation, prune/sort behavior, command-line parsing, and equality/match variants.
