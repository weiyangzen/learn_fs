<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile.h

## Purpose

`xe_tile.h` declares tile initialization and utility helpers.

## Important APIs, Types, and Functions

It exposes early/noalloc/full tile init, VRAM allocation, migration wait, root-tile check, `xe_tile_to_vr()`, and config-dependent `xe_tile_local_pagemap()`.

## Control Flow

Device probe and teardown use these APIs in staged order. SVM and migration code use local pagemap and migration wait helpers.

## State and Persistence Behavior

The APIs operate on persistent `struct xe_tile` state defined in `xe_tile_types.h`.

## Dependencies and Integration Points

It includes tile types and forward-declares device/pagemap types. It is consumed by probe, SVM, migration, debugfs, and platform setup code.

## Risks and Test Signals

Callers must not use full init before required allocation/noalloc stages. Build tests should cover pagemap enabled and disabled branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile.h -->
