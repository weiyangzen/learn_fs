<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_dh.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_dh.h

## Purpose
This header defines the SCSI device-handler infrastructure used mainly by multipath and special arrays to attach per-device policy for sense checking, activation, request preparation, parameter setting, and rescans.

## Important APIs, Types, And Functions
It defines device-handler result/error codes, `activate_complete`, and `struct scsi_device_handler` with list/module/name fields plus `check_sense`, `attach`, `detach`, `activate`, `prep_fn`, `set_params`, and `rescan` callbacks. If `CONFIG_SCSI_DH` is enabled it declares `scsi_dh_activate()`, `scsi_dh_attach()`, `scsi_dh_attached_handler_name()`, and `scsi_dh_set_params()`. If disabled it provides stubs.

## Control Flow
When enabled, a handler is registered, attached to a request queue/device, can prepare requests, classify sense into retry/fail/activate actions, and can asynchronously activate paths with a completion callback. Disabled builds immediately complete activation successfully but reject attach/parameter operations.

## State And Persistence
Handlers are runtime kernel modules linked on a global list and referenced by `struct scsi_device::handler` plus handler private data. No durable state is owned by the header.

## Dependencies And Integration Points
It includes `scsi_device.h` and integrates with request queues, SCSI sense handling, device state, and multipath/path activation logic.

## Risks
Disabled stubs have mixed semantics: activation succeeds but attachment returns unsupported. Callback completion must be invoked exactly once. Sense classification controls retry/fail behavior, so handler bugs can cause I/O loss or endless retries.

## Test Signals
Build both enabled/disabled configurations, attach/detach handlers, verify activation callback ordering, prep request behavior, sense classification results, parameter parsing, and path rescan interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_dh.h -->
