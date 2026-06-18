# sources/distributed-fs/ceph-client/drivers/power/reset/st-poweroff.c

## Purpose
STMicroelectronics STi restart driver using syscfg regmap.

## Important APIs, Types, and Functions
`struct reset_syscfg`, static STiH407 register/mask data, global selected config, restart notifier, and platform probe.

## Control Flow
probe matches compatible data, resolves `st,syscfg` regmap, and registers restart; callback updates syscfg bits to request reset and delays.

## State and Persistence Behavior
global pointer to selected syscfg config persists; syscfg bits persist until reset.

## Dependencies and Integration Points
ARCH_STI, syscon/regmap, OF, restart notifier.

## Risks and Edge Cases
global state is single-instance; no unregister for built-in path; exact masks are SoC-specific.

## Test Signals
STiH407 DT probe, syscfg phandle failure, restart bit trace, and reboot.
