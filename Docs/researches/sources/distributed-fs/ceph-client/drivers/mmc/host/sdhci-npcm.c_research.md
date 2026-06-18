# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-npcm.c

Purpose: this is a compact Nuvoton NPCM SDHCI platform driver for NPCM7xx and NPCM8xx controllers. It mostly selects SoC-specific SDHCI quirks, enables the optional clock, exposes 8-bit capability when hardware advertises it, parses MMC DT properties, and registers the generic SDHCI host.

Important APIs, types, and functions: the two `struct sdhci_pltfm_data` instances are the primary configuration: NPCM7xx uses `SDHCI_QUIRK_DELAY_AFTER_POWER` plus `SDHCI_QUIRK2_STOP_WITH_TC` and `SDHCI_QUIRK2_NO_1_8_V`; NPCM8xx drops the no-1.8-V restriction. `npcm_sdhci_probe()` is the only custom control path. The platform driver uses `sdhci_pltfm_remove` and `sdhci_pltfm_pmops`.

Control flow: probe obtains match data, initializes an SDHCI platform host with the matched quirks, enables an optional unnamed clock through `devm_clk_get_optional_enabled()`, reads `SDHCI_CAPABILITIES`, sets `MMC_CAP_8_BIT_DATA` if `SDHCI_CAN_DO_8BIT` is present, parses MMC DT properties, and calls `sdhci_add_host()`. There is no custom reset, clock, tuning, voltage, or power code.

State and persistence: there is no private driver state beyond the generic `sdhci_pltfm_host` and its optional clock. Persistent behavior comes from static match data and hardware capabilities read at probe time.

Dependencies and integration points: the file depends on `sdhci-pltfm.h`, clock APIs, MMC host capability bits, and OF match data for `nuvoton,npcm750-sdhci` and `nuvoton,npcm845-sdhci`.

Risks: because probe returns directly on failures after `sdhci_pltfm_init()`, cleanup depends on devm/platform lifetime and generic remove behavior. The 8-bit capability is trusted from the hardware register rather than DT, so incorrect capability wiring could expose a bus width the board cannot use. NPCM7xx intentionally disables 1.8 V; regressions here would show as failed UHS negotiation.

Test signals: successful module probe, clock enable, `mmc_of_parse()` behavior for bus width/card-detect properties, correct absence or presence of 1.8 V modes by compatible, 8-bit eMMC enumeration when `SDHCI_CAN_DO_8BIT` is set, and suspend/resume via platform PM ops.
