<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_debugfs.c

## Purpose

`xe_tile_debugfs.c` creates per-tile debugfs directories and reusable show callbacks for tile-specific debugfs files.

## Important APIs, Types, and Functions

`xe_tile_debugfs_simple_show()` resolves the tile from the parent dentry private pointer and invokes a printer function stored in `drm_info_list.data`. `xe_tile_debugfs_show_with_rpm()` wraps the simple show with runtime PM. `xe_tile_debugfs_register()` creates `tileN`, stores the tile pointer, adds VF-safe `ggtt` and `sa_info` files, and creates `vram_mm` resource-manager debugfs when VRAM exists.

## Control Flow

Debugfs registration runs per tile. File reads resolve `drm_info_node`, parent dentry, tile, and printer callback, then emit through a DRM seq-file printer.

## State and Persistence Behavior

`tile->debugfs` stores the directory dentry, and its inode private pointer stores the tile. Debugfs entries reflect live GGTT, suballocator, and TTM manager state.

## Dependencies and Integration Points

The file depends on Linux debugfs, DRM debugfs helpers, runtime PM, GGTT dump, suballocator dump, and TTM VRAM manager debugfs.

## Risks and Test Signals

Risks include dentry private pointer assumptions, missing runtime PM for future files that need hardware access, and debugfs creation errors being silently ignored. Tests should cover directory layout, file read callbacks, VF-safe file presence, and RPM acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_debugfs.c -->
