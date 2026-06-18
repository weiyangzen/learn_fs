<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_debugfs.h

## Purpose

`xe_tile_debugfs.h` declares the per-tile debugfs registration and reusable show callbacks.

## Important APIs, Types, and Functions

It exposes `xe_tile_debugfs_register()`, `xe_tile_debugfs_simple_show()`, and `xe_tile_debugfs_show_with_rpm()`.

## Control Flow

Tile debugfs setup calls register. Other tile-specific debugfs providers reuse the show callbacks with `drm_info_list.data` set to tile printer functions.

## State and Persistence Behavior

The functions operate on tile debugfs dentries and live tile state, but the header owns none.

## Dependencies and Integration Points

It forward-declares `seq_file` and `xe_tile`. It is reused by core tile debugfs and SR-IOV PF tile debugfs.

## Risks and Test Signals

Consumers must set dentry private data as expected by the implementation. Tests should read representative debugfs files and verify correct tile selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_debugfs.h -->
