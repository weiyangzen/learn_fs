# sources/distributed-fs/ceph-client/drivers/clk/spacemit/Makefile

## Purpose
This Makefile maps SpacemiT Kconfig symbols to common and SoC-specific clock-controller objects.

## Important APIs, Types, And Functions
`spacemit-ccu.o` is built from common helper files `ccu_common.o`, `ccu_pll.o`, `ccu_mix.o`, and `ccu_ddn.o`. `spacemit-ccu-k1.o` includes `ccu-k1.o`; `spacemit-ccu-k3.o` includes `ccu-k3.o`.

## Control Flow
The kernel build system links the aggregate common module when `CONFIG_SPACEMIT_CCU` is enabled and links K1/K3 modules based on their SoC-specific symbols.

## State And Persistence
No runtime state exists. The object grouping controls module boundaries and symbol linkage.

## Dependencies And Integration Points
This file integrates with the SpacemiT Kconfig menu and the shared CCU implementation files in the same directory. The SoC-specific objects depend on common code being available through `SPACEMIT_CCU`.

## Risks
Omitting a common helper object can cause unresolved symbols in K1/K3 modules. If common helpers export module symbols implicitly within the same aggregate only, moving objects between modules needs careful linkage review.

## Test Signals
Build common, K1, and K3 configurations as modules and built-ins. Confirm generated module names match expected platform-driver aliases and that K1/K3 modules can load with the common CCU module.
