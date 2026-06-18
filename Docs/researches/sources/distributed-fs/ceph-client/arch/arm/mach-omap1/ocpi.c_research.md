<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ocpi.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ocpi.c

## Purpose
Provides minimal OMAP16xx OCPI interconnect setup, primarily to allow OHCI USB access through the OCP bridge.

## Important APIs, Types, and Functions
Exports `ocpi_enable()`. Module lifecycle functions are `omap_ocpi_init()` and `omap_ocpi_exit()`.

## Control Flow
`omap_ocpi_init()` exits on non-16xx, gets and enables `l3_ocpi_ck`, calls `ocpi_enable()`, and logs availability. `ocpi_enable()` clears low protection/security bits in OCPI registers to allow peripheral bus access. Exit disables and releases the clock.

## State and Persistence Behavior
State is the retained `ocpi_ck` pointer and modified OCPI protection/security registers. The code does not restore OCPI register values on module exit.

## Dependencies and Integration Points
Uses the clock framework, OMAP1 raw IO helpers, CPU predicates, and is called by USB OHCI platform data through `usb.c`.

## Risks
Only OMAP16xx is supported. The protection/security writes are broad (`~0xff`) and affect access policy for the bridge. Clock acquisition failure prevents OCPI setup and can break USB host DMA/register access.

## Test Signals
On OMAP16xx with OHCI enabled, verify `l3_ocpi_ck` enablement, `ocpi_enable()` success, and USB host enumeration. Non-16xx tests should return `-ENODEV`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ocpi.c -->
