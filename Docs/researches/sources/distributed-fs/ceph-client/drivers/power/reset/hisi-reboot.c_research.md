# sources/distributed-fs/ceph-client/drivers/power/reset/hisi-reboot.c

## Purpose
HiSilicon board reboot driver.

## Important APIs, Types, and Functions
global MMIO base and reboot offset, restart notifier `hisi_restart_handler()`, and platform probe.

## Control Flow
probe maps MMIO, reads optional reboot offset, registers restart notifier; handler writes magic/reset value to the mapped offset and delays.

## State and Persistence Behavior
global base/offset persist for module lifetime; hardware reset register controls final reboot.

## Dependencies and Integration Points
ARCH_HISI, OF platform, MMIO, restart notifier.

## Risks and Edge Cases
single global instance; no unregister in built-in usage; minimal error checking after write.

## Test Signals
HiSilicon DT probe, custom offset, restart register trace, and reboot.
