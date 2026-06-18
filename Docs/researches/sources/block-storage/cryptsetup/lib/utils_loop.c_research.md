# File Research: sources/block-storage/cryptsetup/lib/utils_loop.c

## Purpose
Implements loopback block-device helpers for regular-file-backed cryptsetup devices.

## Key Responsibilities
- Finds free loop devices through `/dev/loop-control`, falling back to scanning `/dev/loop0..255`.
- Attaches files to loop devices with `LOOP_CONFIGURE` when available.
- Falls back to older `LOOP_SET_FD` and `LOOP_SET_STATUS64`.
- Supports autoclear, read-only fallback, offset, and optional block-size setting.
- Detaches and resizes loop devices.
- Reads loop backing file from sysfs or `LOOP_GET_STATUS64`.
- Detects whether a path is a loop block device.

## Important Details
- Autoclear is verified after attach; failure clears the loop fd.
- The attach path returns an open loop fd so the loop remains alive until close.
- Read-only file attach is retried when write open fails with read-only/access errors.
- Loop-device detection checks block type and major number 7.

## Dependencies
Uses Linux loop ioctls, sysfs, major/minor helpers, and `utils_loop.h`.
