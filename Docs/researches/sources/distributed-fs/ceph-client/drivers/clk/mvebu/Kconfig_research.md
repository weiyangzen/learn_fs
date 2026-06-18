# sources/distributed-fs/ceph-client/drivers/clk/mvebu/Kconfig

Purpose: defines build symbols for Marvell EBU/Armada clock controller support.

Important APIs/types: internal helper symbols include `MVEBU_CLK_COMMON`, `MVEBU_CLK_CPU`, `MVEBU_CLK_COREDIV`, and `ARMADA_AP_CP_HELPER`. SoC symbols select the helper subsets required by their clock files.

Control flow: Kconfig selection controls which early-init or platform clock drivers are compiled. Legacy Armada 370/XP/Dove/Kirkwood/Orion select common helpers; AP806/CP110 and AP CPU select AP/CP naming helpers.

State and persistence: build-time only.

Dependencies and integration: consumed by the mvebu Makefile and platform/`CLK_OF_DECLARE` code in the folder.

Risks: symbols are bool and mostly hidden, so top-level SoC config must select them correctly. Missing helper selection causes link failures or missing runtime providers.

Test signals: defconfig coverage for each Armada family, compile-test builds of individual symbols, and verifying dependent object inclusion.
