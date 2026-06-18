# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v3.5.1.c

Purpose: Defines IPA core register descriptors for IPA v3.5.1 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v3_5_1`. It extends the v3.1-style map with `IPA_TX_CFG`, `FLAVOR_0`, and idle indication descriptors while retaining legacy hash flush, IPA_BCR, counter config, endpoint control/config/NAT/header/mode/aggregation/deaggregation/resource/status, combined endpoint filter/router hash config, IRQ, UC IRQ, and suspend registers.

Control flow and integration: Selected for v3.5.1 platforms and consumed through common register helpers during probe, endpoint setup, resource setup, table hash flush, and interrupt configuration.

State and persistence: Static register metadata only. Values written through the map remain in IPA hardware until changed or reset.

Dependencies: Coupled to `ipa_reg.h` field IDs and endpoint/resource code that expects v3.x offset/stride layout.

Risks: It looks close to v3.1 but has additional TX/flavor/idle registers and fewer resource groups than some later maps. Feature code must test register presence through the versioned table rather than assuming all later fields exist.

Test signals: Probe IPA v3.5.1, read flavor information, configure TX settings, run endpoint traffic, flush hash tables, and exercise IRQ/microcontroller paths.
