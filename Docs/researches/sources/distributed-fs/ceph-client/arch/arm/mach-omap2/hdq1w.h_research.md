<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/hdq1w.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/hdq1w.h

## Purpose
`hdq1w.h` shares OMAP HDQ/1-Wire reset constants and the reset helper prototype with hwmod integration code.

## Important APIs, Types, and Functions
It defines `HDQ_CTRL_STATUS_OFFSET`, `HDQ_CTRL_STATUS_CLOCKENABLE_SHIFT`, and declares `omap_hdq1w_reset(struct omap_hwmod *oh)`.

## Control Flow
No runtime control flow exists. Consumers use the constants during the custom reset flow in `hdq1w.c`.

## State and Persistence Behavior
No state is stored here. The constants describe module register state controlled elsewhere.

## Dependencies and Integration Points
It includes `omap_hwmod.h` and integrates with `hdq1w.c` and OMAP hwmod reset hooks. The comment indicates a future driver cleanup could move these macros to the actual HDQ driver.

## Risks
Changing offsets or bit positions breaks the reset sequence. Moving definitions requires synchronized changes in both mach code and any HDQ driver users.

## Test Signals
Compile HDQ-enabled OMAP builds and verify `omap_hdq1w_reset()` users still see the prototype and constants. Runtime validation is successful HDQ reset and driver probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/hdq1w.h -->
