# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/core.c

## Purpose
Implements the Marvell MMP display subsystem core registry. It tracks display paths and panels, matches them by platform path name, initializes path overlays, and exports lookup/register/unregister APIs used by hardware controller, panel, and framebuffer drivers.

## Important APIs, Types, and Functions
- `panel_list`, `path_list`, and `disp_lock` are the global registry state.
- `path_get_overlay()`, `path_check_status()`, and `path_get_modelist()` are default path operations.
- `mmp_register_panel()` and `mmp_unregister_panel()` manage panel list membership and path binding.
- `mmp_get_path()` finds a registered path by name for framebuffer drivers.
- `mmp_register_path()` allocates a flexible `struct mmp_path`, copies platform information, matches an existing panel, initializes overlay objects, and adds it to `path_list`.
- `mmp_unregister_path()` removes and frees a path.

## Control Flow
Hardware controller drivers register paths with `mmp_register_path()`. Panel drivers independently register panels with `mmp_register_panel()`. Both registration flows search the opposite list by name to connect `path->panel`. Framebuffer drivers later call `mmp_get_path()` and `mmp_path_get_overlay()` to access the registered hardware path and overlay.

## State and Persistence
Path and panel registration state persists in global lists protected by `disp_lock`. Each path owns overlay objects and per-path/overlay mutexes until unregister. No persistent storage exists beyond memory.

## Dependencies and Integration Points
Uses public display types from `<video/mmp_disp.h>`, Linux lists, mutexes, module exports, and dynamic allocation. Exports are consumed by `mmp_ctrl.c`, `mmpfb.c`, and panel drivers such as `tpo_tj032md01bw.c`.

## Risks
Name matching with `strcmp()` is the only binding mechanism; platform data mismatch leaves components disconnected. `mmp_get_path()` returns a pointer after releasing `disp_lock`, so callers rely on platform lifetime ordering to avoid unregister races. `mmp_unregister_path()` does not disconnect a panel pointer explicitly before freeing. `mmp_register_path()` returns NULL on allocation failure but some callers treat zero as generic failure.

## Test Signals
Test panel-before-path and path-before-panel registration orders, path lookup by name, overlay count and ID initialization, unregister cleanup, and behavior when names do not match. Module symbol consumers should load in arbitrary order without crashing.
