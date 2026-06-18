# sources/distributed-fs/ceph-client/drivers/peci/controller/Kconfig

Purpose: Defines Kconfig options for hardware PECI bus controller drivers.

Important APIs and types: `CONFIG_PECI_ASPEED` enables ASPEED AST2400/AST2500/AST2600 PECI support with dependencies on ASPEED or compile-test, device tree, I/O memory, and common clock. `CONFIG_PECI_NPCM` enables Nuvoton NPCM PECI support with OF and `REGMAP_MMIO`.

Control flow: Kconfig only. Selection controls which controller objects are built and available to register with the PECI core.

State and persistence: Build configuration determines platform-driver availability and module names `peci-aspeed` or `peci-npcm`.

Dependencies and integration points: Sourced by the top-level PECI Kconfig only when `PECI` is enabled. Controller drivers depend on platform-specific clocks, MMIO, and device-tree matching.

Risks: Missing OF/common-clock dependencies would break ASPEED probe; `COMPILE_TEST` permits non-ASPEED build coverage but not runtime support. NPCM selects regmap MMIO while ASPEED uses direct MMIO and clock-provider APIs.

Test signals: Menu visibility under `PECI`, compile-test builds, module generation for selected controllers, and device-tree compatible matching at runtime.
