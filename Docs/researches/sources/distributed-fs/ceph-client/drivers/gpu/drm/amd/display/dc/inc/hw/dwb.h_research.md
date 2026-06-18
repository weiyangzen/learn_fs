# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dwb.h

## Purpose

`dwb.h` defines the Display Writeback Controller abstraction. DWB captures a display source, optionally scales/converts it, and writes frames through MCIF writeback buffers for capture, composition, or remote/display features.

## Important APIs, Types, And Functions

Important enums cover software version, source selection, pipe IDs, frame capture enable, scaler filter type, boundary mode, output CSC mode, output gamma LUT mode, color volume, and color space. Key structs include HDR metadata, EFC display settings, warmup params, caps, `dwbc`, and `dwbc_funcs`. Operations include capability query, enable/disable/update, enabled/status query, frame capture enable, scaler/stereo/new-content/warmup programming, MCIF buffer line readback, optional output CSC/OGAM, input transfer function, DRR timestamp, and DWB status.

## Control Flow

Resource/HWSS code assigns a DWB pipe and MCIF buffer, configures source OTG or legacy source, programs scaler/color/stereo/warmup/EFC state from `dc_dwb_params`, enables frame capture, and updates or disables the block on stream changes. MCIF line readback and timestamps support synchronization/debug.

## State And Persistence Behavior

`dwbc` persists per writeback block and stores context, instance, MCIF pointer, enable/status fields, selected input source, output black flag, transfer function, output color space, EFC/DRC flags, source plane/OTG metadata, mask ID, MVC config, and last params. Hardware persists DWB and MCIF programming until disabled or reset.

## Dependencies And Integration Points

It includes DAL and DC hardware types and forward-declares `mcif_wb`. It integrates with `resource_pool`, `dc_writeback_info`, HWSS writeback callbacks, MCIF arbitration/buffer programming, DML writeback bandwidth, and stream/OTG resources.

## Risks And Edge Cases

DWB capabilities vary by version and ASIC. Source selection differs between legacy DCE and DCN values. Output color and transfer functions are conditionally compiled for FP support. MCIF buffer overruns, scaler bounds, HDR/EFC metadata, and DRR timestamps require synchronized programming. Cached `params` can become stale after stream topology changes.

## Test Signals

Tests should cover caps, enable/update/disable, each source type, scaler formats, stereo, output black, warmup pattern, OGAM/CSC paths, MCIF buffer overrun readback, DRR timestamp, and writeback under mode changes. Captured-frame correctness and no overruns are key signals.
