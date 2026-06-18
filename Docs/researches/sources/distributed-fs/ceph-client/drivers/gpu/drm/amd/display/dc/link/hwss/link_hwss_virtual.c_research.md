# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_virtual.c

## Purpose

`link_hwss_virtual.c` provides a minimal no-op link HWSS for virtual links. Virtual streams do not need physical stream/link encoder setup, attribute programming, or link-output disable sequencing.

## Important APIs, Types, And Functions

`virtual_setup_stream_encoder()`, `virtual_setup_stream_attribute()`, and `virtual_reset_stream_encoder()` explicitly ignore `pipe_ctx`. `virtual_disable_link_output()` ignores link/resource/signal. `get_virtual_link_hwss()` returns a static vtable containing only those base operations.

## Control Flow

All operations return immediately. The vtable omits optional extension callbacks and audio callbacks, so callers must only use operations valid for virtual links.

## State And Persistence Behavior

The file does not mutate hardware or persistent software state. It exists to satisfy generic sequencing contracts without programming physical resources.

## Dependencies And Integration Points

It includes `link_hwss_virtual.h`, which includes `core_types.h`. DPMS and HWSS selection can use this vtable for virtual signal paths, while DPMS also has early returns for virtual streams.

## Risks And Edge Cases

If a caller assumes optional vtable members exist for a virtual link, it will dereference null function pointers. The no-op behavior also means any required virtual metadata must be handled outside this HWSS layer.

## Test Signals

Virtual display enable/disable should complete without physical encoder programming, DPCD/AUX activity, or audio packet operations. Build coverage catches vtable layout drift.
