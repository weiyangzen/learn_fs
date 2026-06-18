# sources/distributed-fs/ceph-client/drivers/clk/spacemit/Kconfig

## Purpose
This Kconfig file declares clock support for SpacemiT platforms. It provides a common CCU symbol plus selectable K1 and K3 SoC clock-controller drivers.

## Important APIs, Types, And Functions
The symbols are `SPACEMIT_CCU`, `SPACEMIT_K1_CCU`, and `SPACEMIT_K3_CCU`. The common symbol is tristate and selects `AUXILIARY_BUS` and `MFD_SYSCON`. K1 and K3 symbols are user-visible tristates that select the common CCU support.

## Control Flow
Configuration selection controls which Makefile objects are built. Selecting either SoC-specific CCU pulls in the shared CCU core.

## State And Persistence
No runtime state exists in this file. Build configuration determines module availability and dependency inclusion.

## Dependencies And Integration Points
The menu is visible when `ARCH_SPACEMIT || COMPILE_TEST`. It integrates with `drivers/clk/spacemit/Makefile`, shared CCU implementation files, and SoC-specific K1/K3 sources elsewhere in the directory.

## Risks
Because the common CCU symbol is hidden, all SoC-specific symbols must continue to select it. Missing dependencies on syscon or auxiliary bus would break shared CCU probe paths, but both are selected here.

## Test Signals
Run build coverage for `ARCH_SPACEMIT`, `COMPILE_TEST`, K1-only, K3-only, both built-in, and both modular configurations. Runtime tests should verify module autoload and shared CCU dependency loading.
