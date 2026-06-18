# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/Makefile

## Purpose
Builds the Freescale/NXP Management Complex bus driver as a composite kbuild object and optionally builds the userspace support module.

## Important APIs, Types, And Functions
`mc-bus-driver-objs` combines `fsl-mc-bus.o`, `mc-sys.o`, `mc-io.o`, `dpbp.o`, `dpcon.o`, `dprc.o`, `dprc-driver.o`, `fsl-mc-allocator.o`, `fsl-mc-msi.o`, `dpmcp.o`, and `obj-api.o`. `obj-$(CONFIG_FSL_MC_BUS)` builds the composite object, and `obj-$(CONFIG_FSL_MC_UAPI_SUPPORT)` adds `fsl-mc-uapi.o`.

## Control Flow
Kbuild links the listed objects into `mc-bus-driver.o` when `FSL_MC_BUS` is selected. The order matters because the composite driver contains command APIs, bus registration, MSI support, resource allocation, and object drivers that are initialized together.

## State And Persistence
There is no runtime state in the Makefile; it produces build artifacts.

## Dependencies And Integration Points
It depends on `drivers/bus/fsl-mc/Kconfig` symbols and on the listed source files remaining present. It integrates core fsl-mc command APIs with Linux bus/driver registration and optional UAPI support.

## Risks And Test Signals
Risks include omitting a required object from the composite, stale filenames, or building UAPI support without core bus support. Test signals are successful link of `mc-bus-driver.o`, symbol availability for exported DPAA2 APIs, and module/built-in smoke tests.
