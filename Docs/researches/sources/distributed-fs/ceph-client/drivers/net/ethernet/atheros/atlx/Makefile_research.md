# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/Makefile

## Purpose
Defines Kbuild objects for the Attansic/Atheros `atlx` Ethernet drivers. It conditionally builds `atl1.o` for `CONFIG_ATL1` and `atl2.o` for `CONFIG_ATL2`.

## Important APIs, Types, and Functions
There are no C APIs or runtime functions. The important declarations are `obj-$(CONFIG_ATL1) += atl1.o` and `obj-$(CONFIG_ATL2) += atl2.o`.

## Control Flow and State
Build-time only. Kconfig symbols select which object files become part of the kernel or modules. No runtime state is created here.

## Dependencies and Integration Points
Integrated with Linux Kbuild and the surrounding `drivers/net/ethernet/atheros` build. `atl1.o` compiles `atl1.c`, which directly includes `atlx.c` as a shared helper implementation. `atl2.o` is another driver in the same folder and shares common `atlx` definitions.

## Risks
The Makefile is small but controls driver inclusion. A wrong object mapping would silently drop driver support or build the wrong module. Because `atl1.c` includes `atlx.c` textually, common-helper compilation assumptions differ from normal multi-object linking; splitting the objects would require symbol/export changes rather than a Makefile-only edit.

## Test Signals
Build with `CONFIG_ATL1=m/y`, `CONFIG_ATL2=m/y`, both enabled, and both disabled. Confirm the expected modules/objects are produced and no duplicate-symbol issues appear from the textual `atlx.c` inclusion.
