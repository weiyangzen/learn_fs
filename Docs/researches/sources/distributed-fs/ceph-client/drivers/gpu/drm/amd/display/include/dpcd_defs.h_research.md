# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/dpcd_defs.h

Purpose: supplies AMD display-local DPCD constants and enums not yet available, or historically duplicated, from DRM DP helper headers. It covers panel replay, PSR, link/audio test patterns, source-specific DPCD locations, and LTTPR count.

Important APIs and control flow: guarded `#ifndef` defines add panel replay capability/configuration/granularity/error/status bits, sink hardware revision, and `DP_TOTAL_LTTPR_CNT` when missing upstream. Enums define DPCD revisions, downstream port types, link test patterns, test color formats/bit depths/dynamic range, PHY test patterns including 128b/132b and PRBS variants, audio test pattern/rate/channel/period values, training pattern encodings including TPS4 and 128b/132b CDS, and PSR sink states. Source/sink DPCD offsets cover source sequence/table/payload/sink cap, backlight, DRR granularity, minimum hblank, panel replay status/deviation/emission/frame skip.

State and persistence behavior: no state. Constants are used as protocol register addresses and values in AUX transactions; compatibility depends on matching the DisplayPort/eDP specifications and DRM helper definitions.

Dependencies and integration points: includes `<drm/display/drm_dp_helper.h>` and supplements it conditionally. Used by link training, compliance test, audio test, PSR, Panel Replay, backlight, LTTPR, and AUX read/write code.

Risks and test signals: risks include local definitions diverging from upstream DRM helpers, enum values needing exact DPCD encodings, new helper definitions changing conditional coverage, and protocol code assuming unsupported sink features. Test signals include compile without redefinition warnings across kernel versions, DP/eDP compliance tests selecting correct patterns, PSR/Panel Replay AUX transactions to expected offsets, audio test pattern handling, and LTTPR count reads at `0xF000A`.
