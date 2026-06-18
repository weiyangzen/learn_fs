
# sources/distributed-fs/ceph-client/drivers/soc/hisilicon/Makefile

## Purpose
Builds the Kunpeng HCCS driver when selected.

## Important APIs, Types, and Functions
No runtime APIs. The rule is `obj-$(CONFIG_KUNPENG_HCCS) += kunpeng_hccs.o`.

## Control Flow
Kernel build includes the HCCS object for built-in or module builds according to the tristate symbol.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Consumes `CONFIG_KUNPENG_HCCS` from Kconfig.

## Risks
Low build-rule risk; symbol mismatch would omit the driver.

## Test Signals
Build with `CONFIG_KUNPENG_HCCS=m/y`.
