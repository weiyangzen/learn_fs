# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci_f_sdh30.c

Purpose: this platform driver supports Fujitsu/Socionext F_SDH30 SDHCI 3.0-style controllers. It supplies vendor reset, voltage-switch, minimum-clock, clock/reset resource handling, and extended-register initialization around the generic SDHCI platform core.

Important APIs, types, and functions: `struct f_sdhost_priv` stores interface/core clocks, optional reset control, vendor HS200 bit, device pointer, and the command/data delay option. `sdhci_f_sdh30_soft_voltage_switch()` programs F_SDH30 IO control and tuning registers for 1.8 V switching and optional HS200 vendor mode. `sdhci_f_sdh30_reset()` wraps generic `sdhci_reset()` with clock-before-reset, command/data delay, and forced card-present behavior for nonremovable media. Probe and remove own the platform host, clocks, reset, vendor register initialization, and `sdhci_add_host()`/`sdhci_pltfm_remove()`.

Control flow: probe allocates an SDHCI platform host with F_SDH30 private data, parses MMC properties, reads the optional command/data delay property, and for OF-backed devices enables `iface` and `core` clocks plus an optional shared reset. It initializes AHB burst/endian/bus-lock bits, toggles eMMC reset in `F_SDH30_ESD_CONTROL`, detects HS200 vendor support from SDHCI capabilities, sets a timeout quirk if the timeout clock is absent, and registers the host. Remove delegates SDHCI teardown to `sdhci_pltfm_remove()`, asserts reset, and disables clocks.

State and persistence: private state persists clock/reset handles and vendor capability choices. Hardware state in AHB, IO_CONTROL2, ESD_CONTROL, TUNING_SETTING, and TEST registers is rewritten during probe, reset, and voltage switch. The `vendor_hs200` flag is derived once from capabilities and reused during soft voltage switch.

Dependencies and integration points: the driver uses `sdhci-pltfm`, generic `sdhci_set_clock()`, `sdhci_set_bus_width()`, `sdhci_set_uhs_signaling()`, OF/ACPI matching, common clocks, reset controls, and MMC DT parsing. Compatibles are `fujitsu,mb86s70-sdhci-3.0` and `socionext,f-sdh30-e51-mmc`; ACPI ID is `SCX0002`.

Risks: the reset path writes a magic clock value if SDHCI clock control is zero, so clock/reset ordering is important. Forced card insertion for nonremovable devices can mask physical detect issues. The driver infers HS200 vendor mode from `SDHCI_CAN_DO_8BIT`, which couples bus-width capability to high-speed vendor programming. Error paths after clock enabling must unwind both clocks and reset correctly. Timeout-clock absence switches to SDCLK-derived timeout behavior, which needs accurate clock reporting.

Test signals: validate OF and ACPI probe, both clock names, optional reset deassert/assert, AHB config bits after probe, eMMC reset pulse, nonremovable card-present force, 1.8 V/HS200 voltage switch register sequence, command/data delay property behavior, and suspend/resume through `sdhci_pltfm_pmops`.
