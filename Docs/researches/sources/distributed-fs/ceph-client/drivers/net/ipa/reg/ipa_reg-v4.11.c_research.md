# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.11.c

Purpose: Defines IPA core register descriptors for IPA v4.11 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v4_11`. The table includes expanded `COMP_CFG` clock/configuration masks, legacy `FILT_ROUT_HASH_FLUSH`, moved aggregation and IRQ offsets, TX configuration, flavor, idle indication, Qtime timestamp and timer granularity registers, resource groups, endpoint config/status, combined endpoint filter/router hash config, and UC/suspend IRQ descriptors.

Control flow and integration: IPA setup and endpoint code uses this table to program v4.11-specific offsets and fields. Table code still uses pre-v5 combined hash registers and legacy hash flush bits for this version.

State and persistence: Static metadata only; programmed IPA registers persist in hardware.

Dependencies: Relies on shared IPA register IDs and field enums. It integrates with endpoint, resource, interrupt, table, and timing configuration code.

Risks: v4.11 shares many structures with v4.5/v4.9 but has some field-mask differences and a different IRQ base than earlier v4.2-style maps. Treating it as v5 would incorrectly use cache-flush and split cache config registers.

Test signals: Probe v4.11, configure endpoints and resources, verify qtime/timer setup, flush legacy hash tables, handle IPA/UC/suspend IRQs, and run traffic through aggregation/deaggregation paths.
