<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_fs_info.go -->
# sources/cloud-native/cri-o/server/image_fs_info.go

## Purpose

This file implements CRI image filesystem usage reporting for image and container storage roots.

## Important APIs, Types, and Functions

`ImageFsInfo` retrieves the storage image server store and calls `getStorageFsInfo`. `getStorageFsInfo(store)` determines graph and image paths and returns CRI filesystem usage entries. `getUsage(containerPath)` calls `utils.GetDiskUsageStats` and wraps bytes/inodes in CRI types.

## Control Flow

When `store.ImageStore()` is empty, graph root is treated as shared image/container storage under `<graphRoot>/<driver>-images`, and the same usage is returned for both image and container filesystems. When image store is separate, container usage is read from `<graphRoot>/<driver>-containers` and image usage from `<imageStore>/<driver>-images`.

## State and Persistence Behavior

The code reads filesystem usage stats and current time only. It does not mutate storage.

## Dependencies and Integration Points

It depends on containers/storage `Store`, CRI `ImageFsInfoResponse`, and CRI-O utility disk usage stats.

## Risks and Edge Cases

Path construction assumes driver-specific directory names. Missing or inaccessible directories return errors. Timestamps are generated per `getUsage`, so image and container entries can have slightly different times.

## Test Signals

Tests cover successful shared graph root usage and failure on invalid image directory. Separate image store behavior is not covered in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_fs_info.go -->
