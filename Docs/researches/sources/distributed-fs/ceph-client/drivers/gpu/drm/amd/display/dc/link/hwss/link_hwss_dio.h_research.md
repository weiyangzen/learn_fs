# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio.h

## Purpose

`link_hwss_dio.h` declares the DIO link hardware-sequencing interface used by generic link code and sibling HWSS variants. It exposes the DIO vtable getter, applicability check, stream setup/reset/attribute routines, DP link output and training helpers, audio helpers, and MST allocation update hook.

## Important APIs, Types, And Functions

The header declares `get_dio_link_hwss()`, `can_use_dio_link_hwss()`, `set_dio_throttled_vcp_size()`, `setup_dio_stream_encoder()`, `reset_dio_stream_encoder()`, `setup_dio_stream_attribute()`, `enable_dio_dp_link_output()`, `disable_dio_link_output()`, `set_dio_dp_link_test_pattern()`, `set_dio_dp_lane_settings()`, `setup_dio_audio_output()`, `enable_dio_audio_packet()`, `disable_dio_audio_packet()`, and `update_dio_stream_allocation_table()`. It depends on `link_hwss.h` and `link_service.h` for `struct link_hwss`, `struct dc_link`, `struct pipe_ctx`, `struct link_resource`, and DP lane/settings types.

## Control Flow

There is no runtime control flow. The declarations let the base DIO implementation and specialized wrappers share operations. Fixed-VS/PE retimer and DPIA variants call these helpers while overriding selected vtable extension functions.

## State And Persistence Behavior

The header stores no state. All state changes happen in `link_hwss_dio.c` through hardware function pointers and caller-owned `pipe_ctx`, `dc_link`, and `link_resource` objects.

## Dependencies And Integration Points

It is included by DIO HWSS consumers and retimer/DPIA specializations. Signature compatibility with `link_hwss.h` is important because the static vtable in the `.c` file assigns these routines to generic function-pointer slots.

## Risks And Edge Cases

Prototype drift breaks link service dispatch at build time. Because many functions take generic pointers, wrong signal/resource combinations will compile but fail at runtime. The header exposes low-level helpers directly, so specialized HWSS files must preserve DIO ordering assumptions when wrapping them.

## Test Signals

Kernel build coverage catches duplicate declarations, missing types, and signature mismatches. Runtime coverage is indirect through DIO DP/HDMI/DVI/LVDS link bring-up, MST allocation, audio, and training/test-pattern paths.
