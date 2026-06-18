# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/Kconfig

Purpose: defines build-time switches for MediaTek and Airoha PM-domain drivers under a menu gated by `ARCH_MEDIATEK || COMPILE_TEST`.

Important entries: `MTK_SCPSYS` is the legacy MediaTek SCPSYS provider and selects `REGMAP`, `MTK_INFRACFG`, and generic PM domains when PM is enabled. `MTK_SCPSYS_PM_DOMAINS` enables the newer generic SCPSYS power-controller driver with regmap and genpd. `MTK_MFG_PM_DOMAIN` enables MFlexGraphics GPU power/frequency support, requires PM, OF, common clock, selects mailbox and genpd, and implies `MTK_GPUEB_MBOX`. `AIROHA_CPU_PM_DOMAIN` is tristate CPU PM-domain support using ARM SMCCC performance-state calls.

Control flow and integration: these symbols drive the Makefile objects in the same directory and therefore select whether platform drivers become built-in or modules. The MediaTek SCPSYS options are bool, while Airoha CPU is tristate and MFG is declared bool despite help text mentioning `y or m`.

State and persistence behavior: no runtime state. It controls kernel configuration and dependency propagation.

Dependencies: relies on architecture symbols, PM, OF, REGMAP, COMMON_CLK, MAILBOX, ARM SMCCC, and MediaTek infracfg support. Build correctness depends on compatible DT bindings being selected elsewhere.

Risks: both legacy `MTK_SCPSYS` and newer `MTK_SCPSYS_PM_DOMAINS` can be enabled together for different compatibles, so duplicate compatible coverage must be avoided in driver tables. `MTK_MFG_PM_DOMAIN` help says module support but the symbol is bool, which may mislead packaging/tests.

Test signals: randconfig/allmodconfig should verify dependencies; DT boot tests should confirm the expected object is built for each compatible and no unresolved symbols appear when COMPILE_TEST is used.
