# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_capture.h

## Purpose

`xe_guc_capture.h` declares the GuC capture API and maps Xe/GuC engine classes into GuC capture-list classes.

## Important APIs, Types, and Functions

- `xe_guc_class_to_capture_class()` maps GuC render and compute to render/compute capture, GSC other to GSC, and video/blitter classes directly.
- `xe_engine_class_to_guc_capture_class()` composes Xe engine class to GuC class and then to capture class.
- Public functions cover capture processing, ADS list retrieval and sizing, null list retrieval, worst-case ADS sizing, descriptor list lookup, matching/locking output nodes, manual capture, snapshot printing/capture, steered-list initialization, matched-node cleanup, and capture init.

## Control Flow

GuC init calls capture init, ADS calls list sizing/retrieval, CT event handling calls `xe_guc_capture_process()`, and devcoredump/snapshot paths call matching, manual capture, printing, and cleanup helpers.

## State and Persistence Behavior

The header exposes opaque parsed-output pointers and operates on `struct xe_guc`, `struct xe_exec_queue`, and hardware engine snapshots. Actual state lives in `guc->capture`.

## Dependencies and Integration Points

It includes GuC capture/scheduler ABI and `xe_guc.h`, so it connects firmware class constants, Xe engine classes, ADS, CT event handling, and devcoredump reporting.

## Risks and Edge Cases

Invalid engine classes warn and return `GUC_CAPTURE_LIST_CLASS_MAX`; callers must not use that as a real class. The API exposes internal parsed-output pointers, making lifetime rules important for callers that lock and later release matched nodes.

## Test Signals

Tests should verify class mapping, invalid-class handling, ADS list calls for every owner/type/class combination, and matched-node lock/release lifetimes through devcoredump flows.
