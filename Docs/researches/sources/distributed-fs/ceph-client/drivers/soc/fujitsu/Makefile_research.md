
# sources/distributed-fs/ceph-client/drivers/soc/fujitsu/Makefile

## Purpose
Builds the Fujitsu A64FX diagnostic driver according to Kconfig.

## Important APIs, Types, and Functions
No code APIs. The single rule is `obj-$(CONFIG_A64FX_DIAG) += a64fx-diag.o`.

## Control Flow
Kernel build includes `a64fx-diag.c` only when `CONFIG_A64FX_DIAG=y`.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Consumes the `A64FX_DIAG` Kconfig symbol from the same directory.

## Risks
Low build-system risk; mismatch with Kconfig symbol would omit the driver.

## Test Signals
Compile with `CONFIG_A64FX_DIAG=y` and verify `a64fx-diag.o` is linked.
