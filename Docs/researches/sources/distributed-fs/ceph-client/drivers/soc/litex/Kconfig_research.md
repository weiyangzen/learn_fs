
# sources/distributed-fs/ceph-client/drivers/soc/litex/Kconfig

## Purpose
Defines LiteX SoC Builder driver options.

## Important APIs, Types, and Functions
No runtime APIs. `LITEX` is a bool selected by `LITEX_SOC_CONTROLLER`; `LITEX_SOC_CONTROLLER` is tristate, depends on OF and HAS_IOMEM, and enables CSR access verification and common LiteX accessors.

## Control Flow
The controller symbol gates `litex_soc_ctrl.o`.

## State and Persistence
Kernel configuration only.

## Dependencies and Integration Points
Drivers using `linux/litex.h` accessors should depend on `LITEX`.

## Risks
The SPDX tag uses `SPDX-License_Identifier` rather than the standard `SPDX-License-Identifier`, which may not be recognized by tooling.

## Test Signals
Kconfig visibility, selection of `LITEX`, and license tooling checks.
