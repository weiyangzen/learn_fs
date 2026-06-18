<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ti81xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ti81xx.h

### Purpose
`ti81xx.h` defines base physical addresses for TI81xx control, PRCM, slow L4, TAP, and interrupt-controller blocks.

### Important APIs, Types, And Functions
It exposes address macros such as `L4_SLOW_TI81XX_BASE`, `TI81XX_CTRL_BASE`, `TI81XX_PRCM_BASE`, `TI81XX_TAP_BASE`, and `TI81XX_ARM_INTC_BASE`.

### Control Flow
There is no executable flow. The derived TAP base compensates for common OMAP revision-check code adding a fixed offset while TI81xx places the device ID elsewhere.

### State, Persistence, And Dependencies
The header has no state and depends on TI81xx control-module offset definitions from included OMAP headers.

### Integration Points
SoC revision detection, control-module access, PRCM access, and interrupt-controller mapping use these constants.

### Risks
Incorrect base constants break early boot mappings and SoC identification. The TAP adjustment is subtle and tied to implementation details of `omap3_check_revision`.

### Test Signals
Early boot on TI81xx should identify the device revision correctly and map PRCM/control/interrupt blocks without faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ti81xx.h -->
