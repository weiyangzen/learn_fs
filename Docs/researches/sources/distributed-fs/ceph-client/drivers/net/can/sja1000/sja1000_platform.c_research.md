# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/sja1000_platform.c

Purpose: platform-bus SJA1000 driver supporting legacy platform data and device tree bindings, including NXP generic, Renesas RZ/N1, and Technologic variants.

Important APIs/types/functions: `struct sja1000_of_data` supplies optional private size and init hook. Accessors support 8/16/32-bit register spacing plus Technologic indirect 16-bit address/data access. `sp_populate()` handles platform data; `sp_populate_of()` parses OF properties `reg-io-width`, `nxp,external-clock-frequency`, `nxp,tx-output-mode`, `nxp,tx-output-config`, `nxp,clock-out-frequency`, and `nxp,no-comparator-bypass`. `sp_probe()`/`sp_remove()` bind to `module_platform_driver()`.

Control flow: probe requires platform data or OF node, maps resource 0 with devm helpers, obtains IRQ, optionally enables a clock for OF devices, allocates SJA1000 netdev with OF-specific private bytes, derives IRQ flags, sets register base/accessors and timing/output registers, applies match-data init hooks, then registers the SJA1000 device. Remove unregisters and frees the CAN device; devm handles mappings/clocks.

State and persistence: runtime state is in `sja1000_priv` plus optional `technologic_priv` spinlock. Renesas match data sets `SJA1000_QUIRK_NO_CDR_REG` and `SJA1000_QUIRK_RESET_ON_OVERRUN`; the intended reset-on-overrun IRQ oneshot flag is checked before OF init, which is a code-detail risk. No persistent storage.

Dependencies/integration: platform resources, OF matching, optional clocks, SocketCAN SJA1000 core, and the Linux CAN platform data ABI. Device tree properties control register stride and output clock behavior.

Risks: incorrect `reg-io-width` selects wrong register stride. Clock frequency is divided by two; missing/zero clock can invalidate bittiming. IRQ trigger/share flags differ between platform data and OF. Quirk initialization order should be reviewed for reset-on-overrun IRQ threading semantics.

Test signals: OF probe for generic, Renesas, and Technologic compatible strings; verify register reads with 1/2/4-byte spacing; check clock-derived bittiming; validate reset-on-overrun behavior on Renesas hardware; remove path should unregister cleanly.
