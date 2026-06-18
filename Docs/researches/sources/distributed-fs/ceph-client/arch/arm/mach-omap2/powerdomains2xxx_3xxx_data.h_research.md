# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains2xxx_3xxx_data.h

## Purpose
`powerdomains2xxx_3xxx_data.h` declares the shared OMAP2/3 powerdomain descriptors defined in `powerdomains2xxx_3xxx_data.c`.

## Important APIs, Types, and Functions
It declares `extern struct powerdomain gfx_omap2_pwrdm;` and `extern struct powerdomain wkup_omap2_pwrdm;`.

## Control Flow
There is no control flow. SoC-specific data files include the header and reference the shared descriptors in their init arrays.

## State and Persistence Behavior
The header owns no state but exposes mutable `struct powerdomain` objects to OMAP2/3 registration code.

## Dependencies and Integration Points
It includes `powerdomain.h` and integrates with OMAP2/3 data files that need the shared GFX and WKUP domains.

## Risks
Declaration/definition mismatch breaks builds. Incorrect sharing can register a descriptor on SoCs where the hardware block is absent.

## Test Signals
Compile OMAP2 and OMAP3 powerdomain data. Boot each SoC family and ensure shared domains are registered only on valid variants.
