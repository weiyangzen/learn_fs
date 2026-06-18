# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-ma35d1.c

Purpose: this platform driver supports the Nuvoton MA35D1 SDHCI controller. It adds command-conflict clock gating rules, 128 MiB ADMA boundary splitting, pinctrl-assisted voltage switching, reset-before-tuning behavior, syscon voltage-stable setup, and removal-time card clock disable.

Important APIs, types, and functions: `struct ma35_priv` stores reset control and optional pinctrl states. `restore_data[]` lists SDHCI and vendor registers saved around tuning reset. `ma35_adma_write_desc` splits descriptors crossing 128 MiB boundaries. `ma35_set_clock` toggles `MA35_SDHCI_CMD_CONFLICT_CHK` based on whether the target clock exceeds 52 MHz. `ma35_execute_tuning` saves registers, asserts/deasserts reset, restores registers, then delegates to `sdhci_execute_tuning()`.

Control flow: `ma35_probe()` initializes platform data, expands ADMA table count using DMA mask size, enables an optional unnamed clock, parses MMC/OF properties, gets reset control, initializes optional pinctrl states, optionally sets a system-controller voltage-stable bit and overrides voltage switching, overrides execute tuning, adds the host, and finally programs MBIU burst chunks. Voltage switch selects `state_uhs` or `default` before generic SDHCI voltage switching.

State and persistence: persistent driver state is in devm-managed private data and hardware registers. The tuning path temporarily captures register values in a stack array and restores them after controller reset. Pinctrl state and syscon bits remain in hardware only; no filesystem state exists.

Dependencies and integration points: integrates with `sdhci-pltfm`, reset framework, optional clocks, DMA mask APIs, pinctrl, `mmc_of_parse`, syscon/regmap property `nuvoton,sys`, and compatible `nuvoton,ma35d1-sdhci`.

Risks: register restore coverage must match all registers reset by the tuning workaround; missing a register can cause subtle post-tuning failures. Boundary-splitting assumes two descriptors are enough per crossing and requires the expanded ADMA table count. Pinctrl lookup failures are tolerated, so boards relying on pin state must define names correctly. Probe error paths return without explicit host free, relying on devm/platform cleanup.

Test signals: tune at HS200/SDR104 speeds, transfers crossing 128 MiB DMA boundaries, voltage switch with and without `state_uhs`, command-conflict behavior across 52 MHz, syscon absence/presence, reset controller faults, and remove-time clock disable should be exercised.
