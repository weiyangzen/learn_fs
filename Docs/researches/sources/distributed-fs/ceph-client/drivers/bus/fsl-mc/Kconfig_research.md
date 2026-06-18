# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/Kconfig

## Purpose
Defines Kconfig options for the Freescale/NXP DPAA2 Management Complex bus and its optional userspace support.

## Important APIs, Types, And Functions
`FSL_MC_BUS` enables the core QorIQ DPAA2 fsl-mc bus driver. It depends on OF and supported architectures or `COMPILE_TEST`, and selects `GENERIC_MSI_IRQ`. `FSL_MC_UAPI_SUPPORT` enables userspace interrogation/configuration support and depends on `FSL_MC_BUS`.

## Control Flow
Kconfig resolution controls whether the fsl-mc composite object and optional UAPI object are built. The main bus option gates discovery and binding of DPAA2 objects represented as Linux devices; UAPI support is layered on top.

## State And Persistence
The file contributes configuration state through `.config`; it has no runtime state.

## Dependencies And Integration Points
It is included by `drivers/bus/Kconfig` and consumed by `drivers/bus/fsl-mc/Makefile`. It connects DPAA2 object discovery to OF-described platforms and MSI interrupt infrastructure.

## Risks And Test Signals
Risks include excluding valid architectures, missing interrupt infrastructure selection, or enabling UAPI without the bus. Test signals are config dependency checks, compile-test builds, and boot-time fsl-mc bus discovery on Layerscape/DPAA2 systems.
