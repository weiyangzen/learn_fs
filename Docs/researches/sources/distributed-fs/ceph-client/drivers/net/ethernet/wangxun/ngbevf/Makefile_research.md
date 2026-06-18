# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbevf/Makefile

## Purpose
The `ngbevf` Makefile builds the Wangxun 1GbE VF driver object when `CONFIG_NGBE` is enabled.

## Important APIs, Types, and Functions
It declares `obj-$(CONFIG_NGBE) += ngbevf.o` and builds `ngbevf.o` from `ngbevf_main.o`.

## Control Flow
Kbuild consumes this file at build time only. There is no runtime logic.

## State and Persistence Behavior
No runtime state or persistence is present.

## Dependencies and Integration Points
The object links against shared `libwx` VF/common code. The use of `CONFIG_NGBE` ties the VF module build to the same config symbol as the PF driver.

## Risks and Edge Cases
If Kconfig expects a separate VF option, this Makefile does not provide one. Adding VF support files requires updating `ngbevf-objs`.

## Test Signals
Build with `CONFIG_NGBE=m/y` and verify `ngbevf` links and loads with its shared dependencies.
