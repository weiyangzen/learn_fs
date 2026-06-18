<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mux.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mux.h

## Purpose
Defines the OMAP1 pin-mux table schema, helper macros for mux/pull register fields, and declarations for mux initialization.

## Important APIs, Types, and Functions
Provides `MUX_CFG`, `MUX_CFG_7XX`, `struct pin_config`, `struct omap_mux_cfg`, `omap1_mux_init()`, `omap_mux_register()`, and `omap2_mux_init()` declarations.

## Control Flow
Compile-time macros expand concise table entries into `pin_config` initializers. Runtime flow is implemented in `mux.c`, which consumes the structures and register metadata generated here.

## State and Persistence Behavior
No state; it defines the structure of mux state that `mux.c` stores globally and writes to hardware.

## Dependencies and Integration Points
Depends on `linux/soc/ti/omap1-mux.h` for register constants and on optional debug config for register-name fields.

## Risks
Macro argument order is dense and easy to misuse: mux register, bit offset, mode, pull register, pull bit, pull state, pu/pd select, and debug flag. Incorrect metadata can silently program the wrong register bits.

## Test Signals
Compile with and without `CONFIG_OMAP_MUX_DEBUG` to ensure structure layout consumers match. Validate new table entries against TRM register fields and with runtime mux debug output.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mux.h -->
