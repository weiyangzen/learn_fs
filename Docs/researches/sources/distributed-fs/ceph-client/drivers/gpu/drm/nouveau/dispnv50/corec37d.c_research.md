<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/corec37d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/corec37d.c

## Purpose
This file implements the GV100-era core channel behavior for modern window-based display hardware, including window ownership, modern update interlocks, notifier handling, mapped capabilities, and initialization of window usage bounds.

## Important APIs, Types, and Functions
It defines `corec37d_wndw_owner`, `corec37d_update`, `corec37d_ntfy_wait_done`, `corec37d_ntfy_init`, `corec37d_caps_init`, `corec37d_init`, the `corec37d` function table, and `corec37d_new`.

## Control Flow
Init sets the context DMA notifier and programs usage/format bounds for eight windows, then marks `assign_windows` true. Window owner emits ownership for each window, assigning pairs to heads by `i >> 1`. Update optionally enables a notifier, emits cursor and window interlock flags, emits the modern UPDATE method, optionally disables notify, and kicks. Caps init constructs and maps a `GV100_DISP_CAPS` object instead of reading caps through the legacy notifier path. Notifier init/reset writes the modern notifier status and payload fields.

## State and Persistence Behavior
The file persists core channel context DMA, window usage bounds, window ownership, caps object mapping, notifier memory, and the `assign_windows` flag. Update methods synchronize cursor/window interlocks rather than legacy base/overlay interlocks.

## Dependencies and Integration Points
It depends on class `clc37d`, pushc37b macros, NVIF object construction/mapping, `headc37d`, `sorc37d`, optional `crcc37d`, `nv50_dmac` construction via `core507d_new_`, and modern `nv50_wndw`/cursor commit paths.

## Risks
The window count is hard-coded to eight with `XXX` comments; future or smaller hardware can diverge. Window-to-head ownership uses a fixed two-windows-per-head mapping. Caps object map failures need cleanup by higher layers. Usage bounds restrict scaling and format support; wrong values can reject valid commits or allow unsupported fetches.

## Test Signals
GV100/Turing-family init, caps object mapping, window assignment, atomic commits with cursor and window interlocks, notifier completion, multi-head plane distribution, CRC debugfs where enabled, and failure injection for caps construction/mapping validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/corec37d.c -->
