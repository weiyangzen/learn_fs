# sources/distributed-fs/ceph-client/drivers/misc/mei/gsc_proxy/Makefile

## Purpose
This Makefile builds the Intel MEI GSC proxy client driver when `CONFIG_INTEL_MEI_GSC_PROXY` is enabled.

## Important APIs, Types, and Functions
The sole build rule is `obj-$(CONFIG_INTEL_MEI_GSC_PROXY) += mei_gsc_proxy.o`.

## Control Flow
Kbuild compiles `mei_gsc_proxy.c` into a module or built-in object according to the Kconfig symbol.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Connects the `gsc_proxy` subdirectory to the MEI top-level Makefile and Kconfig.

## Risks
A symbol/object mismatch would silently omit the proxy driver.

## Test Signals
Signals are successful module build and presence of the `mei_gsc_proxy` MEI client driver when configured.
