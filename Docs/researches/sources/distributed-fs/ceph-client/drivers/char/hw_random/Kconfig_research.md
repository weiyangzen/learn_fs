# sources/distributed-fs/ceph-client/drivers/char/hw_random/Kconfig

## Purpose
This Kconfig file defines the hardware random number generator menu. It enables the common `HW_RANDOM` core and a large set of architecture, bus, firmware, and SoC-specific RNG provider drivers, plus UML random integration.

## Important APIs, Types, and Functions
- `menuconfig HW_RANDOM` gates the core `rng-core` module and `/dev/hwrng` infrastructure.
- Individual `config HW_RANDOM_*` symbols select provider drivers for Intel, AMD, Broadcom, Cavium/Marvell, CryptoCell, ARM SMCCC, Exynos, i.MX, Ingenic, Keystone, Meson, Mediatek, MPFS, JH7110, and others.
- Dependency clauses encode architecture, bus, firmware, I/O, OF, PCI, AMBA, and PM assumptions.

## Control Flow
There is no runtime control flow. Kconfig evaluation presents options under `if HW_RANDOM`, applies `depends on`, `default`, and help text rules, and emits configuration symbols consumed by the Makefile. `UML_RANDOM` sits outside the menu and selects `HW_RANDOM`.

## State and Persistence Behavior
The file persists build-time configuration state through `.config`. It does not create runtime state. Defaults often follow `HW_RANDOM` or specific architectures, making many provider modules available when the core is enabled.

## Dependencies and Integration Points
It integrates directly with `drivers/char/hw_random/Makefile`, provider source files, architecture symbols, PCI/OF/AMBA/OPTEE/IBMVIO/VIRTIO availability, and the kernel random subsystem through the selected core.

## Risks
Incorrect dependencies can expose unbuildable drivers to `COMPILE_TEST` or hide a valid provider for an SoC. Broad defaults to `HW_RANDOM` can increase build coverage and module footprint. Help text contains provider names used by users to select modules, so stale names can mislead configuration.

## Test Signals
Run `make olddefconfig`, `allmodconfig`, and targeted `COMPILE_TEST` builds for changed symbols. Verify each enabled symbol maps to an object in the Makefile and that architecture-specific providers are hidden without their required bus or firmware dependencies.
