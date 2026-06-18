# sources/distributed-fs/ceph-client/drivers/virt/coco/guest/report.c

## Purpose
Implements the common TSM attestation report configfs frontend. It lets userspace create `configfs/tsm/report/<item>` instances, write report parameters and an input blob, and read provider-generated report, aux, or manifest blobs.

## APIs, Types, and Functions
Exports `tsm_report_register()` and `tsm_report_unregister()`. Core types are global `provider` (`ops`, private data, active item count) and per-item `struct tsm_report_state` wrapping `struct tsm_report`. Store/read handlers cover `privlevel`, `privlevel_floor`, `service_provider`, `service_guid`, `service_manifest_version`, `inblob`, `generation`, `provider`, `outblob`, `auxblob`, and `manifestblob`.

## Control Flow and State
Module init registers configfs subsystem `tsm` and default group `report`. Providers register one active `struct tsm_report_ops`; registration is rejected when another provider is active or configfs items already exist. Each write takes `tsm_rwsem` for write, advances `write_generation`, and mutates the descriptor. Reads first try a cached report under read lock; if stale, the slow path takes write lock, clears old blobs, calls `ops->report_new()`, updates `read_generation`, and copies requested blob data. Visibility callbacks defer attribute exposure to the active provider.

## Dependencies and Integration
Depends on configfs, shared `linux/tsm.h`, provider modules such as SEV, TDX, and Arm CCA, and cleanup guard macros.

## Risks and Test Signals
Risks include provider unregister while items exist, generation counter wrap guard, stale cached blobs, input blob length validation delegated to providers, and attribute visibility changing with provider state. Tests should cover no-provider errors, concurrent reads/writes, repeated configfs items, provider conflict, unregister with items present, and provider-specific visibility matrices.
