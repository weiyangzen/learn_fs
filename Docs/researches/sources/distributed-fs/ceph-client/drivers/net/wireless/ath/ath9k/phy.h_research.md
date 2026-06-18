<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/phy.h

Purpose: Provides compact PHY register and bitfield constants used by ath9k hardware code, especially channel select math, TX gain/CLC fields, antenna swap/reduced-chain flags, chip ID, spur frequency fields, PLL registers, and antenna diversity LNA configuration values.

Important APIs and types: Macros include `CHANSEL_2G()`, `CHANSEL_5G()`, `AR_PHY_BASE`, `AR_PHY(n)`, TX power/gain masks and shifts, CLC table/register fields, `ANTSWAP_AB`, `REDUCE_CHAIN_0`, `REDUCE_CHAIN_1`, `AR_PHY_CHIP_ID`, spur frequency masks, `AR_PHY_PLL_CONTROL`, and `AR_PHY_PLL_MODE`. The only type is `enum ath9k_ant_div_comb_lna_conf`, enumerating LNA1/LNA2 combining modes.

Control flow: None. This header is a constant definition layer consumed by register-programming code in chipset-specific PHY, calibration, spur mitigation, channel, PLL, and antenna-diversity paths.

State and persistence: No state. The constants define hardware register addresses and bit meanings; writes using these constants persist in hardware registers until reset/reprogramming.

Dependencies and integration points: Included by ath9k hardware implementation files through shared headers. Integrates with channel frequency selection, AR PHY register addressing, calibration/tuning logic, and antenna diversity decisions that reference `ath9k_ant_div_comb_lna_conf`.

Risks: Incorrect channel select divisors or register masks can tune the radio to wrong frequencies or corrupt PHY calibration. The file is small but high impact because constants are trusted by low-level code without runtime validation. LNA enum ordering must match code and hardware expectations.

Test signals: Compile all chipset PHY code, validate 2 GHz/5 GHz channel programming, PLL control writes, spur mitigation fields, TX gain calibration, antenna-diversity LNA transitions, and hardware bring-up/regression on devices using reduced-chain or antenna-swap settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/phy.h -->
