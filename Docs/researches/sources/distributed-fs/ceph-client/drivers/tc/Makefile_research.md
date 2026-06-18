# sources/distributed-fs/ceph-client/drivers/tc/Makefile

## Purpose
Builds the TURBOchannel bus support objects when `CONFIG_TC` is enabled.

## Important APIs, Types, and Functions
The only build rule is `obj-$(CONFIG_TC) += tc.o tc-driver.o`, which links bus probing/enumeration from `tc.c` with driver-core services from `tc-driver.c`.

## Control Flow and State
No runtime flow. Kbuild includes these objects in the kernel or module according to the `CONFIG_TC` tristate/bool configuration.

## Dependencies and Integration Points
Depends on the architecture/configuration exposing `CONFIG_TC` and public declarations in `<linux/tc.h>`.

## Risks and Test Signals
If either object is omitted, the TC bus either cannot enumerate devices or cannot match/register drivers. Test signals are successful builds for TC-enabled architectures and presence of `tc_bus_type` plus `tc_init()` in the final image.
