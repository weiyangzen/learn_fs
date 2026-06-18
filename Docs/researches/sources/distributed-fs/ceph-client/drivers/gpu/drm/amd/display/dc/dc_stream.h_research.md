# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_stream.h

## Purpose
`dc_stream.h` defines the DC stream state object and the public stream update/control API. A stream represents one display timing/output path with sink/link association, timing, color, info packets, audio, writeback, cursor, VRR/FreeSync, DSC, dynamic metadata, and commit/update state.

## Important APIs, Types, And Data Contracts
`struct dc_stream_state` is the central state container. It stores sink/link/link encoder, timing and timing adjustments, HDMI/DP info packets, DSC PPS, source/destination rectangles, audio info, HDR/dynamic metadata, transfer functions, color space, dither, view format, FreeSync/VRR flags, ABM level, context pointer, bit-depth/clamping, signal, DPMS, cursor attributes/position, kref, writeback info, boot optimization flags, stream id, test pattern, update flags, SubVP/phantom markers, luminance data, sharpening flags, DRR trigger mode, and update scratch.

`struct dc_stream_status` describes committed resource assignment: OTG, stream encoder, plane list/count, audio instance, timing sync group, ABM support, MALL/SubVP config, and FPO state. `struct dc_stream_update` is a pointer-based partial update descriptor for stream updates. `union stream_update_flags` tracks which stream properties changed.

Major APIs include stream comparison, `dc_update_planes_and_stream` and its prepare/execute/cleanup split, `dc_commit_updates_for_stream`, stream logging/current stream lookup, vblank counter and scanout position, DP SDP send, writeback add/remove/disable, DSC resource addition, dynamic metadata status/set, stream validation, stereo/sync trigger, surface update checking, stream create/copy/update signal, retain/release/status access, cursor check/set/program functions, VRR vmin/vmax adjustment, CRC functions, static-screen/dither/gamut/CSC helpers, 3DLUT allocation/release/init, pipe context lookup, DMUB dirty rect update, and cursor-limit queries.

## Control Flow And State
The stream update flow can be monolithic via `dc_update_planes_and_stream` or split into scratch init, locked prepare, unlocked execute, and locked cleanup. Stream objects are reference-counted with `kref`. Partial updates use pointer fields: a null pointer means no update for that property, while a non-null pointer supplies a new value. Committed resource status is retrieved through stream status helpers and current DC state.

## Dependencies And Integration Points
It includes `dc_types.h` and `grph_object_defs.h`, and it depends on many DC core types. It integrates with atomic commit, resource validation, hardware sequencing, link/MST/DSC code, color management, cursor programming, writeback, CRC/secure display, DMUB dirty rectangles, FreeSync/DRR, SubVP/MALL, and display manager state.

## Risks
The stream struct is broad and long-lived; partial updates must carefully distinguish null/no-change from pointer-to-new-value. Reference-count errors can leak or free active streams. Deprecated `sink` pointer should not be used by new code. Dynamic link encoder assignment must use volatile state rather than static link fields. Cursor and SubVP flags interact and can block power-saving paths. Writeback arrays are bounded by `MAX_DWB_PIPES`, and plane arrays by `MAX_SURFACES`.

## Test Signals
Atomic stream create/copy/release, stream update prepare/execute/cleanup, cursor set/program, VRR/DRR adjustments, DSC resource add, MST bandwidth update, dynamic metadata, writeback add/remove, CRC read/configure, 3DLUT lifecycle, SubVP/phantom stream interactions, and current-stream status queries are key signals.
