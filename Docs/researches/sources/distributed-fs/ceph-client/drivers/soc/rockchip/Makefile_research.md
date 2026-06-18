# sources/distributed-fs/ceph-client/drivers/soc/rockchip/Makefile

## Purpose

The Rockchip SoC Makefile maps Kconfig symbols to the GRF, IO-domain, and DTPM object files.

## Important APIs, Types, and Functions

`obj-$(CONFIG_ROCKCHIP_GRF) += grf.o`, `obj-$(CONFIG_ROCKCHIP_IODOMAIN) += io-domain.o`, and `obj-$(CONFIG_ROCKCHIP_DTPM) += dtpm.o` are the entire build contract.

## Control Flow

Kbuild includes the relevant object when each symbol is enabled as built-in or module according to Kconfig type.

## State and Persistence Behavior

No runtime state. Build artifacts reflect `.config`.

## Dependencies and Integration Points

It depends on local Kconfig symbols and source file names staying synchronized.

## Risks and Edge Cases

Renaming source files or adding a new Rockchip SoC helper without this Makefile update will silently omit code from builds. Module/built-in state follows Kconfig and can affect init ordering.

## Test Signals

Build each symbol individually as supported and verify expected object/module output.
