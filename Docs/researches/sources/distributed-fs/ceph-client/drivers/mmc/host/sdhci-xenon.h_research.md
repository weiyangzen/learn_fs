# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-xenon.h

Purpose: this shared header defines Marvell Xenon SDHC vendor register offsets, bit fields, variant IDs, private driver state, and the PHY helper interface used between `sdhci-xenon.c` and `sdhci-xenon-phy.c`.

Important APIs, types, and functions: register definitions cover system configuration, system operation control, extended operation control, tuning status/control, eMMC strobe control, retuning request control, extended present state, and current DLL delay. Constants define default and lowest SDCLK frequencies, retuning counts, and Xenon-specific Host Control 2 values for HS200 and HS400. `enum xenon_variant` names `XENON_A3700`, `XENON_AP806`, `XENON_AP807`, `XENON_CP110`, and `XENON_AC5`. `struct xenon_priv` is the shared per-host state. Function prototypes export `xenon_phy_adj()`, `xenon_phy_parse_params()`, and `xenon_soc_pad_ctrl()` from the PHY companion.

Control flow: the header itself does not execute logic, but it defines the data contract for the Xenon driver pair. The platform file allocates `struct xenon_priv` as SDHCI platform private data, fills variant, slot ID, tuning count, clocks, and restore state, then delegates PHY parsing and adjustment to the PHY file. The PHY file reads and updates `phy_type`, `phy_params`, `emmc_phy_regs`, cached IOS fields, and initial card type from this structure.

State and persistence: persistent state in `struct xenon_priv` includes retuning period, SDHC slot index, initialization-time card type, cached bus width/timing/clock for avoiding redundant PHY programming, AXI clock handle, selected PHY type, board-specific PHY parameters, register table pointer, restore-needed flag for system sleep, and hardware variant. Comments explicitly limit `init_card_type` to initialization/PHY-timing use rather than normal transfer-time card access.

Dependencies and integration points: the header assumes SDHCI/MMC types are visible to C files including it and shares constants with both the platform and PHY implementations. It is the boundary that prevents the PHY file from needing to know platform probe details while still letting it use Xenon-private state.

Risks: because register offsets and bit fields are centralized here, incorrect definitions affect reset recovery, slot enablement, SDIO IRQ indication, retuning, HS400 strobe, and DLL lock detection. `struct xenon_priv` contains a `void *phy_params`, so type safety is enforced only by the platform/PHY pairing. Cached IOS state must be cleared on runtime suspend; otherwise the PHY layer can skip needed reconfiguration after clocks are stopped.

Test signals: compile both Xenon C files together, validate all supported compatibles map to the expected `enum xenon_variant`, verify private state initialization before PHY calls, confirm reset/resume reuses the register constants correctly, and exercise IOS changes that update cached bus width/timing/clock.
