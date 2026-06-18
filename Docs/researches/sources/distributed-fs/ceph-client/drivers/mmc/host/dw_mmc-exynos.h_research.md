# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-exynos.h

Purpose: provides Exynos-specific register offsets and bitfield helpers used by `dw_mmc-exynos.c` for clock selection, HS400 DQS/strobe control, security management unit registers, and fixed divider constants.

Important APIs and definitions: key offsets include `SDMMC_CLKSEL`, `SDMMC_CLKSEL64`, `SDMMC_HS400_DQS_EN`, `SDMMC_HS400_DLINE_CTRL`, and SMU protector registers. Macros build and update sample/drive/divider timing fields, read divider/drive values, clear wakeup interrupt state, control data strobe and AXI nonblocking writes, and encode DQS read delay.

Control flow: no executable code exists. The Exynos implementation reads and writes these offsets through the shared `mci_readl/mci_writel` macros while handling `set_ios`, tuning, init, and resume.

State and persistence: the header stores no state. Constants describe hardware register state that is saved in Exynos private data or reprogrammed at runtime by the C file.

Dependencies and integration points: included by `dw_mmc-exynos.c` and assumes Linux `BIT` plus shared DW register access conventions. It is tightly coupled to Samsung/ARTPEC register layouts layered around the standard DW MMC block.

Risks: macro names are similar to standard DW fields but target SoC extension registers; misuse in generic code would corrupt unrelated offsets. Fixed dividers and minimum clock constants must match SoC integration. SMU constants allow broad non-secure access when programmed by the implementation.

Test signals: compile coverage for Exynos driver, register read/write validation on Exynos4/5/7/7870 and ARTPEC-8, HS400 mode testing, and resume tests that exercise `SDMMC_CLKSEL_WAKEUP_INT`.
