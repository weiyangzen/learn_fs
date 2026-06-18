# sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_api.h

## Purpose

`scsi_transport_api.h` is a tiny internal transport-facing declaration header. It exposes `scsi_schedule_eh()` to transport code without including a broader private SCSI core header.

## Important APIs, types, and functions

The sole declaration is `void scsi_schedule_eh(struct Scsi_Host *shost);`, which schedules SCSI error handling for a host. The header relies on `struct Scsi_Host` being declared before use or by the including context.

## Control flow

The header has no runtime flow. Transport implementations include it and call `scsi_schedule_eh()` when a transport-level condition requires host error handling.

## State and persistence behavior

No state is owned here. Calls to the declared function affect host error-handler scheduling state in the SCSI core implementation.

## Dependencies and integration points

It integrates with transport code such as libsas, where `sas_scsi_host.c` calls `scsi_schedule_eh(ha->shost)`. It avoids exposing all of `scsi_priv.h` to transport users that only need this one hook.

## Risks and edge cases

Because the header does not include the definition or forward declaration of `struct Scsi_Host`, include ordering matters unless callers already have the type from SCSI host headers. Any signature change must be coordinated with the implementation and all transport callers.

## Test signals

Compile transport users that include this header, especially SAS/libsas. Runtime tests should induce transport errors that call `scsi_schedule_eh()` and confirm the host error handler runs.
