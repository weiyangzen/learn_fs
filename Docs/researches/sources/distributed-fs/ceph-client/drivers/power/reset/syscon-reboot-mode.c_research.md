# sources/distributed-fs/ceph-client/drivers/power/reset/syscon-reboot-mode.c

## Purpose
generic syscon-backed reboot-mode provider.

## Important APIs, Types, and Functions
`struct syscon_reboot_mode`, write callback, and platform probe.

## Control Flow
probe gets parent syscon regmap, reads required `offset` and optional `mask`, initializes a reboot-mode driver, and registers it; callback writes magic into masked register bits.

## State and Persistence Behavior
mode magic persists in syscon/retention register until boot firmware consumes or clears it.

## Dependencies and Integration Points
MFD_SYSCON, reboot-mode core, OF.

## Risks and Edge Cases
mask defaults to all bits and can overwrite unrelated fields; parent must be a syscon; write failures occur during reboot notification.

## Test Signals
mode property parsing, mask behavior, bootloader recovery/bootloader modes, and regmap failures.
