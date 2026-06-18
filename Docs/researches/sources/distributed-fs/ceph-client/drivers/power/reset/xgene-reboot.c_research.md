# sources/distributed-fs/ceph-client/drivers/power/reset/xgene-reboot.c

## Purpose
AppliedMicro X-Gene MMIO reboot driver.

## Important APIs, Types, and Functions
`struct xgene_reboot_context`, restart sys-off handler, and platform probe.

## Control Flow
probe allocates context, maps CSR resource, reads optional `mask` defaulting to all bits, and registers restart; callback writes mask and delays/warns.

## State and Persistence Behavior
context is devm-managed; CSR write persists until reset.

## Dependencies and Integration Points
ARM64 X-Gene, OF platform resources, sys-off restart.

## Risks and Edge Cases
mask property must match hardware; no reset completion detection; only restart, not shutdown.

## Test Signals
DT mask values, mapping failure, restart register trace, and reboot.
