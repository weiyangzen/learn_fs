# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-esdhc.c

Purpose: this driver adapts Freescale/NXP eSDHC OF controllers to the SDHCI core. eSDHC exposes mostly 32-bit registers with non-standard bit layouts, so the file provides endian-specific read/write shims, clock/tuning workarounds, voltage switching, DMA setup, and SoC errata handling.

Important APIs, types, and functions: `struct sdhci_esdhc` records vendor/spec versions, errata booleans, peripheral clock, clock fixups, and the active divider ratio. `struct esdhc_clk_fixup` caps timing-specific clocks for affected LS/P-series SoCs. Register access is normalized by `esdhc_readl_fixup`, `esdhc_readw_fixup`, `esdhc_readb_fixup`, and matching write fixups used by BE/LE `sdhci_ops`. Other key functions are `esdhc_of_set_clock`, `esdhc_execute_tuning`, `esdhc_signal_voltage_switch`, `esdhc_reset`, `esdhc_of_enable_dma`, and `esdhc_irq`.

Control flow: `sdhci_esdhc_probe()` chooses big- or little-endian platform data from the `little-endian` property, installs MMC host callbacks for voltage switching, tuning, and HS400 DDR preparation, calls `esdhc_init()` to detect host version, SoC quirks, peripheral clock, and DMA clock source, applies OF/MMC properties and SoC-specific quirks, parses voltage ranges, then adds the host. During I/O, SDHCI register access flows through the fixup layer, which merges transfer mode with command writes, remaps host-control DMA bits, masks unsupported capabilities, and preserves old hardware layouts.

State and persistence: state is volatile in `struct sdhci_esdhc` plus hardware registers. `esdhc_proctl` is a static suspend scratch value for host-control restore. Tuning state includes `in_sw_tuning` and `div_ratio`; suspend can request retuning when the mode is not tuning mode 3. No persistent disk state is produced.

Dependencies and integration points: the driver integrates with `sdhci-pltfm`, `sdhci-esdhc.h` register definitions, OF matching, `soc_device_match()` errata tables, common clock API, DMA coherency from OF, SCFG syscon-like IO mapping for voltage select, and MMC tuning/HS400 callbacks.

Risks: the biggest risk is register translation drift: the core assumes standard SDHCI semantics while hardware uses eSDHC placement. Tuning errata paths mix hardware and software tuning, reduced clocks, tuning-block windows, and DLL setup; small order changes can cause false tuning success. Voltage switching maps a global matching SCFG node and ioremaps it dynamically, so platform description mistakes can affect unrelated hosts. The static `esdhc_proctl` is shared across instances, which is a multi-host suspend/resume risk.

Test signals: validate BE and LE systems, host-version fixups, clock fixups per compatible, P2020/P1010/LS errata, DMA coherent and non-coherent paths, HS200/HS400 tuning including erratum fallback, 1.8 V switching through SCFG and direct PROCTL, suspend/resume with retune, and ADMA block-gap workaround behavior.
