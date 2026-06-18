# sources/distributed-fs/ceph-client/arch/x86/include/asm/olpc_ofw.h

## Purpose
Declares OLPC Open Firmware detection, call, page-table setup, and device-tree construction interfaces.

## Important APIs, Types, And Functions
Defines `OLPC_OFW_PDE_NR`, `OLPC_OFW_SIG`, `olpc_ofw(name, args, res)` wrapper, `__olpc_ofw()`, `olpc_ofw_detect()`, `setup_olpc_ofw_pgd()`, `olpc_ofw_present()`, `olpc_ofw_is_installed()`, and `olpc_dt_build_devicetree()`. Disabled configs provide no-op stubs for setup/detection.

## Control Flow
Boot code detects whether OFW is installed and mapped at the expected location, installs its PDE into kernel page tables, then later callers can invoke firmware commands through `__olpc_ofw()` with argument/result arrays. Device-tree construction can query OFW.

## State And Persistence
State is detected firmware presence and page-table mapping. It persists for the booted kernel.

## Dependencies And Integration Points
Integrates with OLPC platform boot, early page-table setup, firmware calls, and device-tree population.

## Risks And Edge Cases
Calling firmware requires exact argument counts and stable mapping. Wrong PDE index or signature handling can corrupt page tables or call absent firmware. Disabled stubs omit `olpc_ofw_present()`, so callers must be config-aware.

## Test Signals
OLPC boot with OFW present, device-tree creation, firmware command smoke tests, and non-OLPC build coverage are useful.
