# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/cursor_reg_cache.h

## Purpose

`cursor_reg_cache.h` defines packed software mirrors for HUBP and DPP cursor registers. These caches support cursor position/attribute programming and cursor offload paths without repeatedly reconstructing register bitfields.

## Important APIs, Types, And Functions

Important types include `reg_cursor_control_cfg`, `cursor_position_cache_hubp`, `cursor_attribute_cache_hubp`, `cursor_rect`, `reg_cur0_control_cfg`, `cursor_position_cache_dpp`, `cursor_attribute_cache_dpp`, and `cursor_attributes_cfg`. Bitfields cover enable flags, magnification, mode, pitch, lines per chunk, position, hotspot, destination offsets, surface addresses, size, settings, expansion mode, ROM enable, and FP scale/bias.

## Control Flow

HUBP and DPP cursor functions update cache structures alongside hardware programming. Offload/update paths can compare or reuse cached control, position, hotspot, size, address, and scale/bias values while coordinating HUBP memory fetch and DPP composition state.

## State And Persistence Behavior

The caches are embedded in `struct hubp` and `struct dpp`, persisting for the hardware object lifetime. They are software mirrors only; hardware persistence occurs through later register writes.

## Dependencies And Integration Points

The header is included by `hubp.h` and `dpp.h`. It integrates with cursor attribute/position APIs, cursor offload, HUBP surface address programming, DPP cursor matrix/scale programming, and HWSS cursor update functions.

## Risks And Edge Cases

Bitfield layout must match register definitions and compiler assumptions. Cached values can become stale after hardware reset, power gating, or direct register writes outside the cache path. Width-limited fields such as 13-bit destination offset and 16-bit position/size require caller validation.

## Test Signals

Tests should cover cursor enable/disable, movement, hotspot changes, large coordinates, pitch/line-per-chunk modes, FP scale/bias programming, offload abort/commit, power-gate resume, and hardware readback consistency. Visible cursor corruption or lag indicates cache/register mismatch.
