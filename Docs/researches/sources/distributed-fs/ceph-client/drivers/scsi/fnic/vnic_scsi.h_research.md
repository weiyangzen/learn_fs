# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_scsi.h

## Purpose

`vnic_scsi.h` defines FNIC-specific vNIC SCSI configuration limits, defaults, feature flags, and the device-specific FC configuration structure read from firmware/device-specific space.

## Important APIs, types, and data

- `VNIC_FNIC_*` constants bound WQ, copy WQ, RQ, timer, retry, timeout, max data field size, IO throttle, link-down, port-down, LUN, and queue-depth settings.
- `struct vnic_fc_config` contains WWNs, flags, descriptor counts, FLOGI/PLOGI retry and timeout settings, IO throttle, timeout policies, max data field size, FC timers, interrupt settings, queue depth, and copy-WQ count.
- Feature flags include FCP sequence-level error recovery, persistent binding, FIP capability, FC initiator/target, and FC-NVMe initiator/target roles.

## Control flow

FNIC probe/configuration code reads device-specific values into `struct vnic_fc_config`, validates them against the min/max constants, and uses them to size queues and configure FC behavior.

## State and persistence behavior

The structure is configuration state obtained from firmware and then used by the driver at runtime. The header itself owns no mutable state.

## Dependencies and integration points

It integrates `vnic_dev_spec()`/firmware configuration with FNIC queue allocation, libfc/libfcoe behavior, and SCSI host settings.

## Risks and edge cases

- Invalid firmware values must be clamped or rejected by consumers; this header only declares bounds.
- `VNIC_FNIC_FLOGI_RETRIES_DEF` is unlimited (`0xffffffff`), so retry logic must avoid unbounded blocking behavior.
- Feature flags include roles that may not be supported by the rest of this FNIC code path.

## Test signals

Configuration tests should cover boundary values for descriptor counts, timers, retries, max frame size, queue depth, and role/feature flags.
